"""
SLA & Delivery Promise Monitoring service.

Computes delivery-promise compliance from the Olist orders actually present in
the database:

- Monitored order  : status 'delivered' with BOTH an actual customer delivery
  date and an estimated (promised) delivery date. Everything else (canceled,
  shipped, processing, ...) has no comparable promise-vs-actual pair and is
  reported separately as "not monitorable" — never fabricated.
- On-time          : delivered <= promised (margin <= 0 days).
- Delayed          : delivered >  promised (margin >  0 days).
- Delay days       : (delivered - promised) in days, delayed orders only.
- Critical delayed : delay > CRITICAL_DELAY_DAYS (7). A published business rule,
  surfaced in the API response so the dashboard can state it explicitly.

All aggregates run the same WHERE predicates inline (no subquery joins — SQLite
materializes a 24k-row subquery unindexed and the join cost explodes), so every
panel describes the same slice of orders.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, List, Optional, Sequence

from sqlalchemy import case, func
from sqlalchemy.orm import Query, Session

from app.agents._shared import pct, simulated_clock, tz
from app.models.olist import (
    CategoryTranslation,
    Customer,
    Order,
    OrderItem,
    OrderReview,
    Product,
    Seller,
)

CRITICAL_DELAY_DAYS = 7.0

_DELAY_BUCKETS: Sequence[tuple[str, float, float]] = (
    # (label, min_days (exclusive), max_days (inclusive)]
    ("1-3 days", 0.0, 3.0),
    ("3-7 days", 3.0, 7.0),
    ("7-14 days", 7.0, 14.0),
    ("14+ days", 14.0, float("inf")),
)

# Category label: English translation when one exists, else the raw Portuguese
# name, else 'uncategorized' (products with a null category exist in Olist).
_category_label = func.coalesce(
    func.coalesce(CategoryTranslation.product_category_name_english, Product.product_category_name),
    "uncategorized",
)


def _parse_date(v: Optional[str]) -> Optional[date]:
    if not v:
        return None
    try:
        return datetime.strptime(v, "%Y-%m-%d").date()
    except ValueError:
        return None


def case_late(order_model):
    """SQL-boolean: delivered after the promised date (portable across SQLite/Postgres)."""
    return order_model.order_delivered_customer_date > order_model.order_estimated_delivery_date


def sum_late(order_model):
    """COUNT of late orders as an integer SUM. `func.sum()` over a bare boolean
    comes back typed as Boolean (True/1) — the CASE keeps the aggregate integer."""
    return func.sum(case((case_late(order_model), 1), else_=0))


def _date_filters(q: Query, filters: Dict[str, Any]) -> Query:
    start, end = _parse_date(filters.get("start")), _parse_date(filters.get("end"))
    if start:
        q = q.filter(Order.order_purchase_timestamp >= datetime.combine(start, datetime.min.time()))
    if end:
        q = q.filter(Order.order_purchase_timestamp < datetime.combine(end, datetime.max.time()))
    return q


def _base_order_query(db: Session, filters: Dict[str, Any]) -> Query:
    """Delivered orders with promise + actual dates (the monitored scope), with
    order-level filters applied. Item-level filters (seller/category) are NOT
    applied here — callers join OrderItem themselves with `_item_filters`."""
    clock = simulated_clock(db)
    q = (
        db.query(Order)
        .join(Customer, Order.customer_id == Customer.customer_id)
        .filter(
            Order.order_purchase_timestamp <= clock,
            Order.order_status == "delivered",
            Order.order_delivered_customer_date.isnot(None),
            Order.order_estimated_delivery_date.isnot(None),
        )
    )
    q = _date_filters(q, filters)
    if filters.get("state"):
        q = q.filter(Customer.customer_state == filters["state"])
    return q


def _item_filters(q: Query, filters: Dict[str, Any]) -> Query:
    """Apply item-level scope filters. Requires OrderItem already joined; adds
    Product/CategoryTranslation joins only when a category filter is set."""
    if filters.get("seller"):
        q = q.filter(OrderItem.seller_id == filters["seller"])
    if filters.get("category"):
        q = (
            q.join(Product, OrderItem.product_id == Product.product_id)
            .outerjoin(CategoryTranslation, CategoryTranslation.product_category_name == Product.product_category_name)
            .filter(_category_label == filters["category"])
        )
    return q


def monitored_base_query(db: Session, filters: Dict[str, Any]) -> Query:
    """The monitored scope including item-level filters (single OrderItem join
    serves both seller and category — joining twice would cross-product rows)."""
    q = _base_order_query(db, filters)
    if filters.get("seller") or filters.get("category"):
        q = q.join(OrderItem, OrderItem.order_id == Order.order_id)
        q = _item_filters(q, filters)
    return q


def order_values(db: Session, filters: Dict[str, Any]) -> Dict[str, float]:
    """
    order_id -> total order value (sum of item price + freight) for every
    monitored order in the current filter scope. Orders without item rows are
    simply absent and reported as a data-coverage gap, never counted as 0.
    An order passes the seller/category scope when ANY of its items matches —
    same semantics as the monitored-order query.
    """
    q = (
        db.query(OrderItem.order_id, func.sum(OrderItem.price + OrderItem.freight_value))
        .join(Order, Order.order_id == OrderItem.order_id)
        .join(Customer, Order.customer_id == Customer.customer_id)
        .filter(
            Order.order_purchase_timestamp <= simulated_clock(db),
            Order.order_status == "delivered",
            Order.order_delivered_customer_date.isnot(None),
            Order.order_estimated_delivery_date.isnot(None),
        )
    )
    q = _date_filters(q, filters)
    if filters.get("state"):
        q = q.filter(Customer.customer_state == filters["state"])
    q = _item_filters(q, filters)
    rows = q.group_by(OrderItem.order_id).all()
    return {oid: float(v or 0.0) for oid, v in rows}


def _percentile(sorted_vals: List[float], p: float) -> float:
    if not sorted_vals:
        return 0.0
    idx = min(int(len(sorted_vals) * p), len(sorted_vals) - 1)
    return round(sorted_vals[idx], 2)


def _monthly_key(dt: datetime) -> str:
    return f"{dt.year:04d}-{dt.month:02d}"


def _state_breakdown(monitored_rows: List[Dict[str, Any]], limit: int = 15) -> List[Dict[str, Any]]:
    agg: Dict[str, Dict[str, Any]] = {}
    for r in monitored_rows:
        a = agg.setdefault(r["state"], {"state": r["state"], "orders": 0, "delayed": 0, "margins": []})
        a["orders"] += 1
        if r["margin_days"] > 0:
            a["delayed"] += 1
            a["margins"].append(r["margin_days"])
    items = []
    for a in agg.values():
        items.append(
            {
                "state": a["state"],
                "orders": a["orders"],
                "delayed": a["delayed"],
                "delay_rate_pct": pct(a["delayed"], a["orders"]),
                "avg_delay_days": round(sum(a["margins"]) / len(a["margins"]), 2) if a["margins"] else 0.0,
            }
        )
    items.sort(key=lambda i: (-i["delayed"], -i["orders"]))
    return items[:limit]


def _seller_breakdown(db: Session, filters: Dict[str, Any], limit: int = 15) -> List[Dict[str, Any]]:
    """Per-seller delay stats. An order fulfilled by two sellers contributes to
    both sellers' counts (its delay is a fact about each of those shipments)."""
    clock = simulated_clock(db)
    q = (
        db.query(
            OrderItem.seller_id,
            func.count(func.distinct(OrderItem.order_id)),
            sum_late(Order),
            func.min(Seller.seller_state),
        )
        .join(Order, Order.order_id == OrderItem.order_id)
        .join(Customer, Order.customer_id == Customer.customer_id)
        .outerjoin(Seller, Seller.seller_id == OrderItem.seller_id)
        .filter(
            Order.order_purchase_timestamp <= clock,
            Order.order_status == "delivered",
            Order.order_delivered_customer_date.isnot(None),
            Order.order_estimated_delivery_date.isnot(None),
        )
    )
    q = _date_filters(q, filters)
    if filters.get("state"):
        q = q.filter(Customer.customer_state == filters["state"])
    if filters.get("seller"):
        q = q.filter(OrderItem.seller_id == filters["seller"])
    if filters.get("category"):
        q = (
            q.join(Product, OrderItem.product_id == Product.product_id)
            .outerjoin(CategoryTranslation, CategoryTranslation.product_category_name == Product.product_category_name)
            .filter(_category_label == filters["category"])
        )
    rows = q.group_by(OrderItem.seller_id).all()

    items = [
        {"seller_id": s, "seller_state": st or "—", "orders": int(n), "delayed": int(late or 0)}
        for s, n, late, st in rows
    ]
    items = [i for i in items if i["orders"] >= 10]
    items.sort(key=lambda i: (-i["delayed"], -i["orders"]))
    top = items[:limit]
    if top:
        top_ids = [i["seller_id"] for i in top]
        margins = _delay_margins_by_seller(db, filters, top_ids)
        for i in top:
            m = margins.get(i["seller_id"], [])
            i["delay_rate_pct"] = pct(i["delayed"], i["orders"])
            i["avg_delay_days"] = round(sum(m) / len(m), 2) if m else 0.0
    return top


def _delay_margins_by_seller(db: Session, filters: Dict[str, Any], seller_ids: List[str]) -> Dict[str, List[float]]:
    clock = simulated_clock(db)
    q = (
        db.query(OrderItem.seller_id, Order.order_delivered_customer_date, Order.order_estimated_delivery_date)
        .join(Order, Order.order_id == OrderItem.order_id)
        .join(Customer, Order.customer_id == Customer.customer_id)
        .filter(
            OrderItem.seller_id.in_(seller_ids),
            Order.order_purchase_timestamp <= clock,
            Order.order_status == "delivered",
            Order.order_delivered_customer_date.isnot(None),
            Order.order_estimated_delivery_date.isnot(None),
            Order.order_delivered_customer_date > Order.order_estimated_delivery_date,
        )
    )
    q = _date_filters(q, filters)
    if filters.get("state"):
        q = q.filter(Customer.customer_state == filters["state"])
    if filters.get("category"):
        q = (
            q.join(Product, OrderItem.product_id == Product.product_id)
            .outerjoin(CategoryTranslation, CategoryTranslation.product_category_name == Product.product_category_name)
            .filter(_category_label == filters["category"])
        )
    out: Dict[str, List[float]] = {}
    for seller_id, delivered, estimated in q.all():
        if delivered and estimated:
            out.setdefault(seller_id, []).append((tz(delivered) - tz(estimated)).total_seconds() / 86400.0)
    return out


def _category_breakdown(db: Session, filters: Dict[str, Any], limit: int = 15) -> List[Dict[str, Any]]:
    clock = simulated_clock(db)
    q = (
        db.query(
            _category_label,
            func.count(func.distinct(OrderItem.order_id)),
            sum_late(Order),
        )
        .join(Order, Order.order_id == OrderItem.order_id)
        .join(Product, Product.product_id == OrderItem.product_id)
        .outerjoin(CategoryTranslation, CategoryTranslation.product_category_name == Product.product_category_name)
        .join(Customer, Order.customer_id == Customer.customer_id)
        .filter(
            Order.order_purchase_timestamp <= clock,
            Order.order_status == "delivered",
            Order.order_delivered_customer_date.isnot(None),
            Order.order_estimated_delivery_date.isnot(None),
        )
    )
    q = _date_filters(q, filters)
    if filters.get("state"):
        q = q.filter(Customer.customer_state == filters["state"])
    if filters.get("seller"):
        q = q.filter(OrderItem.seller_id == filters["seller"])
    if filters.get("category"):
        q = q.filter(_category_label == filters["category"])
    rows = q.group_by(_category_label).all()
    items = [
        {"category": c, "orders": int(n), "delayed": int(late or 0), "delay_rate_pct": pct(int(late or 0), int(n))}
        for c, n, late in rows
    ]
    items.sort(key=lambda i: (-i["delayed"], -i["orders"]))
    return items[:limit]


def _support_response(db: Session, filters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Review-answer latency (review_creation_date -> review_answer_timestamp) as
    the closest support-response signal the Olist dataset offers. There is no
    contractual SLA threshold in the data, so this reports the observed
    distribution — with that stated explicitly — rather than a pass/fail rate
    against an invented deadline.
    """
    clock = simulated_clock(db)

    def _scoped_reviews(*cols):
        q = (
            db.query(*cols)
            .join(Order, Order.order_id == OrderReview.order_id)
            .join(Customer, Order.customer_id == Customer.customer_id)
            .filter(
                Order.order_purchase_timestamp <= clock,
                Order.order_status == "delivered",
                Order.order_delivered_customer_date.isnot(None),
                Order.order_estimated_delivery_date.isnot(None),
            )
        )
        q = _date_filters(q, filters)
        if filters.get("state"):
            q = q.filter(Customer.customer_state == filters["state"])
        if filters.get("seller") or filters.get("category"):
            q = q.join(OrderItem, OrderItem.order_id == Order.order_id)
            if filters.get("seller"):
                q = q.filter(OrderItem.seller_id == filters["seller"])
            if filters.get("category"):
                q = (
                    q.join(Product, OrderItem.product_id == Product.product_id)
                    .outerjoin(CategoryTranslation, CategoryTranslation.product_category_name == Product.product_category_name)
                    .filter(_category_label == filters["category"])
                )
        return q

    total_reviews = _scoped_reviews(func.count(OrderReview.review_id)).scalar() or 0
    rows = _scoped_reviews(OrderReview.review_creation_date, OrderReview.review_answer_timestamp).filter(
        OrderReview.review_answer_timestamp.isnot(None)
    ).all()
    if not rows:
        return {
            "status": "UNAVAILABLE",
            "reason": "No answered reviews in the current scope.",
            "reviews_in_scope": int(total_reviews),
        }
    latencies = sorted(
        (tz(a) - tz(c)).total_seconds() / 3600.0 for c, a in rows if a and c and a > c
    )
    if not latencies:
        return {
            "status": "UNAVAILABLE",
            "reason": "Review answer timestamps precede creation timestamps — no usable response times.",
            "reviews_in_scope": int(total_reviews),
        }
    answered = len(latencies)
    return {
        "status": "OK",
        "reviews_in_scope": int(total_reviews),
        "answered_reviews": answered,
        "avg_response_hours": round(sum(latencies) / answered, 1),
        "median_response_hours": _percentile(latencies, 0.5),
        "p90_response_hours": _percentile(latencies, 0.9),
        "pct_over_48h": pct(sum(1 for h in latencies if h > 48), answered),
        "pct_over_72h": pct(sum(1 for h in latencies if h > 72), answered),
        "note": "No contractual support-SLA deadline exists in the Olist dataset; these are observed response-time statistics.",
    }


def _unmonitored_by_status(db: Session, filters: Dict[str, Any]) -> Dict[str, int]:
    """Status counts for all in-scope orders (monitorable + not), honoring the
    same item-level scope filters so `total_orders_in_scope` always matches
    what the monitored panels describe."""
    clock = simulated_clock(db)
    q = (
        db.query(Order.order_status, func.count(func.distinct(Order.order_id)))
        .filter(Order.order_purchase_timestamp <= clock)
    )
    q = _date_filters(q, filters)
    if filters.get("state"):
        q = q.join(Customer, Order.customer_id == Customer.customer_id).filter(Customer.customer_state == filters["state"])
    if filters.get("seller") or filters.get("category"):
        q = q.join(OrderItem, OrderItem.order_id == Order.order_id)
        if filters.get("seller"):
            q = q.filter(OrderItem.seller_id == filters["seller"])
        if filters.get("category"):
            q = (
                q.join(Product, OrderItem.product_id == Product.product_id)
                .outerjoin(CategoryTranslation, CategoryTranslation.product_category_name == Product.product_category_name)
                .filter(_category_label == filters["category"])
            )
    q = q.group_by(Order.order_status)
    counts = {status: int(n) for status, n in q.all()}
    monitored = counts.pop("delivered", 0)
    return {"delivered": monitored, **counts}


def _filter_options(db: Session) -> Dict[str, Any]:
    states = [s for (s,) in db.query(Customer.customer_state).distinct().order_by(Customer.customer_state).all()]
    categories = [
        c
        for (c,) in db.query(_category_label)
        .select_from(Product)
        .outerjoin(CategoryTranslation, CategoryTranslation.product_category_name == Product.product_category_name)
        .distinct()
        .order_by(_category_label)
        .all()
    ]
    top_sellers = [
        {"seller_id": s, "orders": int(n)}
        for s, n in db.query(OrderItem.seller_id, func.count(func.distinct(OrderItem.order_id)))
        .group_by(OrderItem.seller_id)
        .order_by(func.count(func.distinct(OrderItem.order_id)).desc())
        .limit(50)
        .all()
    ]
    bounds = db.query(func.min(Order.order_purchase_timestamp), func.max(Order.order_purchase_timestamp)).first()
    return {
        "states": states,
        "categories": categories,
        "sellers": top_sellers,
        "purchase_date_range": [bounds[0].isoformat()[:10] if bounds[0] else None, bounds[1].isoformat()[:10] if bounds[1] else None],
    }


def get_sla_overview(
    db: Session,
    *,
    start: Optional[str] = None,
    end: Optional[str] = None,
    state: Optional[str] = None,
    seller: Optional[str] = None,
    category: Optional[str] = None,
    critical_limit: int = 15,
) -> Dict[str, Any]:
    filters = {"start": start, "end": end, "state": state, "seller": seller, "category": category}

    # Column projection (tuples), NOT ORM entities: entity loading + lazy
    # `o.customer` access ran a SELECT per order (~24k) and cost minutes.
    # monitored_base_query (not _base_order_query) so seller/category filters apply.
    rows = (
        monitored_base_query(db, filters)
        .with_entities(
            Order.order_id,
            Order.order_purchase_timestamp,
            Order.order_estimated_delivery_date,
            Order.order_delivered_customer_date,
            Customer.customer_state,
        )
        # An item-level scope filter (seller/category) multiplies an order by
        # its matching item rows — DISTINCT collapses back to one per order.
        .distinct()
        .all()
    )
    status_counts = _unmonitored_by_status(db, filters)
    total_in_scope = sum(status_counts.values())
    monitored_rows: List[Dict[str, Any]] = []
    for oid, purchase, promised, delivered, state_ in rows:
        if not purchase or not promised or not delivered:
            continue
        margin = (tz(delivered) - tz(promised)).total_seconds() / 86400.0
        monitored_rows.append(
            {
                "order_id": oid,
                "purchase": purchase,
                "promised": promised,
                "delivered": delivered,
                "state": state_ or "—",
                "margin_days": margin,
            }
        )

    monitored = len(monitored_rows)
    if monitored == 0:
        return {
            "status": "NO_DATA",
            "reason": "No delivered orders with promise dates match the current filters.",
            "filters": filters,
            "filter_options": _filter_options(db),
        }

    delayed = [r for r in monitored_rows if r["margin_days"] > 0]
    on_time = monitored - len(delayed)
    delays = sorted(r["margin_days"] for r in delayed)
    critical = [r for r in delayed if r["margin_days"] > CRITICAL_DELAY_DAYS]

    buckets = []
    for label, lo, hi in _DELAY_BUCKETS:
        buckets.append({"label": label, "count": sum(1 for d in delays if lo < d <= hi)})
    buckets.insert(0, {"label": "on time / early", "count": on_time})

    monthly: Dict[str, Dict[str, Any]] = {}
    for r in monitored_rows:
        key = _monthly_key(r["purchase"])
        m = monthly.setdefault(key, {"month": key, "monitored": 0, "delayed": 0, "delay_days": []})
        m["monitored"] += 1
        if r["margin_days"] > 0:
            m["delayed"] += 1
            m["delay_days"].append(r["margin_days"])
    trend = [
        {
            "month": m["month"],
            "monitored": m["monitored"],
            "delayed": m["delayed"],
            "delay_rate_pct": pct(m["delayed"], m["monitored"]),
            "avg_delay_days": round(sum(m["delay_days"]) / len(m["delay_days"]), 2) if m["delay_days"] else 0.0,
        }
        for m in sorted(monthly.values(), key=lambda m: m["month"])
    ]

    values = order_values(db, filters)
    critical_rows = sorted(critical, key=lambda r: -r["margin_days"])[:critical_limit]
    critical_orders = [
        {
            "order_id": r["order_id"],
            "purchase_date": r["purchase"].isoformat()[:10],
            "promised_date": r["promised"].isoformat()[:10],
            "delivered_date": r["delivered"].isoformat()[:10],
            "delay_days": round(r["margin_days"], 1),
            "customer_state": r["state"],
            "order_value": round(values.get(r["order_id"], 0.0), 2),
            "value_known": r["order_id"] in values,
        }
        for r in critical_rows
    ]

    canceled = status_counts.get("canceled", 0)

    return {
        "status": "OK",
        "filters": filters,
        "data_source": "Olist Brazilian E-commerce dataset (orders, order_items, order_reviews)",
        "definitions": {
            "monitored": "Delivered orders with both an actual and a promised delivery date.",
            "on_time": "Delivered on or before the promised date.",
            "delayed": "Delivered after the promised date.",
            "critical": f"Delayed by more than {CRITICAL_DELAY_DAYS:.0f} days (business rule).",
        },
        "overview": {
            "total_orders_in_scope": total_in_scope,
            "monitored_orders": monitored,
            "on_time_orders": on_time,
            "delayed_orders": len(delayed),
            "sla_compliance_pct": pct(on_time, monitored),
            "delay_rate_pct": pct(len(delayed), monitored),
            "avg_delay_days": round(sum(delays) / len(delays), 2) if delays else 0.0,
            "median_delay_days": _percentile(delays, 0.5),
            "p90_delay_days": _percentile(delays, 0.9),
            "max_delay_days": round(delays[-1], 1) if delays else 0.0,
            "critical_delayed_orders": len(critical),
            "critical_threshold_days": CRITICAL_DELAY_DAYS,
            "unmonitored_by_status": status_counts,
            "orders_without_item_value": monitored - len(values),
        },
        "delay_buckets": buckets,
        "monthly_trend": trend,
        "by_state": _state_breakdown(monitored_rows),
        "by_seller": _seller_breakdown(db, filters),
        "by_category": _category_breakdown(db, filters),
        "critical_orders": {"total_critical": len(critical), "items": critical_orders},
        "support_response": _support_response(db, filters),
        "cancellations": {
            "canceled_orders_in_scope": canceled,
            "refund_data": "UNAVAILABLE",
            "note": "The Olist dataset records cancellations but no refund amounts, so refund value vs deadline cannot be computed.",
        },
        "filter_options": _filter_options(db),
    }

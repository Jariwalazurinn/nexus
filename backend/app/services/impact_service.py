"""
Business Impact Estimation service.

Quantifies the order value tied up in delivery-promise breaches using actual
Olist dataset values (item price + freight). Everything here is an ESTIMATE of
value AFFECTED / EXPOSED — the dataset carries no refund, penalty, or margin
data, so no figure in this module may be reported as confirmed lost revenue.

Relationships (verified against app.models.olist):
  orders 1—N order_items (price, freight_value, seller_id, product_id)
  orders N—1 customers (customer_id, customer_state)
  order_items N—1 products → product_category_name (→ English translation)

An order counts as delayed when order_delivered_customer_date >
order_estimated_delivery_date (same definition as the SLA dashboard). Order
value = Σ(price + freight) over its items; orders missing item rows are
excluded from value aggregates and reported as a coverage gap — never counted
as zero-value.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.agents._shared import pct, simulated_clock, tz
from app.models.olist import CategoryTranslation, Customer, Order, OrderItem, Product, Seller
from app.services.sla_service import (
    _category_label,
    _date_filters,
    _filter_options,
    _item_filters,
    _percentile,
    monitored_base_query,
    order_values,
)


def _affected_items(db: Session, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Item-level rows for DELAYED monitored orders: one row per item with its
    seller and category, for per-seller / per-category attribution. An order
    fulfilled by two sellers contributes each item to its own seller — that is
    where the value physically sits; order-level counts elsewhere stay
    deduplicated by order_id."""
    clock = simulated_clock(db)
    q = (
        db.query(
            OrderItem.order_id,
            OrderItem.seller_id,
            OrderItem.price,
            OrderItem.freight_value,
            # Plain column, NOT an aggregate: any aggregate in the SELECT with
            # no GROUP BY collapses the whole query to a single row in SQLite.
            Seller.seller_state,
            _category_label,
        )
        .join(Order, Order.order_id == OrderItem.order_id)
        .join(Customer, Order.customer_id == Customer.customer_id)
        .outerjoin(Seller, Seller.seller_id == OrderItem.seller_id)
        .join(Product, Product.product_id == OrderItem.product_id)
        .outerjoin(CategoryTranslation, CategoryTranslation.product_category_name == Product.product_category_name)
        .filter(
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
    # Item-level scope filters applied inline — Product/CategoryTranslation are
    # already joined above, so _item_filters would join them a second time and
    # SQLite would fail with an ambiguous-column error.
    if filters.get("seller"):
        q = q.filter(OrderItem.seller_id == filters["seller"])
    if filters.get("category"):
        q = q.filter(_category_label == filters["category"])
    items = []
    for oid, seller_id, price, freight, seller_state, category in q.all():
        items.append(
            {
                "order_id": oid,
                "seller_id": seller_id,
                "seller_state": seller_state or "—",
                "item_value": float(price or 0.0) + float(freight or 0.0),
                "category": category,
            }
        )
    return items


def _group_impact(
    groups: Dict[str, Dict[str, Any]], key_field: str, limit: int
) -> List[Dict[str, Any]]:
    out = []
    for g in groups.values():
        out.append(
            {
                key_field: g[key_field],
                "delayed_orders": g["orders"],
                "affected_value": round(g["value"], 2),
                "avg_delay_days": round(sum(g["delays"]) / len(g["delays"]), 2) if g["delays"] else 0.0,
            }
        )
    out.sort(key=lambda i: -i["affected_value"])
    return out[:limit]


def get_business_impact(
    db: Session,
    *,
    start: Optional[str] = None,
    end: Optional[str] = None,
    state: Optional[str] = None,
    seller: Optional[str] = None,
    category: Optional[str] = None,
    top_limit: int = 15,
) -> Dict[str, Any]:
    filters = {"start": start, "end": end, "state": state, "seller": seller, "category": category}

    # Same scope + classification query as the SLA dashboard (see sla_service
    # for the tuple-projection / DISTINCT rationale).
    rows = (
        monitored_base_query(db, filters)
        .with_entities(
            Order.order_id,
            Order.order_purchase_timestamp,
            Order.order_estimated_delivery_date,
            Order.order_delivered_customer_date,
            Customer.customer_id,
            Customer.customer_state,
        )
        .distinct()
        .all()
    )
    monitored = len(rows)
    if monitored == 0:
        return {
            "status": "NO_DATA",
            "reason": "No delivered orders with promise dates match the current filters.",
            "filters": filters,
        }

    delayed_orders: Dict[str, Dict[str, Any]] = {}
    ontime_orders: Dict[str, Dict[str, Any]] = {}
    for oid, purchase, promised, delivered, cust_id, state_ in rows:
        if not purchase or not promised or not delivered:
            continue
        margin = (tz(delivered) - tz(promised)).total_seconds() / 86400.0
        bucket = delayed_orders if margin > 0 else ontime_orders
        bucket[oid] = {
            "purchase": purchase,
            "customer_id": cust_id,
            "state": state_ or "—",
            "margin_days": margin,
        }

    values = order_values(db, filters)  # order_id -> Σ(price + freight)

    delayed_ids = set(delayed_orders)
    ontime_ids = set(ontime_orders)
    delayed_with_value = delayed_ids & values.keys()
    affected_value = sum(values[oid] for oid in delayed_with_value)
    affected_customers = {d["customer_id"] for d in delayed_orders.values() if d["customer_id"]}
    delays = sorted(d["margin_days"] for d in delayed_orders.values())

    ontime_value = sum(values[oid] for oid in ontime_ids & values.keys())
    ontime_with_value = len(ontime_ids & values.keys())

    # ── Item-level attribution (delayed orders only) ────────────────
    items = _affected_items(db, filters)
    by_seller: Dict[str, Dict[str, Any]] = {}
    by_category: Dict[str, Dict[str, Any]] = {}
    item_orders_by_seller: Dict[str, set] = {}
    item_orders_by_cat: Dict[str, set] = {}
    for it in items:
        s = by_seller.setdefault(
            it["seller_id"], {"seller_id": it["seller_id"], "state": it["seller_state"], "orders": 0, "value": 0.0, "delays": []}
        )
        s["value"] += it["item_value"]
        item_orders_by_seller.setdefault(it["seller_id"], set()).add(it["order_id"])
        c = by_category.setdefault(it["category"], {"category": it["category"], "orders": 0, "value": 0.0, "delays": []})
        c["value"] += it["item_value"]
        item_orders_by_cat.setdefault(it["category"], set()).add(it["order_id"])
    # order counts per group are DISTINCT orders (items don't inflate counts)
    for seller_id, oids in item_orders_by_seller.items():
        by_seller[seller_id]["orders"] = len(oids)
        by_seller[seller_id]["delays"] = [delayed_orders[o]["margin_days"] for o in oids if o in delayed_orders]
    for cat, oids in item_orders_by_cat.items():
        by_category[cat]["orders"] = len(oids)
        by_category[cat]["delays"] = [delayed_orders[o]["margin_days"] for o in oids if o in delayed_orders]

    # ── Location + time attribution (order-level, deduped) ──────────
    by_state: Dict[str, Dict[str, Any]] = {}
    by_month: Dict[str, Dict[str, Any]] = {}
    for oid, d in delayed_orders.items():
        st = by_state.setdefault(d["state"], {"state": d["state"], "orders": 0, "value": 0.0, "delays": []})
        st["orders"] += 1
        st["delays"].append(d["margin_days"])
        if oid in values:
            st["value"] += values[oid]
        month = f"{d['purchase'].year:04d}-{d['purchase'].month:02d}"
        m = by_month.setdefault(month, {"month": month, "orders": 0, "value": 0.0, "delays": []})
        m["orders"] += 1
        m["delays"].append(d["margin_days"])
        if oid in values:
            m["value"] += values[oid]

    # ── High-impact orders: worst value-at-risk among delayed ───────
    top_rows = sorted(
        ((oid, values[oid], delayed_orders[oid]) for oid in delayed_with_value),
        key=lambda t: -t[1],
    )[:top_limit]
    top_orders = [
        {
            "order_id": oid,
            "order_value": round(v, 2),
            "delay_days": round(d["margin_days"], 1),
            "purchase_date": d["purchase"].isoformat()[:10],
            "customer_state": d["state"],
        }
        for oid, v, d in top_rows
    ]

    total_monitored_value = affected_value + ontime_value

    return {
        "status": "OK",
        "filters": filters,
        "data_source": "Olist Brazilian E-commerce dataset (orders, order_items, order_payments)",
        "definitions": {
            "affected_order_value": "Sum of item price + freight over delayed orders — order value AFFECTED by a late delivery, not money lost.",
            "revenue_exposure": "Same figure viewed as exposure: value that was at risk while the order was late. Estimated, not confirmed.",
            "lost_revenue": "NOT CALCULABLE from this dataset — no refund, penalty, or margin data exists. Never reported here.",
            "aov": "Average order value = total order value / number of orders (orders with item rows only).",
        },
        "summary": {
            "monitored_orders": monitored,
            "delayed_orders": len(delayed_orders),
            "on_time_orders": len(ontime_orders),
            "delay_rate_pct": pct(len(delayed_orders), monitored),
            "affected_customers": len(affected_customers),
            "affected_order_value": round(affected_value, 2),
            "avg_delay_days": round(sum(delays) / len(delays), 2) if delays else 0.0,
            "p90_delay_days": _percentile(delays, 0.9),
            "estimated_revenue_exposure": round(affected_value, 2),
            "actual_lost_revenue": "UNAVAILABLE",
            "value_coverage": {
                "delayed_orders_with_value": len(delayed_with_value),
                "delayed_orders_without_value": len(delayed_ids) - len(delayed_with_value),
                "note": "Delayed orders lacking order-item rows are excluded from value figures (counted here), never valued at zero.",
            },
        },
        "aov_comparison": {
            "delayed_aov": round(affected_value / len(delayed_with_value), 2) if delayed_with_value else 0.0,
            "ontime_aov": round(ontime_value / ontime_with_value, 2) if ontime_with_value else 0.0,
            "delayed_orders_with_value": len(delayed_with_value),
            "ontime_orders_with_value": ontime_with_value,
            "monitored_order_value": round(total_monitored_value, 2),
        },
        "impact_by_seller": _group_impact(by_seller, "seller_id", top_limit),
        "impact_by_category": _group_impact(by_category, "category", top_limit),
        "impact_by_state": _group_impact(by_state, "state", top_limit),
        "impact_by_month": _group_impact(by_month, "month", 48),
        "top_impacted_orders": top_orders,
        "filter_options": _filter_options(db),
    }

"""
One-off top-up for order_items / order_payments coverage.

The original seed capped its CSV reads (`nrows=...`), so orders near the end of
the Olist order file were inserted while their item/payment rows (which live in
separate, differently-ordered CSVs) were never read. The fix in
`seed_nexus_data.py` reads the full files now; this script completes any
database seeded by the OLD code without re-importing orders:

- only rows whose order_id already exists in the database are inserted;
- (order_id, order_item_id) / (order_id, payment_sequential) dedup makes it
  safe to re-run any number of times;
- the monitored order scope (the 25k orders already in the DB) is unchanged.

Run:  cd backend && python -m scripts.topup_financials
"""
import logging
import os
import sys

import pandas as pd

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.database.session import SessionLocal, init_db  # noqa: E402
from app.models.olist import Order, OrderItem, OrderPayment, Product, Seller  # noqa: E402
from scripts.seed_nexus_data import find_dataset  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("topup_financials")


def topup_items(db) -> int:
    path = find_dataset("olist_order_items_dataset.csv")
    df = pd.read_csv(path)
    df["shipping_limit_date"] = pd.to_datetime(df["shipping_limit_date"], errors="coerce")

    valid_orders = {r[0] for r in db.query(Order.order_id).all()}
    existing = {(r[0], r[1]) for r in db.query(OrderItem.order_id, OrderItem.order_item_id).all()}
    known_products = {r[0] for r in db.query(Product.product_id).all()}
    known_sellers = {r[0] for r in db.query(Seller.seller_id).all()}

    records = []
    for _, row in df.iterrows():
        oid = str(row["order_id"])
        seq = int(row["order_item_id"])
        if oid not in valid_orders or (oid, seq) in existing:
            continue
        existing.add((oid, seq))
        records.append({
            "order_id": oid,
            "order_item_id": seq,
            "product_id": str(row["product_id"]),
            "seller_id": str(row["seller_id"]),
            "shipping_limit_date": row["shipping_limit_date"].to_pydatetime() if pd.notna(row["shipping_limit_date"]) else None,
            "price": float(row["price"]) if pd.notna(row.get("price")) else 0.0,
            "freight_value": float(row["freight_value"]) if pd.notna(row.get("freight_value")) else 0.0,
        })

    if not records:
        logger.info("Order items already complete — nothing to insert.")
        return 0

    missing_products = {r["product_id"] for r in records} - known_products
    missing_sellers = {r["seller_id"] for r in records} - known_sellers
    if missing_products:
        db.bulk_insert_mappings(Product, [{"product_id": p, "product_category_name": "general"} for p in missing_products])
    if missing_sellers:
        db.bulk_insert_mappings(Seller, [
            {"seller_id": s, "seller_zip_code_prefix": 0, "seller_city": "unknown", "seller_state": "NA"}
            for s in missing_sellers
        ])
    db.commit()
    db.bulk_insert_mappings(OrderItem, records)
    db.commit()
    logger.info(f"Inserted {len(records):,} order item rows (+{len(missing_products)} products, +{len(missing_sellers)} sellers).")
    return len(records)


def topup_payments(db) -> int:
    path = find_dataset("olist_order_payments_dataset.csv")
    df = pd.read_csv(path)

    valid_orders = {r[0] for r in db.query(Order.order_id).all()}
    existing = {(r[0], r[1]) for r in db.query(OrderPayment.order_id, OrderPayment.payment_sequential).all()}

    records = []
    for _, row in df.iterrows():
        oid = str(row["order_id"])
        seq = int(row["payment_sequential"])
        if oid not in valid_orders or (oid, seq) in existing:
            continue
        existing.add((oid, seq))
        records.append({
            "order_id": oid,
            "payment_sequential": seq,
            "payment_type": str(row.get("payment_type") or "credit_card"),
            "payment_installments": int(row["payment_installments"]) if pd.notna(row.get("payment_installments")) else 1,
            "payment_value": float(row["payment_value"]) if pd.notna(row.get("payment_value")) else 0.0,
        })

    if not records:
        logger.info("Order payments already complete — nothing to insert.")
        return 0

    db.bulk_insert_mappings(OrderPayment, records)
    db.commit()
    logger.info(f"Inserted {len(records):,} order payment rows.")
    return len(records)


def main():
    init_db()
    db = SessionLocal()
    try:
        before_orders = db.query(Order).count()
        before_item_orders = db.query(OrderItem.order_id).distinct().count()
        before_pay_orders = db.query(OrderPayment.order_id).distinct().count()
        logger.info(f"Coverage before: {before_orders:,} orders | {before_item_orders:,} with items | {before_pay_orders:,} with payments")

        topup_items(db)
        topup_payments(db)

        after_item_orders = db.query(OrderItem.order_id).distinct().count()
        after_pay_orders = db.query(OrderPayment.order_id).distinct().count()
        logger.info(f"Coverage after:  {before_orders:,} orders | {after_item_orders:,} with items | {after_pay_orders:,} with payments")
    finally:
        db.close()


if __name__ == "__main__":
    main()

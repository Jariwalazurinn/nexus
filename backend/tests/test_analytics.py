"""SLA Monitoring + Business Impact analytics endpoints (app.api.v1.analytics).

Runs against the seeded orders.db fixture — assertions verify internal
consistency of the aggregates (totals add up, rates in range, dedup) rather
than pinned dataset numbers, so the tests stay valid as the seed grows.
"""
from __future__ import annotations


def test_sla_overview_shape_and_consistency(auth_client):
    r = auth_client.get("/api/v1/analytics/sla")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "OK"
    o = body["overview"]
    # headline identities
    assert o["monitored_orders"] == o["on_time_orders"] + o["delayed_orders"]
    assert 0 <= o["sla_compliance_pct"] <= 100
    assert 0 <= o["delay_rate_pct"] <= 100
    assert o["sla_compliance_pct"] + o["delay_rate_pct"] == 100
    # delays: avg between median and max
    assert 0 <= o["median_delay_days"] <= o["avg_delay_days"] <= o["max_delay_days"]
    # buckets partition the monitored set
    assert sum(b["count"] for b in body["delay_buckets"]) == o["monitored_orders"]
    # no fabricated support SLA
    sr = body["support_response"]
    if sr["status"] == "OK":
        assert "No contractual support-SLA" in sr["note"]
    # refunds explicitly unavailable
    assert body["cancellations"]["refund_data"] == "UNAVAILABLE"


def test_sla_filters_narrow_scope(auth_client):
    base = auth_client.get("/api/v1/analytics/sla").json()
    dated = auth_client.get("/api/v1/analytics/sla", params={"start": "2018-01-01", "end": "2018-06-30"}).json()
    assert dated["status"] == "OK"
    assert dated["overview"]["monitored_orders"] <= base["overview"]["monitored_orders"]
    # a filter for a month before the dataset starts yields NO_DATA, not zeros
    empty = auth_client.get("/api/v1/analytics/sla", params={"start": "2099-01-01", "end": "2099-12-31"}).json()
    assert empty["status"] == "NO_DATA"


def test_sla_seller_filter_dedupes_orders(auth_client):
    body = auth_client.get("/api/v1/analytics/sla").json()
    sellers = body.get("by_seller") or body.get("filter_options", {}).get("sellers") or []
    if not sellers:
        return  # nothing to scope on
    seller_id = sellers[0]["seller_id"] if "seller_id" in sellers[0] else sellers[0].get("seller_id")
    scoped = auth_client.get("/api/v1/analytics/sla", params={"seller": seller_id}).json()
    assert scoped["status"] == "OK"
    # monitored count must be distinct orders — never item-row duplicates
    assert scoped["overview"]["monitored_orders"] <= scoped["overview"]["total_orders_in_scope"]


def test_impact_matches_sla_counts_and_money_identities(auth_client):
    sla = auth_client.get("/api/v1/analytics/sla").json()
    r = auth_client.get("/api/v1/analytics/impact")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "OK"
    # both dashboards describe the same monitored slice
    assert body["summary"]["monitored_orders"] == sla["overview"]["monitored_orders"]
    assert body["summary"]["delayed_orders"] == sla["overview"]["delayed_orders"]
    s = body["summary"]
    assert s["affected_customers"] <= s["delayed_orders"]  # deduped customers
    assert s["estimated_revenue_exposure"] == s["affected_order_value"]
    # AOV identity: affected value / valued delayed orders
    vc = s["value_coverage"]
    aov = body["aov_comparison"]
    if vc["delayed_orders_with_value"] > 0:
        assert aov["delayed_aov"] == round(s["affected_order_value"] / vc["delayed_orders_with_value"], 2)
    # exposure is explicitly labeled an estimate; loss is explicitly unavailable
    assert s["actual_lost_revenue"] == "UNAVAILABLE"


def test_impact_filter_consistency(auth_client):
    r = auth_client.get("/api/v1/analytics/impact", params={"category": "health_beauty"})
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "OK"
    assert body["summary"]["delayed_orders"] <= body["summary"]["monitored_orders"]

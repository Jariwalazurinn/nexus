import { useMemo } from "react";
import { API_ENDPOINTS } from "../config";
import { filtersToQuery, formatBRL, formatNum, shortId, useAnalyticsData, useFilterState, type FilterOptions } from "./analyticsShared";
import { BarRow, EmptyState, ErrorState, FilterBar, KpiCard, LoadingState, Section } from "./analyticsComponents";
import "./AnalyticsDashboards.css";

type SlaResponse = {
  status: "OK" | "NO_DATA";
  reason?: string;
  filters: Record<string, string | null>;
  data_source: string;
  definitions: Record<string, string>;
  overview: {
    total_orders_in_scope: number;
    monitored_orders: number;
    on_time_orders: number;
    delayed_orders: number;
    sla_compliance_pct: number;
    delay_rate_pct: number;
    avg_delay_days: number;
    median_delay_days: number;
    p90_delay_days: number;
    max_delay_days: number;
    critical_delayed_orders: number;
    critical_threshold_days: number;
    unmonitored_by_status: Record<string, number>;
    orders_without_item_value: number;
  };
  delay_buckets: { label: string; count: number }[];
  monthly_trend: { month: string; monitored: number; delayed: number; delay_rate_pct: number; avg_delay_days: number }[];
  by_state: { state: string; orders: number; delayed: number; delay_rate_pct: number; avg_delay_days: number }[];
  by_seller: { seller_id: string; seller_state: string; orders: number; delayed: number; delay_rate_pct: number; avg_delay_days: number }[];
  by_category: { category: string; orders: number; delayed: number; delay_rate_pct: number }[];
  critical_orders: {
    total_critical: number;
    items: {
      order_id: string;
      purchase_date: string;
      promised_date: string;
      delivered_date: string;
      delay_days: number;
      customer_state: string;
      order_value: number;
      value_known: boolean;
    }[];
  };
  support_response:
    | {
        status: "OK";
        reviews_in_scope: number;
        answered_reviews: number;
        avg_response_hours: number;
        median_response_hours: number;
        p90_response_hours: number;
        pct_over_48h: number;
        pct_over_72h: number;
        note: string;
      }
    | { status: "UNAVAILABLE"; reason: string; reviews_in_scope?: number };
  cancellations: { canceled_orders_in_scope: number; refund_data: string; note: string };
  filter_options: FilterOptions;
};

function complianceTone(pct: number): "good" | "warn" | "bad" {
  if (pct >= 92) return "good";
  if (pct >= 80) return "warn";
  return "bad";
}

export default function SlaDashboard() {
  const { applied, draft, setDraft, apply, reset } = useFilterState();
  const { data, loading, error, reload } = useAnalyticsData<SlaResponse>(
    API_ENDPOINTS.analytics.sla + filtersToQuery(applied)
  );

  const o = data?.status === "OK" ? data.overview : null;
  const maxBucket = useMemo(() => Math.max(1, ...(data?.delay_buckets ?? []).map((b) => b.count)), [data]);
  const trend = useMemo(() => (data?.monthly_trend ?? []).slice(-24), [data]);
  const maxTrendMonitored = useMemo(() => Math.max(1, ...trend.map((t) => t.monitored)), [trend]);

  return (
    <div className="ana-root">
      <header className="ana-header">
        <div>
          <span className="agent-eyebrow">Operations Analytics</span>
          <h2 className="ana-title">SLA &amp; Delivery Promise Monitoring</h2>
          <p className="ana-subtitle">
            Tracks every delivered order against the delivery date promised at purchase. An order is{" "}
            <strong>delayed</strong> when the actual delivery lands after the promised date. Orders that can&apos;t be
            scored (not yet delivered, missing dates) are reported separately — never guessed.
          </p>
        </div>
      </header>

      <FilterBar filters={draft} onChange={setDraft} options={data?.filter_options ?? null} onApply={apply} onReset={reset} />

      {loading && <LoadingState />}
      {error && <ErrorState message={error} onRetry={reload} />}
      {!loading && !error && data?.status === "NO_DATA" && (
        <EmptyState title="No monitorable orders in this slice" reason={data.reason} />
      )}

      {!loading && !error && data?.status === "OK" && o && (
        <>
          <div className="ana-kpi-grid">
            <KpiCard label="Orders Monitored" value={formatNum(o.monitored_orders)} sub={`of ${formatNum(o.total_orders_in_scope)} in scope`} tone="info" title="Delivered orders with both an actual and a promised delivery date." />
            <KpiCard label="On-Time Deliveries" value={formatNum(o.on_time_orders)} sub="delivered ≤ promised date" tone="good" />
            <KpiCard label="Delayed Deliveries" value={formatNum(o.delayed_orders)} sub="delivered > promised date" tone="bad" />
            <KpiCard label="SLA Compliance" value={`${o.sla_compliance_pct}%`} sub="on-time ÷ monitored" tone={complianceTone(o.sla_compliance_pct)} />
            <KpiCard label="Delay Rate" value={`${o.delay_rate_pct}%`} sub="delayed ÷ monitored" tone="warn" />
            <KpiCard label="Avg Delay" value={`${o.avg_delay_days} d`} sub={`median ${o.median_delay_days} d · P90 ${o.p90_delay_days} d`} tone="warn" title="Average days late across delayed orders only." />
            <KpiCard label="Critical Delays" value={formatNum(o.critical_delayed_orders)} sub={`more than ${o.critical_threshold_days} days late`} tone="bad" />
          </div>

          <div className="ana-grid-2">
            <Section title="Delay distribution" hint="delayed orders by how many days late">
              <div className="ana-bars">
                {data.delay_buckets.map((b) => (
                  <BarRow
                    key={b.label}
                    label={b.label}
                    value={b.count}
                    max={maxBucket}
                    valueText={formatNum(b.count)}
                    color={b.label === "on time / early" ? "var(--status-success)" : b.label === "14+ days" ? "var(--status-danger)" : "var(--status-warning)"}
                  />
                ))}
              </div>
            </Section>

            <Section title="Unmonitorable orders" hint="no promise-vs-actual pair exists (yet)">
              <div className="ana-chips">
                {Object.entries(o.unmonitored_by_status).map(([status, n]) => (
                  <span key={status} className={`ana-chip ${status === "delivered" ? "ana-chip-ok" : "ana-chip-neutral"}`}>
                    {status}: {formatNum(n)}
                  </span>
                ))}
              </div>
              <p className="ana-note">
                Orders still in the pipeline (processing / shipped) have no actual delivery date to compare against —
                they join the monitored set once delivered. Canceled/unavailable orders will never be scored.
              </p>
              <p className="ana-note">
                Refunds against deadlines: <strong>unavailable</strong> — {data.cancellations.note}
              </p>
            </Section>
          </div>

          <Section title="Monthly trend" hint="last 24 months — delay rate of monitored orders">
            <div className="ana-trend">
              {trend.map((t) => {
                const height = Math.max((t.monitored / maxTrendMonitored) * 100, 4);
                const delayShare = t.delay_rate_pct / 100;
                return (
                  <div key={t.month} className="ana-trend-col" title={`${t.month}: ${formatNum(t.monitored)} monitored, ${formatNum(t.delayed)} delayed (${t.delay_rate_pct}%), avg delay ${t.avg_delay_days}d`}>
                    <div className="ana-trend-bar" style={{ height: `${height}%` }}>
                      <span className="ana-trend-delay" style={{ height: `${delayShare * 100}%` }} />
                    </div>
                    <span className="ana-trend-label">{t.month.slice(2)}</span>
                  </div>
                );
              })}
            </div>
            <p className="ana-note">Bar height = monitored orders; the filled portion = share delivered late that month.</p>
          </Section>

          <div className="ana-grid-2">
            <Section title="Worst customer states" hint="by number of delayed deliveries">
              <DataTable
                head={["State", "Monitored", "Delayed", "Delay rate", "Avg delay"]}
                rows={data.by_state.map((r) => [
                  r.state,
                  formatNum(r.orders),
                  formatNum(r.delayed),
                  `${r.delay_rate_pct}%`,
                  `${r.avg_delay_days} d`,
                ])}
              />
            </Section>
            <Section title="Worst categories" hint="by delayed deliveries (English category names)">
              <DataTable
                head={["Category", "Monitored", "Delayed", "Delay rate"]}
                rows={data.by_category.map((r) => [r.category, formatNum(r.orders), formatNum(r.delayed), `${r.delay_rate_pct}%`])}
              />
            </Section>
          </div>

          <Section title="Worst sellers" hint="min. 10 monitored orders — top 15 by delayed deliveries">
            <DataTable
              head={["Seller", "State", "Monitored", "Delayed", "Delay rate", "Avg delay"]}
              rows={data.by_seller.map((r) => [
                shortId(r.seller_id),
                r.seller_state,
                formatNum(r.orders),
                formatNum(r.delayed),
                `${r.delay_rate_pct}%`,
                `${r.avg_delay_days} d`,
              ])}
            />
          </Section>

          <Section title={`Critical delayed orders (${formatNum(data.critical_orders.total_critical)} total — worst 15 shown)`} hint={`delayed > ${o.critical_threshold_days} days`}>
            <DataTable
              head={["Order", "Purchased", "Promised", "Delivered", "Days late", "State", "Order value"]}
              rows={data.critical_orders.items.map((r) => [
                shortId(r.order_id),
                r.purchase_date,
                r.promised_date,
                r.delivered_date,
                formatNum(r.delay_days, 1),
                r.customer_state,
                r.value_known ? formatBRL(r.order_value) : "n/a",
              ])}
            />
          </Section>

          <div className="ana-grid-2">
            <Section title="Support response times" hint="review-answer latency as the closest available signal">
              {data.support_response.status === "OK" ? (
                <>
                  <div className="ana-kpi-grid ana-kpi-grid-compact">
                    <KpiCard label="Avg response" value={`${data.support_response.avg_response_hours} h`} tone="neutral" />
                    <KpiCard label="Median" value={`${data.support_response.median_response_hours} h`} tone="neutral" />
                    <KpiCard label="P90" value={`${data.support_response.p90_response_hours} h`} tone="warn" />
                    <KpiCard label="Answered >48 h" value={`${data.support_response.pct_over_48h}%`} tone="warn" />
                  </div>
                  <p className="ana-note">{data.support_response.note}</p>
                </>
              ) : (
                <p className="ana-note">{data.support_response.reason}</p>
              )}
            </Section>
            <Section title="Metric definitions" hint="how each figure above is computed">
              <ul className="ana-definitions">
                {Object.entries(data.definitions).map(([k, v]) => (
                  <li key={k}>
                    <strong>{k}</strong>: {v}
                  </li>
                ))}
                <li>
                  <strong>support response</strong>: observed review-answer latency — the Olist dataset has no support
                  ticket system or contractual response deadline, so no pass/fail SLA is claimed here.
                </li>
              </ul>
            </Section>
          </div>
        </>
      )}
    </div>
  );
}

export function DataTable({ head, rows }: { head: string[]; rows: (string | number)[][] }) {
  return (
    <div className="ana-table-wrap">
      <table className="ana-table">
        <thead>
          <tr>
            {head.map((h) => (
              <th key={h}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={i}>
              {r.map((c, j) => (
                <td key={j}>{c}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

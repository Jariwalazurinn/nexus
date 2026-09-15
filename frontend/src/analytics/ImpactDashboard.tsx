import { useMemo } from "react";
import { API_ENDPOINTS } from "../config";
import { filtersToQuery, formatBRL, formatNum, shortId, useAnalyticsData, useFilterState, type FilterOptions } from "./analyticsShared";
import { BarRow, EmptyState, ErrorState, FilterBar, KpiCard, LoadingState, Section } from "./analyticsComponents";
import { DataTable } from "./SlaDashboard";
import "./AnalyticsDashboards.css";

type ImpactResponse = {
  status: "OK" | "NO_DATA";
  reason?: string;
  filters: Record<string, string | null>;
  data_source: string;
  definitions: Record<string, string>;
  summary: {
    monitored_orders: number;
    delayed_orders: number;
    on_time_orders: number;
    delay_rate_pct: number;
    affected_customers: number;
    affected_order_value: number;
    avg_delay_days: number;
    p90_delay_days: number;
    estimated_revenue_exposure: number;
    actual_lost_revenue: string;
    value_coverage: { delayed_orders_with_value: number; delayed_orders_without_value: number; note: string };
  };
  aov_comparison: {
    delayed_aov: number;
    ontime_aov: number;
    delayed_orders_with_value: number;
    ontime_orders_with_value: number;
    monitored_order_value: number;
  };
  impact_by_seller: { seller_id: string; delayed_orders: number; affected_value: number; avg_delay_days: number }[];
  impact_by_category: { category: string; delayed_orders: number; affected_value: number; avg_delay_days: number }[];
  impact_by_state: { state: string; delayed_orders: number; affected_value: number; avg_delay_days: number }[];
  impact_by_month: { month: string; delayed_orders: number; affected_value: number; avg_delay_days: number }[];
  top_impacted_orders: {
    order_id: string;
    order_value: number;
    delay_days: number;
    purchase_date: string;
    customer_state: string;
  }[];
  filter_options: FilterOptions | null;
};

type GroupRow = { label: string; delayed_orders: number; affected_value: number; avg_delay_days: number };

export default function ImpactDashboard() {
  const { applied, draft, setDraft, apply, reset } = useFilterState();
  const { data, loading, error, reload } = useAnalyticsData<ImpactResponse>(
    API_ENDPOINTS.analytics.impact + filtersToQuery(applied)
  );

  const s = data?.status === "OK" ? data.summary : null;
  const aov = data?.aov_comparison;
  const aovDelta = aov ? aov.delayed_aov - aov.ontime_aov : 0;

  const monthRows: GroupRow[] = useMemo(() => {
    if (data?.status !== "OK") return [];
    return [...data.impact_by_month]
      .map((m) => ({ label: m.month, delayed_orders: m.delayed_orders, affected_value: m.affected_value, avg_delay_days: m.avg_delay_days }))
      .sort((a, b) => a.label.localeCompare(b.label))
      .slice(-24);
  }, [data]);
  const maxMonthValue = useMemo(() => Math.max(1, ...monthRows.map((m) => m.affected_value)), [monthRows]);

  return (
    <div className="ana-root">
      <header className="ana-header">
        <div>
          <span className="agent-eyebrow">Operations Analytics</span>
          <h2 className="ana-title">Business Impact Estimation</h2>
          <p className="ana-subtitle">
            Puts order value behind the delays the SLA dashboard finds, using actual order values from the dataset.
            All figures are <strong>estimates of value affected / exposed</strong> — a late order is not a lost sale,
            and this dashboard never claims otherwise.
          </p>
        </div>
      </header>

      <FilterBar filters={draft} onChange={setDraft} options={data?.filter_options ?? null} onApply={apply} onReset={reset} />

      {loading && <LoadingState />}
      {error && <ErrorState message={error} onRetry={reload} />}
      {!loading && !error && data?.status === "NO_DATA" && <EmptyState title="No delayed orders in this slice" reason={data.reason} />}

      {!loading && !error && data?.status === "OK" && s && aov && (
        <>
          <div className="ana-callout ana-callout-warn">
            <strong>How to read these numbers.</strong>{" "}
            <span>
              <em>Affected order value</em> is the real value of delayed orders. <em>Revenue exposure</em> is the same
              money framed as value that was at risk. <em>Actual lost revenue cannot be calculated</em> — the dataset
              has no refund, penalty, or margin data — so it is never reported.
            </span>
          </div>

          <div className="ana-kpi-grid">
            <KpiCard label="Delayed Orders" value={formatNum(s.delayed_orders)} sub={`of ${formatNum(s.monitored_orders)} monitored (${s.delay_rate_pct}%)`} tone="bad" />
            <KpiCard label="Affected Customers" value={formatNum(s.affected_customers)} sub="unique customers with a late delivery" tone="warn" title="Deduplicated — a customer with several late orders counts once." />
            <KpiCard label="Affected Order Value" value={formatBRL(s.affected_order_value)} sub="Σ price + freight of delayed orders" tone="bad" title={data.definitions.affected_order_value} />
            <KpiCard label="Est. Revenue Exposure" value={formatBRL(s.estimated_revenue_exposure)} sub="same value, viewed as at-risk" tone="warn" title={data.definitions.revenue_exposure} />
            <KpiCard label="Actual Lost Revenue" value="n/a" sub="not calculable from this dataset" tone="neutral" title={data.definitions.lost_revenue} />
            <KpiCard label="Avg Delay" value={`${s.avg_delay_days} d`} sub={`P90 ${s.p90_delay_days} d`} tone="neutral" />
          </div>

          <div className="ana-grid-2">
            <Section title="Average order value: delayed vs on-time" hint="does lateness correlate with bigger baskets?">
              <div className="ana-aov">
                <div className="ana-aov-side">
                  <span className="ana-aov-num ana-aov-bad">{formatBRL(aov.delayed_aov)}</span>
                  <span className="ana-aov-cap">Delayed orders ({formatNum(aov.delayed_orders_with_value)})</span>
                </div>
                <div className={`ana-aov-delta ${aovDelta >= 0 ? "ana-aov-bad" : "ana-aov-good"}`}>
                  {aovDelta >= 0 ? "▲" : "▼"} {formatBRL(Math.abs(aovDelta))} {aovDelta >= 0 ? "higher" : "lower"} when delayed
                </div>
                <div className="ana-aov-side">
                  <span className="ana-aov-num ana-aov-good">{formatBRL(aov.ontime_aov)}</span>
                  <span className="ana-aov-cap">On-time orders ({formatNum(aov.ontime_orders_with_value)})</span>
                </div>
              </div>
              <p className="ana-note">Order value = item prices + freight. Orders missing item rows are excluded from both sides (never valued at zero).</p>
            </Section>
            <Section title="Value coverage" hint="how complete the financial picture is">
              <div className="ana-chips">
                <span className="ana-chip ana-chip-ok">delayed orders with item values: {formatNum(s.value_coverage.delayed_orders_with_value)}</span>
                <span className="ana-chip ana-chip-neutral">without item values: {formatNum(s.value_coverage.delayed_orders_without_value)}</span>
                <span className="ana-chip ana-chip-neutral">total monitored order value: {formatBRL(aov.monitored_order_value)}</span>
              </div>
              <p className="ana-note">{s.value_coverage.note}</p>
              <p className="ana-note">
                Affected order value is {formatBRL(s.affected_order_value)} of {formatBRL(aov.monitored_order_value)} monitored —{" "}
                {aov.monitored_order_value > 0 ? ((s.affected_order_value / aov.monitored_order_value) * 100).toFixed(1) : "0"}% of monitored value sits in delayed orders.
              </p>
            </Section>
          </div>

          <Section title="Exposure by month" hint="affected order value per purchase month (last 24)">
            <div className="ana-bars ana-bars-tall">
              {monthRows.map((m) => (
                <BarRow
                  key={m.label}
                  label={m.label}
                  value={m.affected_value}
                  max={maxMonthValue}
                  valueText={formatBRL(m.affected_value)}
                  color="var(--status-danger)"
                />
              ))}
            </div>
          </Section>

          <div className="ana-grid-2">
            <Section title="Exposure by category" hint="top categories by affected order value">
              <DataTable
                head={["Category", "Delayed orders", "Affected value", "Avg delay"]}
                rows={data.impact_by_category.map((r) => [r.category, formatNum(r.delayed_orders), formatBRL(r.affected_value), `${r.avg_delay_days} d`])}
              />
            </Section>
            <Section title="Exposure by customer state" hint="where affected value concentrates">
              <DataTable
                head={["State", "Delayed orders", "Affected value", "Avg delay"]}
                rows={data.impact_by_state.map((r) => [r.state, formatNum(r.delayed_orders), formatBRL(r.affected_value), `${r.avg_delay_days} d`])}
              />
            </Section>
          </div>

          <Section title="Exposure by seller" hint="top 15 by affected order value">
            <DataTable
              head={["Seller", "Delayed orders", "Affected value", "Avg delay"]}
              rows={data.impact_by_seller.map((r) => [shortId(r.seller_id), formatNum(r.delayed_orders), formatBRL(r.affected_value), `${r.avg_delay_days} d`])}
            />
          </Section>

          <Section title="High-impact delayed orders" hint="largest order values among delayed orders">
            <DataTable
              head={["Order", "Purchased", "Order value", "Days late", "State"]}
              rows={data.top_impacted_orders.map((r) => [
                shortId(r.order_id),
                r.purchase_date,
                formatBRL(r.order_value),
                formatNum(r.delay_days, 1),
                r.customer_state,
              ])}
            />
          </Section>

          <Section title="Metric definitions" hint="and what this dashboard deliberately does not claim">
            <ul className="ana-definitions">
              {Object.entries(data.definitions).map(([k, v]) => (
                <li key={k}>
                  <strong>{k}</strong>: {v}
                </li>
              ))}
            </ul>
          </Section>
        </>
      )}
    </div>
  );
}

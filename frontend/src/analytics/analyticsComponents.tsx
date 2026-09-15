/** Presentational components shared by the SLA and Business Impact
 * dashboards. Pure logic lives in analyticsShared.ts; this file exports
 * components only (keeps react-refresh lint happy). */
import type { ReactNode } from "react";
import { AnalyticsFilters, FilterOptions, formatNum, shortId } from "./analyticsShared";

/** Horizontal CSS bar chart row. */
export function BarRow({
  label,
  value,
  max,
  valueText,
  color = "var(--accent-primary-light)",
}: {
  label: string;
  value: number;
  max: number;
  valueText: string;
  color?: string;
}) {
  const pctWidth = max > 0 ? Math.max((value / max) * 100, value > 0 ? 2 : 0) : 0;
  return (
    <div className="ana-bar-row" title={`${label}: ${valueText}`}>
      <span className="ana-bar-label" title={label}>
        {label}
      </span>
      <span className="ana-bar-track">
        <span className="ana-bar-fill" style={{ width: `${pctWidth}%`, background: color }} />
      </span>
      <span className="ana-bar-value">{valueText}</span>
    </div>
  );
}

export function KpiCard({
  label,
  value,
  sub,
  tone = "neutral",
  title,
}: {
  label: string;
  value: string;
  sub?: string;
  tone?: "neutral" | "good" | "warn" | "bad" | "info";
  title?: string;
}) {
  return (
    <div className={`ana-kpi ana-kpi-${tone}`} title={title}>
      <span className="ana-kpi-label">{label}</span>
      <span className="ana-kpi-value">{value}</span>
      {sub && <span className="ana-kpi-sub">{sub}</span>}
    </div>
  );
}

export function Section({ title, hint, children }: { title: string; hint?: string; children: ReactNode }) {
  return (
    <section className="ana-section">
      <div className="ana-section-head">
        <h3>{title}</h3>
        {hint && <span className="ana-section-hint">{hint}</span>}
      </div>
      {children}
    </section>
  );
}

export function LoadingState({ text = "Crunching the order book…" }: { text?: string }) {
  return (
    <div className="ana-state">
      <span className="button-spinner" aria-hidden />
      <p>{text}</p>
    </div>
  );
}

export function ErrorState({ message, onRetry }: { message: string; onRetry: () => void }) {
  return (
    <div className="ana-state ana-state-error">
      <span className="error-icon">⚠️</span>
      <p>{message}</p>
      <button className="dav-btn dav-btn-primary" onClick={onRetry}>
        Retry
      </button>
    </div>
  );
}

export function EmptyState({ title, reason }: { title: string; reason?: string }) {
  return (
    <div className="ana-state">
      <span className="ana-empty-icon">🗂️</span>
      <p>
        <strong>{title}</strong>
      </p>
      {reason && <p className="ana-empty-reason">{reason}</p>}
    </div>
  );
}

export function FilterBar({
  filters,
  onChange,
  options,
  onApply,
  onReset,
}: {
  filters: AnalyticsFilters;
  onChange: (f: AnalyticsFilters) => void;
  options: FilterOptions | null;
  onApply: () => void;
  onReset: () => void;
}) {
  const set = (patch: Partial<AnalyticsFilters>) => onChange({ ...filters, ...patch });
  return (
    <div className="ana-filterbar">
      <label>
        From
        <input type="date" value={filters.start} onChange={(e) => set({ start: e.target.value })} />
      </label>
      <label>
        To
        <input type="date" value={filters.end} onChange={(e) => set({ end: e.target.value })} />
      </label>
      <label>
        State
        <select value={filters.state} onChange={(e) => set({ state: e.target.value })}>
          <option value="">All states</option>
          {(options?.states ?? []).map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
      </label>
      <label>
        Category
        <select value={filters.category} onChange={(e) => set({ category: e.target.value })}>
          <option value="">All categories</option>
          {(options?.categories ?? []).map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>
      </label>
      <label>
        Seller
        <select value={filters.seller} onChange={(e) => set({ seller: e.target.value })}>
          <option value="">All sellers</option>
          {(options?.sellers ?? []).map((s) => (
            <option key={s.seller_id} value={s.seller_id}>
              {shortId(s.seller_id)} ({formatNum(s.orders)} orders)
            </option>
          ))}
        </select>
      </label>
      <div className="ana-filterbar-actions">
        <button className="dav-btn dav-btn-primary" onClick={onApply}>
          Apply
        </button>
        <button className="ana-btn-ghost" onClick={onReset}>
          Reset
        </button>
      </div>
    </div>
  );
}

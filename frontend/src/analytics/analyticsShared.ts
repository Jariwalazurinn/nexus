/** Pure logic for the analytics dashboards: types, filter state, auth-aware
 * fetching, and formatting. No React components here (see
 * analyticsComponents.tsx) so fast-refresh lint stays clean. */
import { useCallback, useEffect, useState } from "react";

export type AnalyticsFilters = {
  start: string;
  end: string;
  state: string;
  seller: string;
  category: string;
};

export const EMPTY_FILTERS: AnalyticsFilters = { start: "", end: "", state: "", seller: "", category: "" };

export type FilterOptions = {
  states: string[];
  categories: string[];
  sellers: { seller_id: string; orders: number }[];
  purchase_date_range: [string | null, string | null];
};

export function filtersToQuery(f: AnalyticsFilters): string {
  const p = new URLSearchParams();
  if (f.start) p.set("start", f.start);
  if (f.end) p.set("end", f.end);
  if (f.state) p.set("state", f.state);
  if (f.seller) p.set("seller", f.seller);
  if (f.category) p.set("category", f.category);
  const s = p.toString();
  return s ? `?${s}` : "";
}

/** Fetch helper that mirrors the app's auth-aware semantics for these
 * dashboards (token attached, 401 surfaces a clear message). */
export async function fetchAnalytics<T>(url: string): Promise<T> {
  const token = (() => {
    try {
      return localStorage.getItem("commerceos_token");
    } catch {
      return null;
    }
  })();
  const headers: Record<string, string> = { Accept: "application/json" };
  if (token) headers.Authorization = `Bearer ${token}`;
  const res = await fetch(url, { headers });
  if (res.status === 401) throw new Error("Session expired — please log in again.");
  if (!res.ok) throw new Error(`Request failed (${res.status})`);
  return (await res.json()) as T;
}

/** Data-loading hook: loading / error / empty states in one place. */
export function useAnalyticsData<T>(url: string) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const reload = useCallback(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    fetchAnalytics<T>(url)
      .then((d) => {
        if (!cancelled) setData(d);
      })
      .catch((e: Error) => {
        if (!cancelled) setError(e.message);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [url]);

  useEffect(() => reload(), [reload]);
  return { data, loading, error, reload };
}

export function formatBRL(v: number | null | undefined): string {
  if (v === null || v === undefined || Number.isNaN(v)) return "—";
  return `R$ ${v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

export function formatNum(v: number | null | undefined, digits = 0): string {
  if (v === null || v === undefined || Number.isNaN(v)) return "—";
  return v.toLocaleString("en-US", { minimumFractionDigits: digits, maximumFractionDigits: digits });
}

/** Shortens 32-char seller ids for table display. */
export function shortId(id: string): string {
  return id.length > 12 ? `${id.slice(0, 6)}…${id.slice(-4)}` : id;
}

/** Convenience hook managing the filter draft/apply cycle. `applied` is what
 * the API call uses; `draft` is what the inputs edit until Apply is clicked. */
export function useFilterState() {
  const [applied, setApplied] = useState<AnalyticsFilters>(EMPTY_FILTERS);
  const [draft, setDraft] = useState<AnalyticsFilters>(EMPTY_FILTERS);
  const apply = useCallback(() => setApplied({ ...draft }), [draft]);
  const reset = useCallback(() => {
    setDraft(EMPTY_FILTERS);
    setApplied(EMPTY_FILTERS);
  }, []);
  return { applied, draft, setDraft, apply, reset };
}

/**
 * FR-047 live eval benchmark panel for Station health.
 */

import { useCallback, useEffect, useState } from 'react';
import {
  fetchStationHealthEvalBenchmark,
  type StationHealthEvalBenchmark,
} from '@/utils/stationHealthApi';
import {
  STATION_HEALTH_EVAL_EMPTY,
  STATION_HEALTH_EVAL_ERROR,
  STATION_HEALTH_EVAL_HEADING,
  STATION_HEALTH_EVAL_INTRO,
  STATION_HEALTH_EVAL_LOADING,
  STATION_HEALTH_NONE,
} from '@/utils/stationHealthCopy';

/**
 * Join top lint codes for the eval panel.
 *
 * @param snapshot - Eval benchmark payload
 * @returns Display string
 * @example
 * const _ = true;
 */
function formatTopCodes(snapshot: StationHealthEvalBenchmark | null): string {
  const rows = snapshot?.top_lint_codes;
  if (!rows?.length) {
    return STATION_HEALTH_NONE;
  }
  return rows.map((row) => `${row.code} ${row.count}`).join(', ');
}

/**
 * Join product ids for the eval panel.
 *
 * @param snapshot - Eval benchmark payload
 * @returns Display string
 * @example
 * const _ = true;
 */
function formatProducts(snapshot: StationHealthEvalBenchmark | null): string {
  const products = snapshot?.products;
  if (!products?.length) {
    return STATION_HEALTH_NONE;
  }
  return products.join(', ');
}

/**
 * Join product failure breakdown rows.
 *
 * @param snapshot - Eval benchmark payload
 * @returns Display string
 * @example
 * const _ = true;
 */
function formatBreakdown(snapshot: StationHealthEvalBenchmark | null): string {
  const rows = snapshot?.product_breakdown;
  if (!rows?.length) {
    return STATION_HEALTH_NONE;
  }
  return rows
    .map((row) => `${row.product.toUpperCase()} ${row.failure_count}`)
    .join(', ');
}

/**
 * Format IWXXM pass / fail / skip for the panel.
 *
 * @param snapshot - Eval benchmark payload
 * @returns Display string
 * @example
 * const _ = true;
 */
function formatIwxxm(snapshot: StationHealthEvalBenchmark | null): string {
  const iwxxm = snapshot?.iwxxm_validation;
  return `${iwxxm?.pass ?? 0} / ${iwxxm?.fail ?? 0} / ${iwxxm?.skip ?? 0}`;
}

/**
 * Show the latest FR-045 live-eval snapshot on Station health.
 *
 * @example
 * const _ = true;
 */
export function StationHealthEvalPanel() {
  const [snapshot, setSnapshot] = useState<StationHealthEvalBenchmark | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async (signal: AbortSignal) => {
    setLoading(true);
    setError(null);
    try {
      const body = await fetchStationHealthEvalBenchmark({ signal });
      setSnapshot(body);
    } catch (err: unknown) {
      if (err instanceof DOMException && err.name === 'AbortError') {
        return;
      }
      setError(STATION_HEALTH_EVAL_ERROR);
      setSnapshot(null);
    } finally {
      if (!signal.aborted) {
        setLoading(false);
      }
    }
  }, []);

  /* eslint-disable react-hooks/set-state-in-effect -- mount fetch for eval panel */
  useEffect(() => {
    const controller = new AbortController();
    void load(controller.signal);
    return () => controller.abort();
  }, [load]);
  /* eslint-enable react-hooks/set-state-in-effect */

  return (
    <section
      className="mt-6 max-w-3xl rounded border border-gray-200 p-4 dark:border-gray-700"
      data-testid="station-health-eval-panel"
      aria-labelledby="station-health-eval-heading"
    >
      <h2 id="station-health-eval-heading" className="text-lg font-medium">
        {STATION_HEALTH_EVAL_HEADING}
      </h2>
      <p className="mt-1 text-sm text-gray-600 dark:text-gray-300">
        {STATION_HEALTH_EVAL_INTRO}
      </p>
      {loading ? (
        <p
          className="mt-3 text-sm text-gray-600"
          data-testid="station-health-eval-loading"
        >
          {STATION_HEALTH_EVAL_LOADING}
        </p>
      ) : null}
      {error ? (
        <p
          className="mt-3 text-sm text-red-700"
          data-testid="station-health-eval-error"
          role="alert"
        >
          {error}
        </p>
      ) : null}
      {!loading && !error && snapshot ? (
        <dl
          className="mt-3 grid grid-cols-2 gap-x-4 gap-y-2 text-sm text-gray-800 dark:text-gray-100"
          data-testid="station-health-eval-stats"
        >
          <dt>Computed at</dt>
          <dd data-testid="station-health-eval-computed-at">
            {snapshot.computed_at || STATION_HEALTH_EVAL_EMPTY}
          </dd>
          <dt>Products</dt>
          <dd data-testid="station-health-eval-products">{formatProducts(snapshot)}</dd>
          <dt>Partial decode</dt>
          <dd data-testid="station-health-eval-partial">
            {snapshot.partial_decode_count}
          </dd>
          <dt>Lint issues</dt>
          <dd data-testid="station-health-eval-lint">{snapshot.lint_count}</dd>
          <dt>Convert failures</dt>
          <dd data-testid="station-health-eval-convert">
            {snapshot.convert_failure_count}
          </dd>
          <dt>IWXXM pass / fail / skip</dt>
          <dd data-testid="station-health-eval-iwxxm">{formatIwxxm(snapshot)}</dd>
          <dt>Top lint codes</dt>
          <dd data-testid="station-health-eval-top-codes">
            {formatTopCodes(snapshot)}
          </dd>
          <dt>Product failure breakdown</dt>
          <dd data-testid="station-health-eval-breakdown">
            {formatBreakdown(snapshot)}
          </dd>
        </dl>
      ) : null}
    </section>
  );
}

/**
 * Public Station health dashboard — availability and quality grades.
 */

import { useCallback, useEffect, useState } from 'react';
import {
  fetchStationHealthList,
  fetchStationHealthMetrics,
  type StationHealthListItem,
  type StationHealthMetric,
} from '@/utils/stationHealthApi';
import {
  STATION_HEALTH_COL_GRADE,
  STATION_HEALTH_COL_PRODUCTS,
  STATION_HEALTH_COL_SCORE,
  STATION_HEALTH_COL_STATION,
  STATION_HEALTH_EMPTY,
  STATION_HEALTH_FILTER_ALL,
  STATION_HEALTH_GRADE_LABEL,
  STATION_HEALTH_INTRO,
  STATION_HEALTH_LOAD_ERROR,
  STATION_HEALTH_LOADING,
  STATION_HEALTH_METRICS_HEADING,
  STATION_HEALTH_PAGE_TITLE,
  STATION_HEALTH_PRODUCT_LABEL,
  STATION_HEALTH_SUMMARY_HEADING,
  STATION_HEALTH_WINDOW_LABEL,
} from '@/utils/stationHealthCopy';
import { shellFrameClass, useLiveConvertLayout } from '@/utils/liveConvertLayout';

/**
 * Drop the sentinel "all" filter value from API query params.
 *
 * @param value - Select value
 * @returns Undefined when the filter is All
 * @example
 * const _ = true;
 */
function optionalFilter(value: string): string | undefined {
  return value === 'all' ? undefined : value;
}

/**
 * Station health dashboard with window, product, and grade filters.
 *
 * @example
 * const _ = true;
 */
export function StationHealthPage() {
  const { layout } = useLiveConvertLayout();
  const frame = shellFrameClass(layout.span);
  const [stations, setStations] = useState<StationHealthListItem[]>([]);
  const [metrics, setMetrics] = useState<StationHealthMetric[]>([]);
  const [gradeCounts, setGradeCounts] = useState<Record<string, number>>({});
  const [windowKey, setWindowKey] = useState('6h');
  const [product, setProduct] = useState('all');
  const [grade, setGrade] = useState('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [list, registry] = await Promise.all([
        fetchStationHealthList({
          window: windowKey,
          product: optionalFilter(product),
          grade: optionalFilter(grade),
        }),
        fetchStationHealthMetrics(),
      ]);
      setStations(list.stations ?? []);
      setGradeCounts(list.summary?.grade_counts ?? {});
      setMetrics(registry.metrics ?? []);
    } catch {
      setError(STATION_HEALTH_LOAD_ERROR);
      setStations([]);
    } finally {
      setLoading(false);
    }
  }, [windowKey, product, grade]);

  /* eslint-disable react-hooks/set-state-in-effect -- refetch when filters change */
  useEffect(() => {
    void load();
  }, [load]);
  /* eslint-enable react-hooks/set-state-in-effect */

  return (
    <main
      className={`mx-auto w-full px-4 py-6 ${frame}`}
      data-testid="station-health-page"
    >
      <h1 className="text-2xl font-semibold text-gray-900 dark:text-gray-100">
        {STATION_HEALTH_PAGE_TITLE}
      </h1>
      <p className="mt-2 max-w-3xl text-sm text-gray-600 dark:text-gray-300">
        {STATION_HEALTH_INTRO}
      </p>

      <section
        className="mt-6 flex flex-wrap gap-3"
        data-testid="station-health-filters"
        aria-label="Station health filters"
      >
        <label className="flex flex-col gap-1 text-sm">
          <span>{STATION_HEALTH_WINDOW_LABEL}</span>
          <select
            data-testid="station-health-window"
            className="rounded border border-gray-300 bg-white px-2 py-1 dark:border-gray-600 dark:bg-gray-900"
            value={windowKey}
            onChange={(event) => setWindowKey(event.target.value)}
          >
            <option value="6h">Last 6 hours</option>
            <option value="1d">Last 1 day</option>
            <option value="30d">Last 1 month</option>
          </select>
        </label>
        <label className="flex flex-col gap-1 text-sm">
          <span>{STATION_HEALTH_PRODUCT_LABEL}</span>
          <select
            data-testid="station-health-product"
            className="rounded border border-gray-300 bg-white px-2 py-1 dark:border-gray-600 dark:bg-gray-900"
            value={product}
            onChange={(event) => setProduct(event.target.value)}
          >
            <option value="all">{STATION_HEALTH_FILTER_ALL}</option>
            <option value="metar">METAR</option>
            <option value="speci">SPECI</option>
            <option value="taf">TAF</option>
          </select>
        </label>
        <label className="flex flex-col gap-1 text-sm">
          <span>{STATION_HEALTH_GRADE_LABEL}</span>
          <select
            data-testid="station-health-grade"
            className="rounded border border-gray-300 bg-white px-2 py-1 dark:border-gray-600 dark:bg-gray-900"
            value={grade}
            onChange={(event) => setGrade(event.target.value)}
          >
            <option value="all">{STATION_HEALTH_FILTER_ALL}</option>
            {['A', 'B', 'C', 'D', 'F'].map((letter) => (
              <option key={letter} value={letter}>
                {letter}
              </option>
            ))}
          </select>
        </label>
      </section>

      <section className="mt-6" aria-labelledby="station-health-summary-heading">
        <h2 id="station-health-summary-heading" className="text-lg font-medium">
          {STATION_HEALTH_SUMMARY_HEADING}
        </h2>
        <div
          className="mt-2 flex flex-wrap gap-3 text-sm text-gray-700 dark:text-gray-200"
          data-testid="station-health-summary"
        >
          {['A', 'B', 'C', 'D', 'F'].map((letter) => (
            <span key={letter} data-testid={`station-health-grade-count-${letter}`}>
              {letter}: {gradeCounts[letter] ?? 0}
            </span>
          ))}
        </div>
      </section>

      {loading ? (
        <p className="mt-6 text-sm text-gray-600" data-testid="station-health-loading">
          {STATION_HEALTH_LOADING}
        </p>
      ) : null}
      {error ? (
        <p
          className="mt-6 text-sm text-red-700"
          data-testid="station-health-error"
          role="alert"
        >
          {error}
        </p>
      ) : null}
      {!loading && !error && stations.length === 0 ? (
        <p className="mt-6 text-sm text-gray-600" data-testid="station-health-empty">
          {STATION_HEALTH_EMPTY}
        </p>
      ) : null}

      {!loading && !error && stations.length > 0 ? (
        <div className="mt-6 overflow-x-auto" data-testid="station-health-table">
          <table className="min-w-full border-collapse text-left text-sm">
            <thead>
              <tr className="border-b border-gray-200 dark:border-gray-700">
                <th className="py-2 pr-4 font-medium">{STATION_HEALTH_COL_STATION}</th>
                <th className="py-2 pr-4 font-medium">{STATION_HEALTH_COL_GRADE}</th>
                <th className="py-2 pr-4 font-medium">{STATION_HEALTH_COL_SCORE}</th>
                <th className="py-2 pr-4 font-medium">{STATION_HEALTH_COL_PRODUCTS}</th>
              </tr>
            </thead>
            <tbody>
              {stations.map((row) => (
                <tr
                  key={row.icao}
                  className="border-b border-gray-100 dark:border-gray-800"
                  data-testid={`station-health-row-${row.icao}`}
                >
                  <td className="py-2 pr-4">
                    <span className="font-medium">{row.icao}</span>
                    {row.name ? (
                      <span className="ml-2 text-gray-500">{row.name}</span>
                    ) : null}
                  </td>
                  <td className="py-2 pr-4">{row.overall_grade}</td>
                  <td className="py-2 pr-4">{row.overall_score.toFixed(1)}</td>
                  <td className="py-2 pr-4">
                    {row.products
                      .map((item) => `${item.product.toUpperCase()} ${item.grade}`)
                      .join(', ')}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}

      <section className="mt-8" aria-labelledby="station-health-metrics-heading">
        <h2 id="station-health-metrics-heading" className="text-lg font-medium">
          {STATION_HEALTH_METRICS_HEADING}
        </h2>
        <ul className="mt-3 space-y-2" data-testid="station-health-metrics">
          {metrics.map((metric) => (
            <li key={metric.id} data-testid={`station-health-metric-${metric.id}`}>
              <span className="font-medium">{metric.label}</span>
              <span className="ml-2 text-sm text-gray-600 dark:text-gray-300">
                {metric.description}
              </span>
            </li>
          ))}
        </ul>
      </section>
    </main>
  );
}

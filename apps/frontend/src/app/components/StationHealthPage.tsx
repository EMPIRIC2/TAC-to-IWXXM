/**
 * Public Station health dashboard - availability and quality grades.
 */

import { useCallback, useEffect, useState } from 'react';
import {
  fetchStationHealthList,
  fetchStationHealthMetrics,
  type StationHealthListItem,
  type StationHealthMetric,
  type StationProductGrade,
} from '@/utils/stationHealthApi';
import {
  formatComponentScore,
  formatCountMap,
  formatStationHealthRegion,
  STATION_HEALTH_COL_AVAILABILITY,
  STATION_HEALTH_COL_CENTENNIAL,
  STATION_HEALTH_COL_FORMATS,
  STATION_HEALTH_COL_GRADE,
  STATION_HEALTH_COL_ISSUES,
  STATION_HEALTH_COL_LINT,
  STATION_HEALTH_COL_MAINTENANCE,
  STATION_HEALTH_COL_MISSING,
  STATION_HEALTH_COL_PRODUCTS,
  STATION_HEALTH_COL_REGION,
  STATION_HEALTH_COL_SOLIDUS,
  STATION_HEALTH_COL_STATION,
  STATION_HEALTH_EMPTY,
  STATION_HEALTH_FILTER_ALL,
  STATION_HEALTH_GRADE_LABEL,
  STATION_HEALTH_INSUFFICIENT,
  STATION_HEALTH_INTRO,
  STATION_HEALTH_LOAD_ERROR,
  STATION_HEALTH_LOADING,
  STATION_HEALTH_METRICS_HEADING,
  STATION_HEALTH_PAGE_TITLE,
  STATION_HEALTH_PRODUCT_LABEL,
  STATION_HEALTH_REGION_LABEL,
  STATION_HEALTH_REGION_OPTIONS,
  STATION_HEALTH_SCORE_HELP,
  STATION_HEALTH_SCORE_HELP_HEADING,
  STATION_HEALTH_SUMMARY_HEADING,
  STATION_HEALTH_WINDOW_LABEL,
} from '@/utils/stationHealthCopy';
import { shellFrameClass, useLiveConvertLayout } from '@/utils/liveConvertLayout';

/** Default page size when no WMO region filter is selected. */
const DEFAULT_LIST_LIMIT = 100;
/** Cap when loading every station in one WMO region. */
const REGION_LIST_LIMIT = 5000;

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
 * Average one numeric product field for the selected window row.
 *
 * @param products - Product grade rows
 * @param key - Field to average
 * @returns Mean value, or null when empty
 * @example
 * const _ = true;
 */
function averageProductField(
  products: StationProductGrade[] | null | undefined,
  key:
    | 'availability_score'
    | 'solidus_rate'
    | 'missing_digit_rate'
    | 'lint_severity_score',
): number | null {
  if (!products || products.length === 0) {
    return null;
  }
  const total = products.reduce((sum, row) => sum + Number(row[key] ?? 0), 0);
  return total / products.length;
}

/**
 * Station health dashboard with window, product, grade, and region filters.
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
  const [region, setRegion] = useState('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    const regionFilter = optionalFilter(region);
    try {
      const [list, registry] = await Promise.all([
        fetchStationHealthList({
          window: windowKey,
          product: optionalFilter(product),
          grade: optionalFilter(grade),
          region: regionFilter,
          limit: regionFilter ? REGION_LIST_LIMIT : DEFAULT_LIST_LIMIT,
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
  }, [windowKey, product, grade, region]);

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
            <option value="90d">Last 3 months</option>
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
        <label className="flex flex-col gap-1 text-sm">
          <span>{STATION_HEALTH_REGION_LABEL}</span>
          <select
            data-testid="station-health-region"
            className="rounded border border-gray-300 bg-white px-2 py-1 dark:border-gray-600 dark:bg-gray-900"
            value={region}
            onChange={(event) => setRegion(event.target.value)}
          >
            <option value="all">{STATION_HEALTH_FILTER_ALL}</option>
            {STATION_HEALTH_REGION_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
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

      <details
        className="mt-4 max-w-3xl text-sm text-gray-700 dark:text-gray-200"
        data-testid="station-health-score-help"
      >
        <summary className="cursor-pointer font-medium">
          {STATION_HEALTH_SCORE_HELP_HEADING}
        </summary>
        <p className="mt-2 text-gray-600 dark:text-gray-300">
          {STATION_HEALTH_SCORE_HELP}
        </p>
      </details>

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
            <caption className="sr-only">{STATION_HEALTH_SCORE_HELP}</caption>
            <thead>
              <tr className="border-b border-gray-200 dark:border-gray-700">
                <th className="py-2 pr-4 font-medium">{STATION_HEALTH_COL_STATION}</th>
                <th className="py-2 pr-4 font-medium">{STATION_HEALTH_COL_REGION}</th>
                <th className="py-2 pr-4 font-medium">{STATION_HEALTH_COL_GRADE}</th>
                <th
                  className="py-2 pr-4 font-medium"
                  data-testid="station-health-col-availability"
                >
                  {STATION_HEALTH_COL_AVAILABILITY}
                </th>
                <th
                  className="py-2 pr-4 font-medium"
                  data-testid="station-health-col-solidus"
                >
                  {STATION_HEALTH_COL_SOLIDUS}
                </th>
                <th
                  className="py-2 pr-4 font-medium"
                  data-testid="station-health-col-missing"
                >
                  {STATION_HEALTH_COL_MISSING}
                </th>
                <th
                  className="py-2 pr-4 font-medium"
                  data-testid="station-health-col-lint"
                >
                  {STATION_HEALTH_COL_LINT}
                </th>
                <th className="py-2 pr-4 font-medium">{STATION_HEALTH_COL_PRODUCTS}</th>
                <th className="py-2 pr-4 font-medium">
                  {STATION_HEALTH_COL_MAINTENANCE}
                </th>
                <th className="py-2 pr-4 font-medium">{STATION_HEALTH_COL_FORMATS}</th>
                <th className="py-2 pr-4 font-medium">{STATION_HEALTH_COL_ISSUES}</th>
                <th className="py-2 pr-4 font-medium">
                  {STATION_HEALTH_COL_CENTENNIAL}
                </th>
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
                  <td
                    className="py-2 pr-4"
                    data-testid={`station-health-region-${row.icao}`}
                  >
                    {formatStationHealthRegion(row.wmo_region)}
                  </td>
                  <td
                    className="py-2 pr-4"
                    data-testid={`station-health-grade-${row.icao}`}
                  >
                    {row.overall_grade}
                  </td>
                  <td
                    className="py-2 pr-4"
                    data-testid={`station-health-availability-${row.icao}`}
                  >
                    {formatComponentScore(
                      averageProductField(row.products, 'availability_score'),
                    )}
                  </td>
                  <td
                    className="py-2 pr-4"
                    data-testid={`station-health-solidus-${row.icao}`}
                  >
                    {formatComponentScore(
                      averageProductField(row.products, 'solidus_rate'),
                      3,
                    )}
                  </td>
                  <td
                    className="py-2 pr-4"
                    data-testid={`station-health-missing-${row.icao}`}
                  >
                    {formatComponentScore(
                      averageProductField(row.products, 'missing_digit_rate'),
                      3,
                    )}
                  </td>
                  <td
                    className="py-2 pr-4"
                    data-testid={`station-health-lint-${row.icao}`}
                  >
                    {formatComponentScore(
                      averageProductField(row.products, 'lint_severity_score'),
                    )}
                  </td>
                  <td className="py-2 pr-4">
                    {row.products
                      .map((item) => `${item.product.toUpperCase()} ${item.grade}`)
                      .join(', ')}
                  </td>
                  <td
                    className="py-2 pr-4"
                    data-testid={`station-health-maintenance-${row.icao}`}
                  >
                    {formatCountMap(row.maintenance_tag_counts)}
                  </td>
                  <td
                    className="py-2 pr-4"
                    data-testid={`station-health-formats-${row.icao}`}
                  >
                    {formatCountMap(row.file_format_counts)}
                  </td>
                  <td
                    className="py-2 pr-4"
                    data-testid={`station-health-issues-${row.icao}`}
                  >
                    {formatCountMap(row.issue_code_counts)}
                  </td>
                  <td
                    className="py-2 pr-4"
                    data-testid={`station-health-centennial-${row.icao}`}
                  >
                    {(row.centennial_metrics ?? [])
                      .filter((metric) => metric.status === 'available')
                      .map((metric) =>
                        metric.score == null
                          ? metric.label
                          : `${metric.label} ${metric.score.toFixed(0)}`,
                      )
                      .join(', ') || STATION_HEALTH_INSUFFICIENT}
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

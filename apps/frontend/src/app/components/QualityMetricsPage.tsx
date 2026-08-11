/**
 * Quality metrics corpus browser — product filter, summary strip, file list, detail.
 *
 * List + detail for F7.q / EV-054 (AC1–AC5).
 */

import { useCallback, useEffect, useMemo, useState } from 'react';
import { Loader2 } from 'lucide-react';
import { fetchQualityMetrics, fetchQualityMetricsDetail } from '@/utils/api';
import type {
  QualityMetricsDetailResponse,
  QualityMetricsFileRow,
  QualityMetricsSummary,
} from '@/utils/openapiTypes';
import { QualityMetricsDetail } from './QualityMetricsDetail';
import { Card } from './ui/card';

/** Operator-visible label for deferred / gap stems (AC5). */
export const QUALITY_METRICS_DEFERRED_LABEL = 'Deferred gap';

/** Page title — primary shell tab. */
export const QUALITY_METRICS_PAGE_TITLE = 'Quality metrics';

interface QualityMetricsPageProps {
  /** Optional stem select hook (in addition to in-page detail). */
  onSelectStem?: (stem: string) => void;
}

/**
 * Browse precomputed official-corpus quality metrics by product.
 *
 * @param props.onSelectStem - Optional callback when a file row is activated
 */
export function QualityMetricsPage({ onSelectStem }: QualityMetricsPageProps) {
  const [productFilter, setProductFilter] = useState<string>('all');
  const [summaries, setSummaries] = useState<QualityMetricsSummary[]>([]);
  const [files, setFiles] = useState<QualityMetricsFileRow[]>([]);
  const [generatedAt, setGeneratedAt] = useState<string>('');
  const [iwxxmPin, setIwxxmPin] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedStem, setSelectedStem] = useState<string | null>(null);
  const [detail, setDetail] = useState<QualityMetricsDetailResponse | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailError, setDetailError] = useState<string | null>(null);

  const loadMetrics = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetchQualityMetrics({
        product: productFilter === 'all' ? undefined : productFilter,
      });
      setSummaries(response.summaries);
      setFiles(response.files);
      setGeneratedAt(response.generated_at);
      setIwxxmPin(response.iwxxm_pin);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load quality metrics');
      setSummaries([]);
      setFiles([]);
    } finally {
      setLoading(false);
    }
  }, [productFilter]);

  /* eslint-disable react-hooks/set-state-in-effect -- refetch when product filter changes */
  useEffect(() => {
    void loadMetrics();
  }, [loadMetrics]);
  /* eslint-enable react-hooks/set-state-in-effect */

  useEffect(() => {
    if (!selectedStem) {
      return;
    }

    let cancelled = false;
    void (async () => {
      setDetailLoading(true);
      setDetailError(null);
      try {
        const response = await fetchQualityMetricsDetail({ stem: selectedStem });
        if (!cancelled) {
          setDetail(response);
        }
      } catch (err: unknown) {
        if (!cancelled) {
          setDetail(null);
          setDetailError(
            err instanceof Error ? err.message : 'Failed to load stem detail',
          );
        }
      } finally {
        if (!cancelled) {
          setDetailLoading(false);
        }
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [selectedStem]);

  const productOptions = useMemo(() => {
    const fromSummaries = summaries.map((s) => s.product);
    const fromFiles = files.map((f) => f.product);
    return Array.from(new Set([...fromSummaries, ...fromFiles])).sort();
  }, [files, summaries]);

  const activeSummary = useMemo(() => {
    if (productFilter === 'all') {
      return summaries.reduce(
        (acc, row) => ({
          product: 'all',
          match_pass: acc.match_pass + row.match_pass,
          match_fail: acc.match_fail + row.match_fail,
          residual_nonempty: acc.residual_nonempty + row.residual_nonempty,
          lint_fail: acc.lint_fail + row.lint_fail,
          validate_fail: acc.validate_fail + row.validate_fail,
          deferred_gaps: acc.deferred_gaps + row.deferred_gaps,
        }),
        {
          product: 'all',
          match_pass: 0,
          match_fail: 0,
          residual_nonempty: 0,
          lint_fail: 0,
          validate_fail: 0,
          deferred_gaps: 0,
        } satisfies QualityMetricsSummary,
      );
    }
    return summaries.find((s) => s.product === productFilter) ?? null;
  }, [productFilter, summaries]);

  const handleSelectStem = (stem: string) => {
    setSelectedStem(stem);
    setDetail(null);
    setDetailError(null);
    setDetailLoading(true);
    onSelectStem?.(stem);
  };

  const handleCloseDetail = () => {
    setSelectedStem(null);
    setDetail(null);
    setDetailError(null);
    setDetailLoading(false);
  };

  return (
    <div
      className="min-h-screen bg-gray-50 p-6 dark:bg-gray-900"
      data-testid="quality-metrics-page"
    >
      <div className="mx-auto max-w-5xl space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            {QUALITY_METRICS_PAGE_TITLE}
          </h1>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Official WMO corpus match, residuals, lint, and validate diagnostics
            {iwxxmPin ? ` · IWXXM ${iwxxmPin}` : ''}
            {generatedAt ? ` · generated ${generatedAt}` : ''}
          </p>
        </div>

        <Card className="p-4">
          <div className="mb-4 flex flex-wrap items-center gap-3">
            <label className="text-sm text-gray-700 dark:text-gray-300">
              Product
              <select
                className="ml-2 rounded border px-2 py-1 text-sm dark:bg-gray-800"
                value={productFilter}
                data-testid="quality-metrics-product-filter"
                aria-label="Filter corpus by product"
                onChange={(e) => setProductFilter(e.target.value)}
              >
                <option value="all">All products</option>
                {productOptions.map((product) => (
                  <option key={product} value={product}>
                    {product.toUpperCase()}
                  </option>
                ))}
              </select>
            </label>
          </div>

          {loading && (
            <div
              className="flex items-center gap-2 text-sm text-gray-500"
              data-testid="quality-metrics-loading"
            >
              <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
              Loading quality metrics…
            </div>
          )}

          {error && (
            <p className="text-sm text-red-600 dark:text-red-400" role="alert">
              {error}
            </p>
          )}

          {!loading && !error && activeSummary && (
            <div
              className="mb-4 grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-6"
              data-testid="quality-metrics-summary"
              aria-label="Quality metrics summary"
            >
              <SummaryStat label="Match pass" value={activeSummary.match_pass} />
              <SummaryStat label="Match fail" value={activeSummary.match_fail} />
              <SummaryStat label="Residuals" value={activeSummary.residual_nonempty} />
              <SummaryStat label="Lint fail" value={activeSummary.lint_fail} />
              <SummaryStat label="Validate fail" value={activeSummary.validate_fail} />
              <SummaryStat label="Deferred gaps" value={activeSummary.deferred_gaps} />
            </div>
          )}

          {!loading && !error && (
            <ul
              className="divide-y divide-gray-200 dark:divide-gray-700"
              data-testid="quality-metrics-file-list"
            >
              {files.length === 0 ? (
                <li className="py-3 text-sm text-gray-500 dark:text-gray-400">
                  No corpus files for this filter.
                </li>
              ) : (
                files.map((row) => {
                  const selected = selectedStem === row.stem;
                  return (
                    <li key={row.stem}>
                      <button
                        type="button"
                        className={`flex w-full flex-wrap items-center justify-between gap-2 px-1 py-3 text-left text-sm ${
                          selected
                            ? 'bg-blue-50 dark:bg-blue-950/40'
                            : 'hover:bg-gray-50 dark:hover:bg-gray-800/60'
                        }`}
                        data-testid={`quality-metrics-row-${row.stem}`}
                        aria-pressed={selected}
                        onClick={() => handleSelectStem(row.stem)}
                      >
                        <div className="min-w-0">
                          <div className="font-medium text-gray-900 dark:text-gray-100">
                            {row.stem}
                          </div>
                          <div className="text-xs text-gray-500 dark:text-gray-400">
                            {row.product.toUpperCase()} · {row.tier} · match{' '}
                            {row.match_status}
                          </div>
                        </div>
                        <div className="flex flex-wrap items-center gap-2 text-xs">
                          {row.deferred ? (
                            <span
                              className="rounded bg-amber-100 px-2 py-0.5 font-medium text-amber-900 dark:bg-amber-950 dark:text-amber-200"
                              data-testid={`quality-metrics-deferred-${row.stem}`}
                            >
                              {QUALITY_METRICS_DEFERRED_LABEL}
                            </span>
                          ) : null}
                          <span className="text-gray-500 dark:text-gray-400">
                            R{row.residual_count} L{row.lint_error_count} V
                            {row.validate_error_count}
                          </span>
                        </div>
                      </button>
                    </li>
                  );
                })
              )}
            </ul>
          )}
        </Card>

        {selectedStem ? (
          <Card className="p-4">
            {detailLoading && (
              <div
                className="flex items-center gap-2 text-sm text-gray-500"
                data-testid="quality-metrics-detail-loading"
              >
                <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
                Loading stem detail…
              </div>
            )}
            {detailError && (
              <p className="text-sm text-red-600 dark:text-red-400" role="alert">
                {detailError}
              </p>
            )}
            {!detailLoading && !detailError && detail ? (
              <QualityMetricsDetail detail={detail} onClose={handleCloseDetail} />
            ) : null}
          </Card>
        ) : null}
      </div>
    </div>
  );
}

function SummaryStat({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-md border border-gray-200 bg-white px-3 py-2 dark:border-gray-700 dark:bg-gray-950">
      <div className="text-xs text-gray-500 dark:text-gray-400">{label}</div>
      <div className="text-lg font-semibold text-gray-900 dark:text-gray-100">
        {value}
      </div>
    </div>
  );
}

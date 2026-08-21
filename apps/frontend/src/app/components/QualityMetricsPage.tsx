/**
 * Quality metrics corpus browser — product filter, summary strip, file list, detail.
 *
 * List + detail for F7.q / EV-054 (AC1–AC5) + EV-056 shareable `/quality/:stem`.
 */

import { useCallback, useEffect, useMemo, useState } from 'react';
import { Loader2 } from 'lucide-react';
import { fetchQualityMetrics, fetchQualityMetricsDetail } from '@/utils/api';
import type {
  QualityMetricsDetailResponse,
  QualityMetricsFileRow,
  QualityMetricsSummary,
} from '@/utils/openapiTypes';
import {
  QUALITY_METRICS_BACK_TO_LIST,
  QualityMetricsDetail,
} from './QualityMetricsDetail';
import { Card } from './ui/card';
import {
  formatMatchStatusLabel,
  QUALITY_METRICS_DEFERRED_LABEL,
  QUALITY_METRICS_DETAIL_LOAD_FAILED,
  QUALITY_METRICS_DETAIL_LOADING,
  QUALITY_METRICS_EMPTY_LIST,
  QUALITY_METRICS_PAGE_SUBTITLE,
  QUALITY_METRICS_PAGE_TITLE,
} from '@/utils/qualityMetricsCopy';

interface QualityMetricsPageProps {
  /** Optional stem select hook (in addition to route navigation). */
  onSelectStem?: (stem: string) => void;
  /** Stem from `/quality/:stem` — when set, show detail-only view. */
  routeStem?: string | null;
  /** Navigate to shareable detail path (list → detail). */
  onOpenDetailRoute?: (stem: string) => void;
  /** Return to list path (`/quality`). */
  onBackToList?: () => void;
}

/**
 * Browse precomputed official-corpus quality metrics by product.
 *
 * @param props.onSelectStem - Optional callback when a file row is activated
 * @param props.routeStem - Active detail stem from the URL
 * @param props.onOpenDetailRoute - Push `/quality/:stem`
 * @param props.onBackToList - Push `/quality`
 */
export function QualityMetricsPage({
  onSelectStem,
  routeStem = null,
  onOpenDetailRoute,
  onBackToList,
}: QualityMetricsPageProps) {
  const [productFilter, setProductFilter] = useState<string>('all');
  const [summaries, setSummaries] = useState<QualityMetricsSummary[]>([]);
  const [files, setFiles] = useState<QualityMetricsFileRow[]>([]);
  const [generatedAt, setGeneratedAt] = useState<string>('');
  const [iwxxmPin, setIwxxmPin] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [localStem, setLocalStem] = useState<string | null>(null);
  const [detail, setDetail] = useState<QualityMetricsDetailResponse | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailError, setDetailError] = useState<string | null>(null);

  const useRoute = typeof onOpenDetailRoute === 'function';
  const selectedStem = useRoute ? routeStem : localStem;

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
            err instanceof Error ? err.message : QUALITY_METRICS_DETAIL_LOAD_FAILED,
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
    onSelectStem?.(stem);
    if (useRoute && onOpenDetailRoute) {
      onOpenDetailRoute(stem);
      return;
    }
    setLocalStem(stem);
    setDetail(null);
    setDetailError(null);
    setDetailLoading(true);
  };

  const handleCloseDetail = () => {
    if (useRoute && onBackToList) {
      onBackToList();
      return;
    }
    setLocalStem(null);
    setDetail(null);
    setDetailError(null);
    setDetailLoading(false);
  };

  const detailOnly = useRoute && Boolean(selectedStem);
  const showInlineDetail = !useRoute && Boolean(selectedStem);

  return (
    <div
      className="min-h-screen bg-gray-50 p-6 dark:bg-gray-900"
      data-testid="quality-metrics-page"
    >
      <div className="mx-auto max-w-5xl space-y-6">
        {!detailOnly ? (
          <>
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                {QUALITY_METRICS_PAGE_TITLE}
              </h1>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {QUALITY_METRICS_PAGE_SUBTITLE}
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
                    aria-label="Filter by product"
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
                  <SummaryStat label="Matches" value={activeSummary.match_pass} />
                  <SummaryStat label="Mismatches" value={activeSummary.match_fail} />
                  <SummaryStat
                    label="With residuals"
                    value={activeSummary.residual_nonempty}
                  />
                  <SummaryStat label="Lint fails" value={activeSummary.lint_fail} />
                  <SummaryStat
                    label="Validation fails"
                    value={activeSummary.validate_fail}
                  />
                  <SummaryStat label="Deferred" value={activeSummary.deferred_gaps} />
                </div>
              )}

              {!loading && !error && (
                <ul
                  className="divide-y divide-gray-200 dark:divide-gray-700"
                  data-testid="quality-metrics-file-list"
                >
                  {files.length === 0 ? (
                    <li className="py-3 text-sm text-gray-500 dark:text-gray-400">
                      {QUALITY_METRICS_EMPTY_LIST}
                    </li>
                  ) : (
                    files.map((row) => (
                      <li key={row.stem}>
                        <button
                          type="button"
                          className="flex w-full flex-wrap items-center justify-between gap-2 px-1 py-3 text-left text-sm hover:bg-gray-50 dark:hover:bg-gray-800/60"
                          data-testid={`quality-metrics-row-${row.stem}`}
                          onClick={() => handleSelectStem(row.stem)}
                        >
                          <div className="min-w-0">
                            <div className="font-medium text-gray-900 dark:text-gray-100">
                              {row.stem}
                            </div>
                            <div className="text-xs text-gray-500 dark:text-gray-400">
                              {row.product.toUpperCase()} · {row.tier} ·{' '}
                              {formatMatchStatusLabel(row.match_status)}
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
                            <span
                              className="text-gray-500 dark:text-gray-400"
                              title="Counts of residuals, lint findings, and validation issues"
                            >
                              Residuals {row.residual_count} · Lint{' '}
                              {row.lint_error_count} · Validation{' '}
                              {row.validate_error_count}
                            </span>
                          </div>
                        </button>
                      </li>
                    ))
                  )}
                </ul>
              )}
            </Card>
          </>
        ) : null}

        {detailOnly ? (
          <Card className="p-4" data-testid="quality-metrics-detail-route">
            {detailLoading && (
              <div
                className="flex items-center gap-2 text-sm text-gray-500"
                data-testid="quality-metrics-detail-loading"
              >
                <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
                {QUALITY_METRICS_DETAIL_LOADING}
              </div>
            )}
            {detailError && (
              <p className="text-sm text-red-600 dark:text-red-400" role="alert">
                {detailError}
              </p>
            )}
            {!detailLoading && !detailError && detail ? (
              <QualityMetricsDetail
                detail={detail}
                onClose={handleCloseDetail}
                closeLabel={QUALITY_METRICS_BACK_TO_LIST}
              />
            ) : null}
          </Card>
        ) : null}

        {showInlineDetail ? (
          <Card className="p-4">
            {detailLoading && (
              <div
                className="flex items-center gap-2 text-sm text-gray-500"
                data-testid="quality-metrics-detail-loading"
              >
                <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
                {QUALITY_METRICS_DETAIL_LOADING}
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

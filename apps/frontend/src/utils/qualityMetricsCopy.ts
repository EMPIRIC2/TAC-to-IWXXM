/**
 * Operator-visible Quality metrics copy (plain language; no planning ids).
 *
 * [Corpus: product §F7.q] [Corpus: product §F7] — EV-048 / EV-056.
 */

/** Operator-visible label for deferred / unscored files (AC5). */
export const QUALITY_METRICS_DEFERRED_LABEL = 'Deferred — not scored yet';

/** Page title — primary shell tab. */
export const QUALITY_METRICS_PAGE_TITLE = 'Quality metrics';

/** Page subtitle — plain-language purpose. */
export const QUALITY_METRICS_PAGE_SUBTITLE =
  'Compare our converted IWXXM to official WMO examples. See match status, leftover TAC (residuals), lint findings, and validation results.';

/** Empty list when the product filter has no rows. */
export const QUALITY_METRICS_EMPTY_LIST = 'No files for this product filter.';

/** Detail load fallback error (non-Error throws). */
export const QUALITY_METRICS_DETAIL_LOAD_FAILED = 'Failed to load file detail';

/** Detail loading indicator. */
export const QUALITY_METRICS_DETAIL_LOADING = 'Loading file detail…';

/**
 * Plain-language match status for list/detail headers.
 *
 * @param status - API `match_status` value
 * @returns Operator-visible label
 */
export function formatMatchStatusLabel(status: string): string {
  switch (status) {
    case 'equal':
      return 'Matches official';
    case 'unequal':
      return 'Differs from official';
    case 'deferred':
      return QUALITY_METRICS_DEFERRED_LABEL;
    default:
      return status;
  }
}

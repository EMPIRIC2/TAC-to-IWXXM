/**
 * Enrich Conversion / validation log Note rows when the wire issue has no hint.
 *
 * Prefer an explicit issue hint (UNKNOWN_ICAO pattern). Otherwise derive a
 * plain-language reason/consequence line from the loaded lint catalog template,
 * with small fallbacks for known sparse codes when the catalog is unavailable.
 */

import type { LintIssueCatalogEntry } from '@/utils/api';
import { scrubInternalDocRefs } from '@/utils/internalDocRefGuard';

/** Wire fields needed to resolve a log hint. */
export type ConversionLogIssueLike = {
  code?: string | null;
  message?: string | null;
  hint?: string | null;
};

/**
 * Plain-language fallbacks when catalog copy is not loaded.
 * Keep free of planning ids. [Corpus: ui-style] [Corpus: product §F7]
 */
const SPARSE_LOG_HINT_FALLBACKS: Readonly<Record<string, string>> = {
  RVR_PRESENT:
    'RVR means Runway Visual Range — how far a pilot can see along the runway. ' +
    'This note flags that one or more RVR groups appear in the TAC (Traditional Alphanumeric Code); ' +
    'conversion continues and does not by itself block IWXXM output.',
  NSW_PRESENT:
    'NSW means No Significant Weather (nil significant weather). ' +
    'This note flags that NSW appears in the report; it is informational for operator awareness ' +
    'and does not by itself block conversion to IWXXM.',
};

const PRODUCT_TOKEN = /\b(METAR|SPECI|TAF|SIGMET|AIRMET|VAA|TCA|SWXA|VONA)\b/i;

/**
 * Guess the product word from the short issue title for `{product}` fill.
 *
 * @param message - Issue title from the convert/lint response
 * @returns Product token or a generic subject
 * @example
 * const _ = true;
 */
export function productLabelFromIssueMessage(
  message: string | null | undefined,
): string {
  const match = (message ?? '').match(PRODUCT_TOKEN);
  return match?.[1]?.toUpperCase() ?? 'This report';
}

/**
 * Turn a catalog message_template into a compact log reason/consequence line.
 *
 * Strips paywall/source tails and fills `{product}` / leftover `{…}` placeholders.
 *
 * @param template - Catalog `message_template`
 * @param productLabel - Subject for `{product}` (e.g. METAR)
 * @returns Scrubbed operator hint, or empty when nothing useful remains
 * @example
 * const _ = true;
 */
export function catalogTemplateToLogHint(
  template: string,
  productLabel: string,
): string {
  let text = scrubInternalDocRefs(template.trim());
  if (!text) {
    return '';
  }
  text = text.replace(/\s*Source:\s*.*$/i, '');
  text = text.replace(/\s*Full normative text may require purchase\.?/gi, '');
  text = text.replace(/\{product\}/gi, productLabel);
  text = text
    .replace(/\{[^}]+\}/g, '')
    .replace(/\s{2,}/g, ' ')
    .trim();
  text = text.replace(/^Informational:\s*/i, '');
  return scrubInternalDocRefs(text).trim();
}

/**
 * Resolve the secondary sentence under a Conversion / validation log Note title.
 *
 * @param issue - Wire issue (message / hint / code)
 * @param catalog - Optional catalog row for the issue code
 * @returns Display hint, or null when none can be derived
 * @example
 * const _ = true;
 */
export function resolveConversionLogHint(
  issue: ConversionLogIssueLike,
  catalog?: LintIssueCatalogEntry | null,
): string | null {
  const explicit = scrubInternalDocRefs((issue.hint ?? '').trim());
  if (explicit) {
    return explicit;
  }

  const productLabel = productLabelFromIssueMessage(issue.message);
  const fromCatalog = catalogTemplateToLogHint(
    catalog?.message_template ?? '',
    productLabel,
  );
  if (fromCatalog) {
    return fromCatalog;
  }

  const code = (issue.code ?? '').trim();
  const fallback = SPARSE_LOG_HINT_FALLBACKS[code];
  if (fallback) {
    return fallback;
  }
  return null;
}

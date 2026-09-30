/**
 * Lint issue catalog helpers for workbench tooltips and panel copy (F15 / F20 / F23).
 *
 * F15 / E11-29 / E11-31: tooltip resolver. F20 / E15-14: tag filter + list copy.
 * F23 / E19-17: same helpers cover ``sigmet`` / ``va`` tags (additive).
 */

import type { LintIssueCatalogEntry } from './api';

/**
 * Index catalog rows by stable public code.
 *
 * @param entries - Catalog rows from GET /lint-issue-catalog
 * @returns Map keyed by ``code``
 * @example
 * const _ = true;
 */
export function indexCatalogByCode(
  entries: LintIssueCatalogEntry[],
): Map<string, LintIssueCatalogEntry> {
  const map = new Map<string, LintIssueCatalogEntry>();
  for (const entry of entries) {
    if (entry.code) {
      map.set(entry.code, entry);
    }
  }
  return map;
}

/**
 * Resolve a tooltip string for a lint issue code from the catalog.
 *
 * Returns ``severity: message_template`` when known; otherwise a fallback that
 * still names the code (never silent empty).
 *
 * @param byCode - Index from {@link indexCatalogByCode}
 * @param code - Public SCREAMING_SNAKE issue code
 * @returns Tooltip text for the console code chip
 * @example
 * const _ = true;
 */
export function resolveLintIssueTooltip(
  byCode: Map<string, LintIssueCatalogEntry>,
  code: string,
): string {
  const entry = byCode.get(code);
  if (!entry) {
    return `${code} (not in loaded catalog)`;
  }
  return `${entry.severity}: ${entry.message_template}`;
}

/**
 * Keep catalog rows whose ``tags`` include ``tag`` (case-insensitive).
 *
 * Empty or whitespace-only ``tag`` returns all rows (no filter).
 *
 * @param entries - Full catalog list
 * @param tag - Tag to match (e.g. ``taf``); empty = all
 * @returns Filtered rows in original order
 * @example
 * const _ = true;
 */
export function filterCatalogByTag(
  entries: LintIssueCatalogEntry[],
  tag: string,
): LintIssueCatalogEntry[] {
  const needle = tag.trim().toLowerCase();
  if (!needle) {
    return entries;
  }
  return entries.filter((entry) =>
    (entry.tags ?? []).some((t) => t.toLowerCase() === needle),
  );
}

/**
 * Format a catalog row for the lightweight panel list (code, severity, tags,
 * and ``product:`` when the registry sets a product).
 *
 * @param entry - Single catalog row
 * @returns One-line operator-facing copy
 * @example
 * const _ = true;
 */
export function formatCatalogEntryCopy(entry: LintIssueCatalogEntry): string {
  const parts = [`${entry.code} (${entry.severity})`];
  const tags = (entry.tags ?? []).join(', ');
  if (tags) {
    parts.push(`tags: ${tags}`);
  }
  if (entry.product) {
    parts.push(`product: ${entry.product}`);
  }
  if (entry.source_attribution) {
    parts.push(`source: ${entry.source_attribution}`);
  } else if (entry.source_id) {
    const url = entry.source_url ? ` (${entry.source_url})` : '';
    parts.push(`source: ${entry.source_id}${url}`);
  }
  return parts.join(' ');
}

/**
 * Map a catalog row family to Rule catalogs shell filter values.
 */
export function catalogShellFamilyForCode(
  entry: Pick<LintIssueCatalogEntry, 'family'> | undefined,
): 'lint' | 'iwxxm' | undefined {
  const familyRaw = entry?.family;
  return familyRaw === 'iwxxm' || familyRaw === 'lint' ? familyRaw : undefined;
}

/**
 * Open Rule catalogs focused on a console lint/validation code.
 */
export function openCatalogForLintCode(
  onOpenCatalog: (
    family?: 'conversion' | 'lint' | 'iwxxm' | 'decoding',
    code?: string,
  ) => void,
  catalogByCode: Map<string, LintIssueCatalogEntry>,
  code: string,
): void {
  onOpenCatalog(catalogShellFamilyForCode(catalogByCode.get(code)), code);
}

/**
 * No-op when the shell does not provide an open-catalog handler.
 */
export function maybeOpenCatalogForLintCode(
  onOpenCatalog:
    | ((family?: 'conversion' | 'lint' | 'iwxxm' | 'decoding', code?: string) => void)
    | undefined,
  catalogByCode: Map<string, LintIssueCatalogEntry>,
  code: string,
): void {
  if (!onOpenCatalog) {
    return;
  }
  openCatalogForLintCode(onOpenCatalog, catalogByCode, code);
}

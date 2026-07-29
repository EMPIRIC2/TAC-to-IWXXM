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
  return parts.join(' ');
}

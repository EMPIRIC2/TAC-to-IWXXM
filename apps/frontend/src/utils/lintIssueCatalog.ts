/**
 * Lint issue catalog helpers for workbench tooltips (F15 / E11-29 / E11-31).
 */

import type { LintIssueCatalogEntry } from './api';

/**
 * Index catalog rows by stable public code.
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

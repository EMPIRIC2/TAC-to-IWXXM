/* eslint-disable complexity */
/**
 * Top-level Validation Issues Catalog page — code, type, level, description, source links.
 *
 * Consumes GET /lint-issue-catalog (additive family + source fields). Peer shell tab
 * for F7.v / #1014; distinct from the workbench browse panel.
 */

import type { LintIssueCatalogEntry } from '@/utils/openapiTypes';

type FamilyFilter =
  | 'all'
  | 'lint'
  | 'iwxxm'
  | 'conversion'
  | 'dissemination'
  | 'decoding';
/**
 * Type `SortKey`.
 * @example
 * const _ = true;
 */
export type SortKey = 'code' | 'level' | 'family' | 'issue_type' | 'source_access';

/** Level filter values for the catalog page. */
export const LEVEL_OPTIONS = ['all', 'critical', 'error', 'warning', 'info'] as const;

/** Source-access filter values. */
export const ACCESS_OPTIONS = [
  'all',
  'public',
  'paywall',
  'login',
  'semantic_only',
] as const;

/** EV-062 type filter set (TAC / IWXXM / Decoding). */
/**
 * EV062_TYPE_OPTIONS.
 */
export const EV062_TYPE_OPTIONS = [
  'all',
  'presence',
  'structure',
  'content',
  'consistency',
  'iwxxm_schema',
  'other',
] as const;

/** Conversion family type filter (D-REQ-05). */
/**
 * CONVERSION_TYPE_OPTIONS.
 */
export const CONVERSION_TYPE_OPTIONS = ['all', 'profile', 'policy', 'other'] as const;

/** Dissemination family type filter. Exchange rows ship as ``profile``. */
/**
 * DISSEMINATION_TYPE_OPTIONS.
 */
export const DISSEMINATION_TYPE_OPTIONS = ['all', 'profile', 'other'] as const;

/**
 * Type options for Family=All: EV-062 ∪ {profile, policy} (D-TP-03).
 * ``other`` already in EV-062.
 */
/**
 * ALL_FAMILY_TYPE_OPTIONS.
 */
export const ALL_FAMILY_TYPE_OPTIONS = [
  'all',
  'presence',
  'structure',
  'content',
  'consistency',
  'iwxxm_schema',
  'profile',
  'policy',
  'other',
] as const;

/**
 * Family-aware catalog type filter options.
 *
 * @param family - Active family filter
 * @returns Option values including ``all``
 * @example
 * const _ = true;
 */
/**
 * typeOptionsForFamily.
 * @example
 * const _ = true;
 */
export function typeOptionsForFamily(family: FamilyFilter): readonly string[] {
  if (family === 'conversion') {
    return CONVERSION_TYPE_OPTIONS;
  }
  if (family === 'dissemination') {
    return DISSEMINATION_TYPE_OPTIONS;
  }
  if (family === 'all') {
    return ALL_FAMILY_TYPE_OPTIONS;
  }
  // lint / iwxxm / decoding — TAC/IWXXM type list
  return EV062_TYPE_OPTIONS;
}

/** Sort control options for the catalog table. */
export const SORT_OPTIONS: { value: SortKey; label: string }[] = [
  { value: 'code', label: 'Code' },
  { value: 'level', label: 'Level' },
  { value: 'family', label: 'Family' },
  { value: 'issue_type', label: 'Type' },
  { value: 'source_access', label: 'Access' },
];

const LEVEL_RANK: Record<string, number> = {
  critical: 0,
  error: 1,
  warning: 2,
  info: 3,
};

/**
 * Whether an operator source URL should be rendered as a clickable link.
 *
 * @param entry - Catalog row
 * @returns True when status is verified and URL is http(s)
 * @example
 * const _ = true;
 */
export function isClickableSource(entry: LintIssueCatalogEntry): boolean {
  const url = entry.source_url;
  if (!url || typeof url !== 'string') {
    return false;
  }
  if (entry.status && entry.status !== 'verified') {
    return false;
  }
  return /^https?:\/\//i.test(url);
}

/**
 * Read a sortable string field from a catalog row (non-level sorts).
 * @example
 * const _ = true;
 */
export function sortFieldValue(entry: LintIssueCatalogEntry, sortBy: SortKey): string {
  switch (sortBy) {
    case 'family':
      return entry.family || '';
    case 'issue_type':
      return entry.issue_type || '';
    case 'source_access':
      return entry.source_access || '';
    case 'code':
    case 'level':
    default:
      return entry.code || '';
  }
}

/**
 * Compare catalog rows for client-side sort.
 * @example
 * const _ = true;
 */
/**
 * compareEntries.
 * @example
 * const _ = true;
 */
export function compareEntries(
  a: LintIssueCatalogEntry,
  b: LintIssueCatalogEntry,
  sortBy: SortKey,
): number {
  if (sortBy === 'level') {
    const rankA = LEVEL_RANK[(a.severity || '').toLowerCase()] ?? 99;
    const rankB = LEVEL_RANK[(b.severity || '').toLowerCase()] ?? 99;
    if (rankA !== rankB) {
      return rankA - rankB;
    }
    return (a.code || '').localeCompare(b.code || '', undefined, {
      sensitivity: 'base',
    });
  }
  const cmp = sortFieldValue(a, sortBy).localeCompare(
    sortFieldValue(b, sortBy),
    undefined,
    {
      sensitivity: 'base',
    },
  );
  if (cmp !== 0) {
    return cmp;
  }
  return (a.code || '').localeCompare(b.code || '', undefined, { sensitivity: 'base' });
}

/**
 * Whether a catalog row matches the selected level filter.
 * Missing severity is not treated as info.
 * @example
 * const _ = true;
 */
/**
 * entryMatchesLevelFilter.
 * @example
 * const _ = true;
 */
export function entryMatchesLevelFilter(
  entry: LintIssueCatalogEntry,
  levelKey: string | null,
): boolean {
  if (!levelKey) {
    return true;
  }
  const severity = (entry.severity || '').toLowerCase();
  return severity.length > 0 && severity === levelKey;
}

/**
 * Whether a catalog row matches the selected type filter.
 * Missing type is not treated as other.
 * @example
 * const _ = true;
 */
/**
 * entryMatchesTypeFilter.
 * @example
 * const _ = true;
 */
export function entryMatchesTypeFilter(
  entry: LintIssueCatalogEntry,
  typeKey: string | null,
): boolean {
  if (!typeKey) {
    return true;
  }
  const issueType = (entry.issue_type || '').toLowerCase();
  return issueType.length > 0 && issueType === typeKey;
}

/**
 * Whether a catalog row matches the selected access filter.
 * Missing access is not treated as public.
 * @example
 * const _ = true;
 */
/**
 * entryMatchesAccessFilter.
 * @example
 * const _ = true;
 */
export function entryMatchesAccessFilter(
  entry: LintIssueCatalogEntry,
  accessKey: string | null,
): boolean {
  if (!accessKey) {
    return true;
  }
  const access = (entry.source_access || '').toLowerCase();
  return access.length > 0 && access === accessKey;
}

type RuleCatalogItemLike = {
  id: string;
  title: string;
  summary?: string | null;
  severity?: string | null;
  tags?: string[] | null;
  issue_type?: string | null;
  source_url?: string | null;
  source_attribution?: string | null;
  source_access?: string | null;
  source_locator?: string | null;
  conform_note?: string | null;
};

/**
 * Map a rule-catalog API row without inventing type, access, or severity.
 *
 * @param item - GET /rule-catalogs item
 * @param family - Active family filter (conversion | dissemination | decoding)
 * @returns Row shaped for the shared catalog table
 * @example
 * const _ = true;
 */
/**
 * mapRuleCatalogItem.
 * @example
 * const _ = true;
 */
export function mapRuleCatalogItem(
  item: RuleCatalogItemLike,
  family: 'conversion' | 'dissemination' | 'decoding',
): LintIssueCatalogEntry {
  const severityRaw = typeof item.severity === 'string' ? item.severity.trim() : '';
  const summary =
    typeof item.summary === 'string' && item.summary.trim() ? item.summary.trim() : '';
  const conform =
    typeof item.conform_note === 'string' && item.conform_note.trim()
      ? item.conform_note.trim()
      : '';
  const descriptionParts = [summary || item.title, conform].filter(
    (part) => typeof part === 'string' && part.length > 0,
  );
  const issueType =
    typeof item.issue_type === 'string' && item.issue_type.trim()
      ? item.issue_type.trim()
      : null;
  const sourceUrl =
    typeof item.source_url === 'string' && item.source_url.trim()
      ? item.source_url.trim()
      : null;
  const sourceAttribution =
    typeof item.source_attribution === 'string' && item.source_attribution.trim()
      ? item.source_attribution.trim()
      : null;
  const sourceAccess =
    typeof item.source_access === 'string' && item.source_access.trim()
      ? item.source_access.trim()
      : null;
  const sourceLocator =
    typeof item.source_locator === 'string' && item.source_locator.trim()
      ? item.source_locator.trim()
      : null;
  return {
    code: item.id,
    // Empty string = severity absent (do not invent "info").
    severity: severityRaw,
    message_template: descriptionParts.join(' '),
    product: null,
    tags: item.tags ?? [],
    family,
    source_id: null,
    source_url: sourceUrl,
    source_attribution: sourceAttribution,
    source_type: null,
    // Leave status null so TAC/IWXXM click rules stay unchanged (TC-EV1308-004).
    status: null,
    semantic_identifier: null,
    last_verified: null,
    replacement_url: null,
    issue_type: issueType,
    source_access: sourceAccess,
    source_locator: sourceLocator,
  };
}

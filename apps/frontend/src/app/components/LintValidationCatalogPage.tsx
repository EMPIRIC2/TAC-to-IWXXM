/* eslint-disable react-refresh/only-export-components */
/**
 * Top-level Validation Issues Catalog page — code, type, level, description, source links.
 *
 * Consumes GET /lint-issue-catalog (additive family + source fields). Peer shell tab
 * for F7.v / #1014; distinct from the workbench browse panel.
 */

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { Loader2 } from 'lucide-react';
import { fetchLintIssueCatalog, fetchRuleCatalog } from '@/utils/api';
import type { LintIssueCatalogEntry } from '@/utils/openapiTypes';
import { Card } from './ui/card';
import {
  LINT_VALIDATION_CATALOG_ACCESS_LABEL,
  LINT_VALIDATION_CATALOG_COL_CODE,
  LINT_VALIDATION_CATALOG_COL_DESCRIPTION,
  LINT_VALIDATION_CATALOG_COL_LEVEL,
  LINT_VALIDATION_CATALOG_COL_PROFILES,
  LINT_VALIDATION_CATALOG_COL_SOURCE,
  LINT_VALIDATION_CATALOG_COL_TYPE,
  LINT_VALIDATION_CATALOG_EMPTY,
  LINT_VALIDATION_CATALOG_EXCHANGE_ALL,
  LINT_VALIDATION_CATALOG_EXCHANGE_LABEL,
  LINT_VALIDATION_CATALOG_LISTED_PROFILE_ONLY,
  LINT_VALIDATION_CATALOG_FAMILY_LABEL,
  LINT_VALIDATION_CATALOG_LEVEL_LABEL,
  LINT_VALIDATION_CATALOG_LOADING,
  LINT_VALIDATION_CATALOG_PAGE_SUBTITLE,
  LINT_VALIDATION_CATALOG_PAGE_TITLE,
  LINT_VALIDATION_CATALOG_PROFILE_ALL,
  LINT_VALIDATION_CATALOG_PROFILE_LABEL,
  LINT_VALIDATION_CATALOG_SORT_LABEL,
  LINT_VALIDATION_CATALOG_TYPE_LABEL,
} from '@/utils/lintValidationCatalogCopy';
import { SEMANTIC_PROFILE_OPTIONS, type IwxxmProfile } from '@/utils/semanticProfile';
import {
  EXCHANGE_PROFILE_OPTIONS,
  type ExchangeProfileId,
} from '@/utils/exchangeProfile';

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

const LEVEL_OPTIONS = ['all', 'critical', 'error', 'warning', 'info'] as const;

/** EV-062 type filter set (TAC / IWXXM / Decoding). */
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
export const CONVERSION_TYPE_OPTIONS = ['all', 'profile', 'policy', 'other'] as const;

/** Dissemination family type filter. Exchange rows ship as ``profile``. */
export const DISSEMINATION_TYPE_OPTIONS = ['all', 'profile', 'other'] as const;

/**
 * Type options for Family=All: EV-062 ∪ {profile, policy} (D-TP-03).
 * ``other`` already in EV-062.
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

const ACCESS_OPTIONS = ['all', 'public', 'paywall', 'login', 'semantic_only'] as const;
const SORT_OPTIONS: { value: SortKey; label: string }[] = [
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
 */
function isClickableSource(entry: LintIssueCatalogEntry): boolean {
  const url = entry.source_url;
  if (!url || typeof url !== 'string') {
    return false;
  }
  if (entry.status && entry.status !== 'verified') {
    return false;
  }
  return url.startsWith('http://') || url.startsWith('https://');
}

/**
 * Function `profileList`.
 */
function profileList(value: string[] | null | undefined): string[] {
  if (!Array.isArray(value)) {
    return [];
  }
  return value.filter(
    (item): item is string => typeof item === 'string' && item.trim().length > 0,
  );
}

/**
 * Human-readable semantic/exchange profile lists for a catalog entry.
 *
 * @param entry - Lint issue catalog row
 * @returns Display strings (comma-joined or “All … profiles”)
 * @example
 * const _ = true;
 */
export function formatApplicableProfiles(entry: LintIssueCatalogEntry): {
  semantic: string;
  exchange: string;
} {
  const semantic = profileList(entry.semantic_profiles);
  const exchange = profileList(entry.exchange_profiles);
  return {
    semantic: semantic.length > 0 ? semantic.join(', ') : 'All semantic profiles',
    exchange: exchange.length > 0 ? exchange.join(', ') : 'All exchange profiles',
  };
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
 * When listed-only is on and a profile axis is selected, require a non-empty
 * applicability list on that axis (empty = unrestricted / all profiles).
 *
 * @example
 * const _ = true;
 */
export function entryMatchesListedProfileFilter(
  entry: LintIssueCatalogEntry,
  options: {
    listedOnly: boolean;
    semanticSelected: boolean;
    exchangeSelected: boolean;
  },
): boolean {
  const { listedOnly, semanticSelected, exchangeSelected } = options;
  if (!listedOnly || (!semanticSelected && !exchangeSelected)) {
    return true;
  }
  if (semanticSelected && profileList(entry.semantic_profiles).length === 0) {
    return false;
  }
  if (exchangeSelected && profileList(entry.exchange_profiles).length === 0) {
    return false;
  }
  return true;
}

/**
 * Whether a catalog row matches the selected access filter.
 * Missing access is not treated as public.
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

/**
 * Browse TAC lint and IWXXM validation catalog rows from the public API.
 * @example
 * const _ = true;
 */
export function LintValidationCatalogPage({
  focusCode,
  initialFamily,
  onFocusHandled,
}: {
  focusCode?: string;
  initialFamily?: 'lint' | 'iwxxm';
  onFocusHandled?: () => void;
} = {}) {
  const [familyFilter, setFamilyFilter] = useState<FamilyFilter>(
    initialFamily ?? 'all',
  );
  const [issueTypeFilter, setIssueTypeFilter] = useState<string>('all');
  const [levelFilter, setLevelFilter] = useState<(typeof LEVEL_OPTIONS)[number]>('all');
  const [sourceAccessFilter, setSourceAccessFilter] =
    useState<(typeof ACCESS_OPTIONS)[number]>('all');
  const [semanticProfileFilter, setSemanticProfileFilter] = useState<
    'all' | IwxxmProfile
  >('all');
  const [exchangeProfileFilter, setExchangeProfileFilter] = useState<
    'all' | ExchangeProfileId
  >('all');
  const [listedProfileOnly, setListedProfileOnly] = useState(false);
  const [sortBy, setSortBy] = useState<SortKey>('code');
  const [entries, setEntries] = useState<LintIssueCatalogEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [highlightedCode, setHighlightedCode] = useState<string | null>(null);
  const focusHandledRef = useRef<string | null>(null);

  const typeOptions = useMemo(() => typeOptionsForFamily(familyFilter), [familyFilter]);

  const usesLintIssueCatalog =
    familyFilter === 'all' || familyFilter === 'lint' || familyFilter === 'iwxxm';

  const loadCatalog = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      if (
        familyFilter === 'conversion' ||
        familyFilter === 'dissemination' ||
        familyFilter === 'decoding'
      ) {
        const response = await fetchRuleCatalog({ family: familyFilter });
        const mapped = (response.items ?? []).map((item) =>
          mapRuleCatalogItem(item, familyFilter),
        );
        setEntries(mapped);
        return;
      }
      const params: {
        family?: string;
        issue_type?: string;
        source_access?: string;
        semantic_profile?: string;
        exchange_profile?: string;
      } = {};
      if (familyFilter !== 'all') {
        params.family = familyFilter;
      }
      if (issueTypeFilter !== 'all') {
        params.issue_type = issueTypeFilter;
      }
      if (sourceAccessFilter !== 'all') {
        params.source_access = sourceAccessFilter;
      }
      if (semanticProfileFilter !== 'all') {
        params.semantic_profile = semanticProfileFilter;
      }
      if (exchangeProfileFilter !== 'all') {
        params.exchange_profile = exchangeProfileFilter;
      }
      const response = await fetchLintIssueCatalog(params);
      setEntries(response.issues ?? []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load catalog');
      setEntries([]);
    } finally {
      setLoading(false);
    }
  }, [
    familyFilter,
    issueTypeFilter,
    sourceAccessFilter,
    semanticProfileFilter,
    exchangeProfileFilter,
  ]);

  /* eslint-disable react-hooks/set-state-in-effect -- refetch when filters change */
  useEffect(() => {
    void loadCatalog();
  }, [loadCatalog]);
  /* eslint-enable react-hooks/set-state-in-effect */

  const sorted = useMemo(() => {
    const levelKey = levelFilter === 'all' ? null : levelFilter;
    const typeKey = issueTypeFilter === 'all' ? null : issueTypeFilter;
    const accessKey = sourceAccessFilter === 'all' ? null : sourceAccessFilter;
    const semanticSelected = semanticProfileFilter !== 'all';
    const exchangeSelected = exchangeProfileFilter !== 'all';
    const filtered = entries.filter(
      (entry) =>
        entryMatchesLevelFilter(entry, levelKey) &&
        entryMatchesTypeFilter(entry, typeKey) &&
        entryMatchesAccessFilter(entry, accessKey) &&
        entryMatchesListedProfileFilter(entry, {
          listedOnly: listedProfileOnly,
          semanticSelected,
          exchangeSelected,
        }),
    );
    return [...filtered].sort((a, b) => compareEntries(a, b, sortBy));
  }, [
    entries,
    levelFilter,
    issueTypeFilter,
    sourceAccessFilter,
    listedProfileOnly,
    semanticProfileFilter,
    exchangeProfileFilter,
    sortBy,
  ]);

  /* eslint-disable react-hooks/set-state-in-effect -- scroll/highlight focus target from shell deep-link */
  useEffect(() => {
    if (!focusCode || loading) {
      return;
    }
    if (focusHandledRef.current === focusCode) {
      return;
    }
    const el = document.querySelector(
      `[data-testid="lint-validation-catalog-entry-${focusCode}"]`,
    );
    if (el instanceof HTMLElement) {
      el.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
      setHighlightedCode(focusCode);
      focusHandledRef.current = focusCode;
      onFocusHandled?.();
      return undefined;
    }
    focusHandledRef.current = focusCode;
    onFocusHandled?.();
    return undefined;
  }, [focusCode, loading, sorted, onFocusHandled]);
  /* eslint-enable react-hooks/set-state-in-effect */

  return (
    <div
      className="min-h-screen bg-gray-50 p-6 dark:bg-gray-900"
      data-testid="lint-validation-catalog-page"
    >
      <div className="mx-auto max-w-6xl space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            {LINT_VALIDATION_CATALOG_PAGE_TITLE}
          </h1>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            {LINT_VALIDATION_CATALOG_PAGE_SUBTITLE}
          </p>
        </div>

        <Card className="p-4">
          <div className="mb-4 flex flex-wrap items-center gap-3">
            <label className="text-sm text-gray-700 dark:text-gray-300">
              {LINT_VALIDATION_CATALOG_FAMILY_LABEL}
              <select
                className="ml-2 rounded border px-2 py-1 text-sm dark:bg-gray-800"
                value={familyFilter}
                data-testid="lint-validation-catalog-family-filter"
                aria-label="Filter by family"
                onChange={(e) => {
                  const next = e.target.value as FamilyFilter;
                  setFamilyFilter(next);
                  const nextTypes = typeOptionsForFamily(next);
                  if (!nextTypes.includes(issueTypeFilter)) {
                    setIssueTypeFilter('all');
                  }
                }}
              >
                <option value="all">All lint / IWXXM</option>
                <option value="lint">TAC validation</option>
                <option value="iwxxm">IWXXM validation</option>
                <option value="conversion">Conversion</option>
                <option value="dissemination">Dissemination</option>
                <option value="decoding">Decoding</option>
              </select>
            </label>
            <label className="text-sm text-gray-700 dark:text-gray-300">
              {LINT_VALIDATION_CATALOG_TYPE_LABEL}
              <select
                className="ml-2 rounded border px-2 py-1 text-sm dark:bg-gray-800"
                value={issueTypeFilter}
                data-testid="lint-validation-catalog-type-filter"
                aria-label="Filter by type"
                onChange={(e) => setIssueTypeFilter(e.target.value)}
              >
                {typeOptions.map((opt) => (
                  <option key={opt} value={opt}>
                    {opt === 'all' ? 'All' : opt.replace('_', ' ')}
                  </option>
                ))}
              </select>
            </label>
            <label className="text-sm text-gray-700 dark:text-gray-300">
              {LINT_VALIDATION_CATALOG_LEVEL_LABEL}
              <select
                className="ml-2 rounded border px-2 py-1 text-sm dark:bg-gray-800"
                value={levelFilter}
                data-testid="lint-validation-catalog-level-filter"
                aria-label="Filter by level"
                onChange={(e) =>
                  setLevelFilter(e.target.value as (typeof LEVEL_OPTIONS)[number])
                }
              >
                {LEVEL_OPTIONS.map((opt) => (
                  <option key={opt} value={opt}>
                    {opt === 'all' ? 'All' : opt}
                  </option>
                ))}
              </select>
            </label>
            <label className="text-sm text-gray-700 dark:text-gray-300">
              {LINT_VALIDATION_CATALOG_ACCESS_LABEL}
              <select
                className="ml-2 rounded border px-2 py-1 text-sm dark:bg-gray-800"
                value={sourceAccessFilter}
                data-testid="lint-validation-catalog-access-filter"
                aria-label="Filter by source access"
                onChange={(e) =>
                  setSourceAccessFilter(
                    e.target.value as (typeof ACCESS_OPTIONS)[number],
                  )
                }
              >
                {ACCESS_OPTIONS.map((opt) => (
                  <option key={opt} value={opt}>
                    {opt === 'all' ? 'All' : opt.replace('_', ' ')}
                  </option>
                ))}
              </select>
            </label>
            <label className="text-sm text-gray-700 dark:text-gray-300">
              {LINT_VALIDATION_CATALOG_PROFILE_LABEL}
              <select
                className="ml-2 rounded border px-2 py-1 text-sm dark:bg-gray-800"
                value={semanticProfileFilter}
                data-testid="lint-validation-catalog-profile-filter"
                aria-label="Filter by profile"
                disabled={!usesLintIssueCatalog}
                onChange={(e) =>
                  setSemanticProfileFilter(
                    e.target.value === 'all' ? 'all' : (e.target.value as IwxxmProfile),
                  )
                }
              >
                <option value="all">{LINT_VALIDATION_CATALOG_PROFILE_ALL}</option>
                {SEMANTIC_PROFILE_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </label>
            <label className="text-sm text-gray-700 dark:text-gray-300">
              {LINT_VALIDATION_CATALOG_EXCHANGE_LABEL}
              <select
                className="ml-2 rounded border px-2 py-1 text-sm dark:bg-gray-800"
                value={exchangeProfileFilter}
                data-testid="lint-validation-catalog-exchange-filter"
                aria-label="Filter by exchange profile"
                disabled={!usesLintIssueCatalog}
                onChange={(e) =>
                  setExchangeProfileFilter(
                    e.target.value === 'all'
                      ? 'all'
                      : (e.target.value as ExchangeProfileId),
                  )
                }
              >
                <option value="all">{LINT_VALIDATION_CATALOG_EXCHANGE_ALL}</option>
                {EXCHANGE_PROFILE_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </label>
            <label className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
              <input
                type="checkbox"
                className="rounded border"
                checked={listedProfileOnly}
                disabled={!usesLintIssueCatalog}
                data-testid="lint-validation-catalog-listed-profile-only"
                aria-label={LINT_VALIDATION_CATALOG_LISTED_PROFILE_ONLY}
                onChange={(e) => setListedProfileOnly(e.target.checked)}
              />
              {LINT_VALIDATION_CATALOG_LISTED_PROFILE_ONLY}
            </label>
            <label className="text-sm text-gray-700 dark:text-gray-300">
              {LINT_VALIDATION_CATALOG_SORT_LABEL}
              <select
                className="ml-2 rounded border px-2 py-1 text-sm dark:bg-gray-800"
                value={sortBy}
                data-testid="lint-validation-catalog-sort"
                aria-label="Sort catalog rows"
                onChange={(e) => setSortBy(e.target.value as SortKey)}
              >
                {SORT_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </label>
          </div>

          {loading && (
            <div
              className="flex items-center gap-2 text-sm text-gray-500"
              data-testid="lint-validation-catalog-loading"
            >
              <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
              {LINT_VALIDATION_CATALOG_LOADING}
            </div>
          )}

          {error && (
            <p className="text-sm text-red-600 dark:text-red-400" role="alert">
              {error}
            </p>
          )}

          {!loading && !error && (
            <div className="overflow-x-auto" data-testid="lint-validation-catalog-list">
              {sorted.length === 0 ? (
                <p className="py-3 text-sm text-gray-500 dark:text-gray-400">
                  {LINT_VALIDATION_CATALOG_EMPTY}
                </p>
              ) : (
                <table className="w-full min-w-[48rem] border-collapse text-left text-sm">
                  <thead>
                    <tr className="border-b border-gray-200 text-gray-600 dark:border-gray-700 dark:text-gray-300">
                      <th className="px-2 py-2 font-medium">
                        {LINT_VALIDATION_CATALOG_COL_CODE}
                      </th>
                      <th className="px-2 py-2 font-medium">
                        {LINT_VALIDATION_CATALOG_COL_TYPE}
                      </th>
                      <th className="px-2 py-2 font-medium">
                        {LINT_VALIDATION_CATALOG_COL_LEVEL}
                      </th>
                      <th className="px-2 py-2 font-medium">
                        {LINT_VALIDATION_CATALOG_COL_PROFILES}
                      </th>
                      <th className="px-2 py-2 font-medium">
                        {LINT_VALIDATION_CATALOG_COL_DESCRIPTION}
                      </th>
                      <th className="px-2 py-2 font-medium">
                        {LINT_VALIDATION_CATALOG_COL_SOURCE}
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                    {sorted.map((entry) => {
                      const profiles = formatApplicableProfiles(entry);
                      return (
                        <tr
                          key={`${entry.family ?? 'lint'}-${entry.code}`}
                          data-testid={`lint-validation-catalog-entry-${entry.code}`}
                          className={
                            highlightedCode === entry.code
                              ? 'align-top bg-sky-50 ring-2 ring-sky-400 dark:bg-sky-950/40'
                              : 'align-top'
                          }
                        >
                          <td className="px-2 py-2 font-mono text-xs text-gray-900 dark:text-gray-100">
                            {entry.code}
                          </td>
                          <td className="px-2 py-2 text-gray-700 dark:text-gray-300">
                            {entry.issue_type ?? '—'}
                          </td>
                          <td className="px-2 py-2 text-gray-700 dark:text-gray-300">
                            {entry.severity || '—'}
                          </td>
                          <td className="px-2 py-2 text-xs text-gray-700 dark:text-gray-300">
                            <div className="space-y-1">
                              <p>
                                <span className="font-medium">Semantic:</span>{' '}
                                {profiles.semantic}
                              </p>
                              <p>
                                <span className="font-medium">Exchange:</span>{' '}
                                {profiles.exchange}
                              </p>
                            </div>
                          </td>
                          <td className="px-2 py-2 text-gray-700 dark:text-gray-300">
                            {entry.message_template}
                          </td>
                          <td className="px-2 py-2">
                            <div className="space-y-1">
                              {entry.source_locator ? (
                                <p className="text-xs text-gray-600 dark:text-gray-400">
                                  {entry.source_locator}
                                </p>
                              ) : null}
                              {entry.source_access ? (
                                <p className="text-xs text-gray-500 dark:text-gray-500">
                                  Access: {entry.source_access.replace('_', ' ')}
                                </p>
                              ) : null}
                              {isClickableSource(entry) ? (
                                <a
                                  href={entry.source_url!}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="break-all text-blue-700 underline hover:text-blue-900 dark:text-blue-400"
                                >
                                  {entry.source_url}
                                </a>
                              ) : entry.source_url ? (
                                <span className="break-all text-gray-500 dark:text-gray-400">
                                  {entry.source_url}
                                </span>
                              ) : (
                                <span className="text-gray-400">—</span>
                              )}
                            </div>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              )}
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}

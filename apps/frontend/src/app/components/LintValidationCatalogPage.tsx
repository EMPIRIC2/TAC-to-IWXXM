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
import { shellFrameClass, useLiveConvertLayout } from '@/utils/liveConvertLayout';
import type { LintIssueCatalogEntry } from '@/utils/openapiTypes';
import { Card } from './ui/card';
import {
  catalogEntryMatchesQuery,
  catalogFamilyLabel,
  selectedCatalogCode,
} from '@/utils/catalogPresentation';
import {
  LINT_VALIDATION_CATALOG_ACCESS_LABEL,
  LINT_VALIDATION_CATALOG_COL_CODE,
  LINT_VALIDATION_CATALOG_COL_DESCRIPTION,
  LINT_VALIDATION_CATALOG_COL_LEVEL,
  LINT_VALIDATION_CATALOG_COL_PROFILES,
  LINT_VALIDATION_CATALOG_COL_SOURCE,
  LINT_VALIDATION_CATALOG_COL_TYPE,
  LINT_VALIDATION_CATALOG_DETAIL,
  LINT_VALIDATION_CATALOG_EXAMPLE_FAIL,
  LINT_VALIDATION_CATALOG_EXAMPLE_FAIL_UNAVAILABLE,
  LINT_VALIDATION_CATALOG_EXAMPLE_NOTE,
  LINT_VALIDATION_CATALOG_EXAMPLE_PASS,
  LINT_VALIDATION_CATALOG_EXAMPLE_PASS_UNAVAILABLE,
  LINT_VALIDATION_CATALOG_EMPTY,
  LINT_VALIDATION_CATALOG_EXCHANGE_ALL,
  LINT_VALIDATION_CATALOG_EXCHANGE_LABEL,
  LINT_VALIDATION_CATALOG_FAMILY_ALL,
  LINT_VALIDATION_CATALOG_LISTED_PROFILE_NEEDS_PROFILE,
  LINT_VALIDATION_CATALOG_LISTED_PROFILE_ONLY,
  LINT_VALIDATION_CATALOG_LOAD_ERROR,
  LINT_VALIDATION_CATALOG_RETRY,
  catalogFilterLabel,
  LINT_VALIDATION_CATALOG_FAMILY_LABEL,
  LINT_VALIDATION_CATALOG_LEVEL_LABEL,
  LINT_VALIDATION_CATALOG_LOADING,
  LINT_VALIDATION_CATALOG_PAGE_SUBTITLE,
  LINT_VALIDATION_CATALOG_PAGE_TITLE,
  LINT_VALIDATION_CATALOG_PROFILE_ALL,
  LINT_VALIDATION_CATALOG_PROFILE_LABEL,
  LINT_VALIDATION_CATALOG_SEARCH,
  LINT_VALIDATION_CATALOG_SORT_LABEL,
  LINT_VALIDATION_CATALOG_TYPE_LABEL,
  LINT_VALIDATION_CATALOG_VIEW_COMPACT,
  LINT_VALIDATION_CATALOG_VIEW_DETAILED,
  LINT_VALIDATION_CATALOG_VIEW_LABEL,
} from '@/utils/lintValidationCatalogCopy';
import {
  readCatalogView,
  writeCatalogView,
  type CatalogView,
} from '@/utils/catalogView';
import { catalogLevelLabel } from '@/utils/readableStatus';
import { ruleExamplePair } from '@/utils/ruleCatalogExamples';
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
 * Extra fields for the selected rule in the detailed catalog view.
 *
 * @param props.entry - Selected catalog row
 * @example
 * const _ = true;
 */
function SelectedRuleFacts({ entry }: { entry: LintIssueCatalogEntry }) {
  const profiles = formatApplicableProfiles(entry);
  return (
    <div
      className="mt-3 space-y-1 text-sm text-gray-700 dark:text-gray-300"
      data-testid="catalog-detail-facts"
    >
      <p>
        {LINT_VALIDATION_CATALOG_COL_TYPE}: {entry.issue_type ?? '—'}
      </p>
      <p>
        {LINT_VALIDATION_CATALOG_COL_PROFILES}: {profiles.semantic}
      </p>
      <p>Exchange: {profiles.exchange}</p>
      <p>
        {LINT_VALIDATION_CATALOG_COL_SOURCE}: {entry.source_locator ?? '—'}
      </p>
    </div>
  );
}

/**
 * Pass and fail reports for the selected rule, or a note when that side is not on file.
 *
 * @param props.code - Selected catalog rule code
 * @example
 * const _ = true;
 */
function RuleExamples({ code }: { code: string }) {
  const examples = ruleExamplePair(code);
  return (
    <section className="mt-4 space-y-3" aria-label="Passing and failing examples">
      <p className="text-sm text-gray-600 dark:text-gray-400">
        {LINT_VALIDATION_CATALOG_EXAMPLE_NOTE}
      </p>
      <div>
        <h3 className="text-sm font-semibold text-emerald-800 dark:text-emerald-300">
          {LINT_VALIDATION_CATALOG_EXAMPLE_PASS}
        </h3>
        {examples.pass ? (
          <pre
            data-testid="catalog-rule-example-pass"
            data-tone="pass"
            className="mt-1 overflow-x-auto rounded-md border border-emerald-300 bg-emerald-50 p-2 font-mono text-xs whitespace-pre-wrap text-emerald-950 dark:border-emerald-800 dark:bg-emerald-950 dark:text-emerald-100"
          >
            {examples.pass}
          </pre>
        ) : (
          <p
            data-testid="catalog-rule-example-pass"
            data-tone="unavailable"
            className="mt-1 text-sm text-gray-600 dark:text-gray-400"
          >
            {LINT_VALIDATION_CATALOG_EXAMPLE_PASS_UNAVAILABLE}
          </p>
        )}
      </div>
      <div>
        <h3 className="text-sm font-semibold text-red-800 dark:text-red-300">
          {LINT_VALIDATION_CATALOG_EXAMPLE_FAIL}
        </h3>
        {examples.fail ? (
          <pre
            data-testid="catalog-rule-example-fail"
            data-tone="fail"
            className="mt-1 overflow-x-auto rounded-md border border-red-300 bg-red-50 p-2 font-mono text-xs whitespace-pre-wrap text-red-950 dark:border-red-800 dark:bg-red-950 dark:text-red-100"
          >
            {examples.fail}
          </pre>
        ) : (
          <p
            data-testid="catalog-rule-example-fail"
            data-tone="unavailable"
            className="mt-1 text-sm text-gray-600 dark:text-gray-400"
          >
            {LINT_VALIDATION_CATALOG_EXAMPLE_FAIL_UNAVAILABLE}
          </p>
        )}
      </div>
    </section>
  );
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
  const { layout } = useLiveConvertLayout();
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
  const [query, setQuery] = useState('');
  const [catalogView, setCatalogView] = useState<CatalogView>(() => readCatalogView());
  const [selectedCode, setSelectedCode] = useState<string | null>(null);
  const [entries, setEntries] = useState<LintIssueCatalogEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [highlightedCode, setHighlightedCode] = useState<string | null>(null);
  const focusHandledRef = useRef<string | null>(null);

  const typeOptions = useMemo(() => typeOptionsForFamily(familyFilter), [familyFilter]);

  const usesLintIssueCatalog =
    familyFilter === 'all' || familyFilter === 'lint' || familyFilter === 'iwxxm';
  const listedProfileNeedsChoice =
    usesLintIssueCatalog &&
    semanticProfileFilter === 'all' &&
    exchangeProfileFilter === 'all';
  const listedProfileLabel = listedProfileNeedsChoice
    ? LINT_VALIDATION_CATALOG_LISTED_PROFILE_NEEDS_PROFILE
    : LINT_VALIDATION_CATALOG_LISTED_PROFILE_ONLY;

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
    } catch {
      setError(LINT_VALIDATION_CATALOG_LOAD_ERROR);
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
        }) &&
        catalogEntryMatchesQuery(entry.code, entry.message_template, query),
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
    query,
  ]);

  const activeCode = selectedCatalogCode(
    sorted.map((entry) => entry.code),
    selectedCode,
  );
  const detail = sorted.find((entry) => entry.code === activeCode);

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
      setSelectedCode(focusCode);
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
      <div className={`mx-auto w-full space-y-6 ${shellFrameClass(layout.span)}`}>
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
                <option value="all">{LINT_VALIDATION_CATALOG_FAMILY_ALL}</option>
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
                    {catalogFilterLabel('type', opt)}
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
                    {catalogFilterLabel('access', opt)}
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
                onChange={(e) => {
                  const next =
                    e.target.value === 'all' ? 'all' : (e.target.value as IwxxmProfile);
                  setSemanticProfileFilter(next);
                  if (next === 'all' && exchangeProfileFilter === 'all') {
                    setListedProfileOnly(false);
                  }
                }}
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
                onChange={(e) => {
                  const next =
                    e.target.value === 'all'
                      ? 'all'
                      : (e.target.value as ExchangeProfileId);
                  setExchangeProfileFilter(next);
                  if (next === 'all' && semanticProfileFilter === 'all') {
                    setListedProfileOnly(false);
                  }
                }}
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
                disabled={!usesLintIssueCatalog || listedProfileNeedsChoice}
                data-testid="lint-validation-catalog-listed-profile-only"
                aria-label={listedProfileLabel}
                onChange={(e) => setListedProfileOnly(e.target.checked)}
              />
              {listedProfileLabel}
            </label>
            <label className="text-sm text-gray-700 dark:text-gray-300">
              {LINT_VALIDATION_CATALOG_SEARCH}
              <input
                type="search"
                className="ml-2 rounded border px-2 py-1 text-sm dark:bg-gray-800"
                value={query}
                data-testid="lint-validation-catalog-search"
                aria-label={LINT_VALIDATION_CATALOG_SEARCH}
                onChange={(e) => setQuery(e.target.value)}
              />
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
            <div
              className="flex rounded-md bg-gray-100 p-0.5 dark:bg-gray-800"
              role="group"
              aria-label={LINT_VALIDATION_CATALOG_VIEW_LABEL}
            >
              <button
                type="button"
                data-testid="lint-validation-catalog-view-detailed"
                aria-pressed={catalogView === 'detailed'}
                className="rounded px-2 py-1 text-xs font-medium text-gray-900 dark:text-gray-100"
                onClick={() => {
                  setCatalogView('detailed');
                  writeCatalogView('detailed');
                }}
              >
                {LINT_VALIDATION_CATALOG_VIEW_DETAILED}
              </button>
              <button
                type="button"
                data-testid="lint-validation-catalog-view-compact"
                aria-pressed={catalogView === 'compact'}
                className="rounded px-2 py-1 text-xs font-medium text-gray-900 dark:text-gray-100"
                onClick={() => {
                  setCatalogView('compact');
                  writeCatalogView('compact');
                }}
              >
                {LINT_VALIDATION_CATALOG_VIEW_COMPACT}
              </button>
            </div>
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
            <div className="flex flex-wrap items-center gap-3" role="alert">
              <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
              <button
                type="button"
                className="rounded border border-gray-300 px-2 py-1 text-sm text-gray-800 hover:bg-gray-100 dark:border-gray-600 dark:text-gray-100 dark:hover:bg-gray-800"
                data-testid="lint-validation-catalog-retry"
                onClick={() => {
                  void loadCatalog();
                }}
              >
                {LINT_VALIDATION_CATALOG_RETRY}
              </button>
            </div>
          )}

          {!loading && !error && (
            <div
              className={
                catalogView === 'compact'
                  ? 'grid gap-4 lg:grid-cols-[minmax(0,1.4fr)_minmax(14rem,0.6fr)]'
                  : 'grid gap-4 lg:grid-cols-[minmax(14rem,0.7fr)_minmax(0,1.3fr)]'
              }
              data-view={catalogView}
            >
              <div data-testid="lint-validation-catalog-list">
                {sorted.length === 0 ? (
                  <p className="py-3 text-sm text-gray-500 dark:text-gray-400">
                    {LINT_VALIDATION_CATALOG_EMPTY}
                  </p>
                ) : (
                  <ul className={catalogView === 'compact' ? 'space-y-1' : 'space-y-2'}>
                    {sorted.map((entry) => {
                      const profiles = formatApplicableProfiles(entry);
                      const selected = entry.code === activeCode;
                      return (
                        <li key={`${entry.family ?? 'lint'}-${entry.code}`}>
                          <article
                            data-testid={`lint-validation-catalog-entry-${entry.code}`}
                            className={
                              highlightedCode === entry.code || selected
                                ? `rounded-md border border-sky-400 bg-sky-50 ring-2 ring-sky-400 dark:bg-sky-950/40 ${catalogView === 'compact' ? 'px-2 py-1' : 'p-3'}`
                                : `rounded-md border border-gray-200 dark:border-gray-700 ${catalogView === 'compact' ? 'px-2 py-1' : 'p-3'}`
                            }
                          >
                            <button
                              type="button"
                              className={
                                catalogView === 'compact'
                                  ? 'flex w-full items-baseline gap-2 text-left'
                                  : 'w-full text-left'
                              }
                              aria-pressed={selected}
                              onClick={() => setSelectedCode(entry.code)}
                            >
                              {catalogView === 'detailed' ? (
                                <>
                                  <span className="text-xs font-semibold uppercase tracking-wide text-gray-700 dark:text-gray-200">
                                    {catalogLevelLabel(entry.severity)}
                                  </span>
                                  <span className="mt-1 block text-xs text-gray-600 dark:text-gray-400">
                                    {catalogFamilyLabel(entry.family)}
                                  </span>
                                  <span className="mt-1 block font-mono text-xs text-gray-900 dark:text-gray-100">
                                    {LINT_VALIDATION_CATALOG_COL_CODE}: {entry.code}
                                  </span>
                                  <span className="mt-1 block text-sm text-gray-800 dark:text-gray-200">
                                    {entry.message_template}
                                  </span>
                                </>
                              ) : (
                                <>
                                  <span className="shrink-0 font-mono text-xs text-gray-900 dark:text-gray-100">
                                    {entry.code}
                                  </span>
                                  <span className="truncate text-sm text-gray-800 dark:text-gray-200">
                                    {entry.message_template}
                                  </span>
                                </>
                              )}
                            </button>
                            {catalogView === 'detailed' ? (
                              <div className="mt-2 space-y-1 text-xs text-gray-700 dark:text-gray-300">
                                <p data-testid="catalog-entry-type">
                                  {LINT_VALIDATION_CATALOG_COL_TYPE}:{' '}
                                  {entry.issue_type ?? '—'}
                                </p>
                                <p data-testid="catalog-entry-level">
                                  {LINT_VALIDATION_CATALOG_COL_LEVEL}:{' '}
                                  {catalogLevelLabel(entry.severity)}
                                </p>
                                <p>
                                  <span className="font-medium">
                                    {LINT_VALIDATION_CATALOG_COL_PROFILES}:
                                  </span>{' '}
                                  Semantic: {profiles.semantic}
                                </p>
                                <p>Exchange: {profiles.exchange}</p>
                                <p className="text-gray-800 dark:text-gray-200">
                                  {LINT_VALIDATION_CATALOG_COL_DESCRIPTION}:{' '}
                                  {entry.message_template}
                                </p>
                                <div>
                                  <p className="font-medium">
                                    {LINT_VALIDATION_CATALOG_COL_SOURCE}
                                  </p>
                                  {entry.source_locator ? (
                                    <p className="text-gray-600 dark:text-gray-400">
                                      {entry.source_locator}
                                    </p>
                                  ) : null}
                                  {entry.source_access ? (
                                    <p className="text-gray-500">
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
                              </div>
                            ) : null}
                          </article>
                        </li>
                      );
                    })}
                  </ul>
                )}
              </div>
              {detail ? (
                <aside
                  className="rounded-md border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-950"
                  data-testid="lint-validation-catalog-detail"
                  aria-label={LINT_VALIDATION_CATALOG_DETAIL}
                >
                  <h2 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
                    {LINT_VALIDATION_CATALOG_DETAIL}
                  </h2>
                  <p className="mt-2 text-xs font-semibold uppercase tracking-wide text-gray-700 dark:text-gray-200">
                    {catalogLevelLabel(detail.severity)}
                  </p>
                  <p className="mt-1 text-xs text-gray-600 dark:text-gray-400">
                    {catalogFamilyLabel(detail.family)}
                  </p>
                  <p className="mt-2 font-mono text-sm text-gray-900 dark:text-gray-100">
                    {detail.code}
                  </p>
                  <p className="mt-2 text-sm text-gray-800 dark:text-gray-200">
                    {detail.message_template}
                  </p>
                  {catalogView === 'detailed' ? (
                    <SelectedRuleFacts entry={detail} />
                  ) : null}
                  <RuleExamples code={detail.code} />
                </aside>
              ) : null}
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}

/**
 * Top-level Validation Issues Catalog page — code, type, level, description, source links.
 *
 * Consumes GET /lint-issue-catalog (additive family + source fields). Peer shell tab
 * for F7.v / #1014; distinct from the workbench browse panel.
 */

import { useCallback, useEffect, useMemo, useState } from 'react';
import { Loader2 } from 'lucide-react';
import { fetchLintIssueCatalog } from '@/utils/api';
import type { LintIssueCatalogEntry } from '@/utils/openapiTypes';
import { Card } from './ui/card';
import {
  LINT_VALIDATION_CATALOG_ACCESS_LABEL,
  LINT_VALIDATION_CATALOG_COL_CODE,
  LINT_VALIDATION_CATALOG_COL_DESCRIPTION,
  LINT_VALIDATION_CATALOG_COL_LEVEL,
  LINT_VALIDATION_CATALOG_COL_SOURCE,
  LINT_VALIDATION_CATALOG_COL_TYPE,
  LINT_VALIDATION_CATALOG_EMPTY,
  LINT_VALIDATION_CATALOG_FAMILY_LABEL,
  LINT_VALIDATION_CATALOG_LEVEL_LABEL,
  LINT_VALIDATION_CATALOG_LOADING,
  LINT_VALIDATION_CATALOG_PAGE_SUBTITLE,
  LINT_VALIDATION_CATALOG_PAGE_TITLE,
  LINT_VALIDATION_CATALOG_SORT_LABEL,
  LINT_VALIDATION_CATALOG_TYPE_LABEL,
} from '@/utils/lintValidationCatalogCopy';

type FamilyFilter = 'all' | 'lint' | 'iwxxm';
type SortKey = 'code' | 'level' | 'family' | 'issue_type' | 'source_access';

const LEVEL_OPTIONS = ['all', 'critical', 'error', 'warning', 'info'] as const;
const TYPE_OPTIONS = [
  'all',
  'presence',
  'structure',
  'content',
  'consistency',
  'iwxxm_schema',
  'other',
] as const;
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
 * Read a sortable string field from a catalog row (non-level sorts).
 */
function sortFieldValue(entry: LintIssueCatalogEntry, sortBy: SortKey): string {
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
 */
function compareEntries(
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
 * Browse TAC lint and IWXXM validation catalog rows from the public API.
 */
export function LintValidationCatalogPage() {
  const [familyFilter, setFamilyFilter] = useState<FamilyFilter>('all');
  const [issueTypeFilter, setIssueTypeFilter] =
    useState<(typeof TYPE_OPTIONS)[number]>('all');
  const [levelFilter, setLevelFilter] = useState<(typeof LEVEL_OPTIONS)[number]>('all');
  const [sourceAccessFilter, setSourceAccessFilter] =
    useState<(typeof ACCESS_OPTIONS)[number]>('all');
  const [sortBy, setSortBy] = useState<SortKey>('code');
  const [entries, setEntries] = useState<LintIssueCatalogEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadCatalog = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetchLintIssueCatalog({
        family: familyFilter === 'all' ? undefined : familyFilter,
        issue_type: issueTypeFilter === 'all' ? undefined : issueTypeFilter,
        source_access: sourceAccessFilter === 'all' ? undefined : sourceAccessFilter,
      });
      setEntries(response.issues ?? []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load catalog');
      setEntries([]);
    } finally {
      setLoading(false);
    }
  }, [familyFilter, issueTypeFilter, sourceAccessFilter]);

  /* eslint-disable react-hooks/set-state-in-effect -- refetch when filters change */
  useEffect(() => {
    void loadCatalog();
  }, [loadCatalog]);
  /* eslint-enable react-hooks/set-state-in-effect */

  const sorted = useMemo(() => {
    const levelKey = levelFilter === 'all' ? null : levelFilter;
    const filtered = entries.filter((entry) => {
      if (levelKey && (entry.severity || '').toLowerCase() !== levelKey) {
        return false;
      }
      return true;
    });
    return [...filtered].sort((a, b) => compareEntries(a, b, sortBy));
  }, [entries, levelFilter, sortBy]);

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
                onChange={(e) => setFamilyFilter(e.target.value as FamilyFilter)}
              >
                <option value="all">All</option>
                <option value="lint">TAC lint</option>
                <option value="iwxxm">IWXXM validation</option>
              </select>
            </label>
            <label className="text-sm text-gray-700 dark:text-gray-300">
              {LINT_VALIDATION_CATALOG_TYPE_LABEL}
              <select
                className="ml-2 rounded border px-2 py-1 text-sm dark:bg-gray-800"
                value={issueTypeFilter}
                data-testid="lint-validation-catalog-type-filter"
                aria-label="Filter by type"
                onChange={(e) =>
                  setIssueTypeFilter(e.target.value as (typeof TYPE_OPTIONS)[number])
                }
              >
                {TYPE_OPTIONS.map((opt) => (
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
                        {LINT_VALIDATION_CATALOG_COL_DESCRIPTION}
                      </th>
                      <th className="px-2 py-2 font-medium">
                        {LINT_VALIDATION_CATALOG_COL_SOURCE}
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                    {sorted.map((entry) => (
                      <tr
                        key={`${entry.family ?? 'lint'}-${entry.code}`}
                        data-testid={`lint-validation-catalog-entry-${entry.code}`}
                        className="align-top"
                      >
                        <td className="px-2 py-2 font-mono text-xs text-gray-900 dark:text-gray-100">
                          {entry.code}
                        </td>
                        <td className="px-2 py-2 text-gray-700 dark:text-gray-300">
                          {entry.issue_type ?? '—'}
                        </td>
                        <td className="px-2 py-2 text-gray-700 dark:text-gray-300">
                          {entry.severity}
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
                    ))}
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

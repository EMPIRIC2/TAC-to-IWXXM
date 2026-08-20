/**
 * Top-level Lint & validation catalog page — code, level, description, source links.
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
  LINT_VALIDATION_CATALOG_COL_CODE,
  LINT_VALIDATION_CATALOG_COL_DESCRIPTION,
  LINT_VALIDATION_CATALOG_COL_LEVEL,
  LINT_VALIDATION_CATALOG_COL_SOURCE,
  LINT_VALIDATION_CATALOG_EMPTY,
  LINT_VALIDATION_CATALOG_FAMILY_LABEL,
  LINT_VALIDATION_CATALOG_LOADING,
  LINT_VALIDATION_CATALOG_PAGE_SUBTITLE,
  LINT_VALIDATION_CATALOG_PAGE_TITLE,
} from '@/utils/lintValidationCatalogCopy';

type FamilyFilter = 'all' | 'lint' | 'iwxxm';

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
 * Browse TAC lint and IWXXM validation catalog rows from the public API.
 */
export function LintValidationCatalogPage() {
  const [familyFilter, setFamilyFilter] = useState<FamilyFilter>('all');
  const [entries, setEntries] = useState<LintIssueCatalogEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadCatalog = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetchLintIssueCatalog({
        family: familyFilter === 'all' ? undefined : familyFilter,
      });
      setEntries(response.issues ?? []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load catalog');
      setEntries([]);
    } finally {
      setLoading(false);
    }
  }, [familyFilter]);

  /* eslint-disable react-hooks/set-state-in-effect -- refetch when family filter changes */
  useEffect(() => {
    void loadCatalog();
  }, [loadCatalog]);
  /* eslint-enable react-hooks/set-state-in-effect */

  const sorted = useMemo(
    () =>
      [...entries].sort((a, b) =>
        (a.code || '').localeCompare(b.code || '', undefined, { sensitivity: 'base' }),
      ),
    [entries],
  );

  return (
    <div
      className="min-h-screen bg-gray-50 p-6 dark:bg-gray-900"
      data-testid="lint-validation-catalog-page"
    >
      <div className="mx-auto max-w-5xl space-y-6">
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
                <table className="w-full min-w-[40rem] border-collapse text-left text-sm">
                  <thead>
                    <tr className="border-b border-gray-200 text-gray-600 dark:border-gray-700 dark:text-gray-300">
                      <th className="px-2 py-2 font-medium">
                        {LINT_VALIDATION_CATALOG_COL_CODE}
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
                          {entry.severity}
                        </td>
                        <td className="px-2 py-2 text-gray-700 dark:text-gray-300">
                          {entry.message_template}
                        </td>
                        <td className="px-2 py-2">
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

/* eslint-disable @typescript-eslint/ban-ts-comment, @typescript-eslint/no-explicit-any, complexity */
// @ts-nocheck — mechanical line-count split
/**
 * Presentational view extracted from LintValidationCatalogPage.tsx (line-count split).
 */
import { Loader2 } from 'lucide-react';
import { Card } from './ui/card';
import { GlossaryRichText } from './glossary/GlossaryRichText';
import { catalogFamilyLabel } from '@/utils/catalogPresentation';
import { catalogFilterLabel } from '@/utils/lintValidationCatalogCopy';
import {
  LINT_VALIDATION_CATALOG_ACCESS_LABEL,
  LINT_VALIDATION_CATALOG_COL_CODE,
  LINT_VALIDATION_CATALOG_COL_DESCRIPTION,
  LINT_VALIDATION_CATALOG_COL_LEVEL,
  LINT_VALIDATION_CATALOG_COL_SOURCE,
  LINT_VALIDATION_CATALOG_COL_TYPE,
  LINT_VALIDATION_CATALOG_DETAIL,
  LINT_VALIDATION_CATALOG_EMPTY,
  LINT_VALIDATION_CATALOG_FAMILY_ALL,
  LINT_VALIDATION_CATALOG_FAMILY_LABEL,
  LINT_VALIDATION_CATALOG_ISSUES_URL,
  LINT_VALIDATION_CATALOG_LEVEL_LABEL,
  LINT_VALIDATION_CATALOG_LOADING,
  LINT_VALIDATION_CATALOG_MISSING_RULE_LEAD,
  LINT_VALIDATION_CATALOG_MISSING_RULE_LINK,
  LINT_VALIDATION_CATALOG_PAGE_SUBTITLE,
  LINT_VALIDATION_CATALOG_PAGE_TITLE,
  LINT_VALIDATION_CATALOG_RETRY,
  LINT_VALIDATION_CATALOG_SEARCH,
  LINT_VALIDATION_CATALOG_SORT_LABEL,
  LINT_VALIDATION_CATALOG_TYPE_LABEL,
  LINT_VALIDATION_CATALOG_VIEW_COMPACT,
  LINT_VALIDATION_CATALOG_VIEW_DETAILED,
  LINT_VALIDATION_CATALOG_VIEW_LABEL,
} from '@/utils/lintValidationCatalogCopy';
import { catalogLevelLabel } from '@/utils/readableStatus';
import { shellFrameClass } from '@/utils/liveConvertLayout';
import { SelectedRuleFacts, RuleExamples } from '@/utils/lintCatalogUi';
import {
  ACCESS_OPTIONS,
  LEVEL_OPTIONS,
  SORT_OPTIONS,
  isClickableSource,
  typeOptionsForFamily,
  type SortKey,
} from '@/utils/lintCatalogHelpers';
import { writeCatalogView } from '@/utils/catalogView';

type FamilyFilter =
  | 'all'
  | 'lint'
  | 'iwxxm'
  | 'conversion'
  | 'dissemination'
  | 'decoding';

export type LintValidationCatalogViewProps = {
  familyFilter: any;
  setFamilyFilter: any;
  issueTypeFilter: any;
  setIssueTypeFilter: any;
  levelFilter: any;
  setLevelFilter: any;
  sourceAccessFilter: any;
  setSourceAccessFilter: any;
  sortBy: any;
  setSortBy: any;
  query: any;
  setQuery: any;
  catalogView: any;
  setCatalogView: any;
  setSelectedCode: any;
  loading: any;
  error: any;
  highlightedCode: any;
  typeOptions: any;
  loadCatalog: any;
  sorted: any;
  activeCode: any;
  detail: any;
};

/**
 * Function `LintValidationCatalogView`.
 */
/**
 * LintValidationCatalogView.
 */
export function LintValidationCatalogView({
  familyFilter,
  setFamilyFilter,
  issueTypeFilter,
  setIssueTypeFilter,
  levelFilter,
  setLevelFilter,
  sourceAccessFilter,
  setSourceAccessFilter,
  sortBy,
  setSortBy,
  query,
  setQuery,
  catalogView,
  setCatalogView,
  setSelectedCode,
  loading,
  error,
  highlightedCode,
  typeOptions,
  loadCatalog,
  sorted,
  activeCode,
  detail,
}: LintValidationCatalogViewProps) {
  return (
    <div
      className="min-h-screen bg-gray-50 dark:bg-gray-900"
      data-testid="lint-validation-catalog-page"
    >
      <div className={`mx-auto w-full space-y-6 px-4 py-6 ${shellFrameClass('roomy')}`}>
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            {LINT_VALIDATION_CATALOG_PAGE_TITLE}
          </h1>
          <GlossaryRichText
            as="p"
            className="text-sm text-gray-600 dark:text-gray-400"
            text={LINT_VALIDATION_CATALOG_PAGE_SUBTITLE}
          />
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
                  className="rounded-md border border-gray-200 bg-white p-4 lg:sticky lg:top-4 lg:max-h-[calc(100dvh-2rem)] lg:self-start lg:overflow-y-auto dark:border-gray-700 dark:bg-gray-950"
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
                  <RuleExamples code={detail.code} severity={detail.severity} />
                  <p className="mt-4 border-t border-gray-200 pt-3 text-sm text-gray-600 dark:border-gray-700 dark:text-gray-400">
                    {LINT_VALIDATION_CATALOG_MISSING_RULE_LEAD}
                    <a
                      href={LINT_VALIDATION_CATALOG_ISSUES_URL}
                      target="_blank"
                      rel="noopener noreferrer"
                      data-testid="lint-validation-catalog-issues-link"
                      className="text-blue-700 underline hover:text-blue-900 dark:text-blue-400"
                    >
                      {LINT_VALIDATION_CATALOG_MISSING_RULE_LINK}
                    </a>
                    .
                  </p>
                </aside>
              ) : null}
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}

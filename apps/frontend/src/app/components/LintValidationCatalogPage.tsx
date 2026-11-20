/* eslint-disable react-refresh/only-export-components */
/**
 * Top-level Validation Issues Catalog page — code, type, level, description, source links.
 *
 * Consumes GET /lint-issue-catalog (additive family + source fields). Peer shell tab
 * for F7.v / #1014; distinct from the workbench browse panel.
 */

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { fetchLintIssueCatalog, fetchRuleCatalog } from '@/utils/api';
import type { LintIssueCatalogEntry } from '@/utils/openapiTypes';
import {
  catalogEntryMatchesQuery,
  selectedCatalogCode,
} from '@/utils/catalogPresentation';
import { LINT_VALIDATION_CATALOG_LOAD_ERROR } from '@/utils/lintValidationCatalogCopy';
import { readCatalogView, type CatalogView } from '@/utils/catalogView';

type FamilyFilter =
  | 'all'
  | 'lint'
  | 'iwxxm'
  | 'conversion'
  | 'dissemination'
  | 'decoding';

import {
  ACCESS_OPTIONS,
  ALL_FAMILY_TYPE_OPTIONS,
  CONVERSION_TYPE_OPTIONS,
  DISSEMINATION_TYPE_OPTIONS,
  EV062_TYPE_OPTIONS,
  LEVEL_OPTIONS,
  type SortKey,
  compareEntries,
  entryMatchesAccessFilter,
  entryMatchesLevelFilter,
  entryMatchesTypeFilter,
  mapRuleCatalogItem,
  sortFieldValue,
  typeOptionsForFamily,
} from '@/utils/lintCatalogHelpers';
import { LintValidationCatalogView } from './LintValidationCatalogView';

export {
  ALL_FAMILY_TYPE_OPTIONS,
  CONVERSION_TYPE_OPTIONS,
  DISSEMINATION_TYPE_OPTIONS,
  EV062_TYPE_OPTIONS,
  compareEntries,
  entryMatchesLevelFilter,
  mapRuleCatalogItem,
  sortFieldValue,
  typeOptionsForFamily,
};

/**
 * LintValidationCatalogPage.
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
      const response = await fetchLintIssueCatalog(params);
      setEntries(response.issues ?? []);
    } catch {
      setError(LINT_VALIDATION_CATALOG_LOAD_ERROR);
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
    const typeKey = issueTypeFilter === 'all' ? null : issueTypeFilter;
    const accessKey = sourceAccessFilter === 'all' ? null : sourceAccessFilter;
    const filtered = entries.filter(
      (entry) =>
        entryMatchesLevelFilter(entry, levelKey) &&
        entryMatchesTypeFilter(entry, typeKey) &&
        entryMatchesAccessFilter(entry, accessKey) &&
        catalogEntryMatchesQuery(entry.code, entry.message_template, query),
    );
    return [...filtered].sort((a, b) => compareEntries(a, b, sortBy));
  }, [entries, levelFilter, issueTypeFilter, sourceAccessFilter, sortBy, query]);

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
    <LintValidationCatalogView
      familyFilter={familyFilter}
      setFamilyFilter={setFamilyFilter}
      issueTypeFilter={issueTypeFilter}
      setIssueTypeFilter={setIssueTypeFilter}
      levelFilter={levelFilter}
      setLevelFilter={setLevelFilter}
      sourceAccessFilter={sourceAccessFilter}
      setSourceAccessFilter={setSourceAccessFilter}
      sortBy={sortBy}
      setSortBy={setSortBy}
      query={query}
      setQuery={setQuery}
      catalogView={catalogView}
      setCatalogView={setCatalogView}
      setSelectedCode={setSelectedCode}
      loading={loading}
      error={error}
      highlightedCode={highlightedCode}
      typeOptions={typeOptions}
      loadCatalog={loadCatalog}
      sorted={sorted}
      activeCode={activeCode}
      detail={detail}
    />
  );
}

/**
 * Load GET /api/v1/lint-issue-catalog once per product for workbench tooltips.
 */

import { useEffect, useMemo, useState } from 'react';
import { fetchLintIssueCatalog, type LintIssueCatalogEntry } from '@/utils/api';
import { indexCatalogByCode } from '@/utils/lintIssueCatalog';

export interface UseLintIssueCatalogResult {
  entries: LintIssueCatalogEntry[];
  byCode: Map<string, LintIssueCatalogEntry>;
  loading: boolean;
  error: string | null;
}

/**
 * Fetch the lint issue catalog for tooltip / panel UI (F15 / E11-31).
 */
export function useLintIssueCatalog(options: {
  product?: string;
  accessToken?: string;
  enabled?: boolean;
}): UseLintIssueCatalogResult {
  const { product, accessToken, enabled = true } = options;
  const [entries, setEntries] = useState<LintIssueCatalogEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!enabled) {
      return;
    }
    const controller = new AbortController();
    setLoading(true);
    setError(null);
    fetchLintIssueCatalog({
      product,
      accessToken,
      signal: controller.signal,
    })
      .then((res) => {
        if (!controller.signal.aborted) {
          setEntries(res.issues);
        }
      })
      .catch((err: unknown) => {
        if (controller.signal.aborted) {
          return;
        }
        setEntries([]);
        setError(err instanceof Error ? err.message : 'Catalog load failed');
      })
      .finally(() => {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      });
    return () => controller.abort();
  }, [product, accessToken, enabled]);

  const byCode = useMemo(() => indexCatalogByCode(entries), [entries]);

  return { entries, byCode, loading, error };
}

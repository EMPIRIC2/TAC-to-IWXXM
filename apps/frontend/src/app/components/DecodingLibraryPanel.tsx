/**
 * Decoding library panel — seeded decode_tac glossary entries (EV-bridge AC9).
 */

import { Loader2 } from 'lucide-react';
import { useCallback, useEffect, useMemo, useState } from 'react';

import {
  listLibraryAssets,
  type LibraryAssetOut,
} from '../../utils/conversionProfilesApi';
import {
  PROFILES_LIBRARY_ACCESS_BUILTIN,
  PROFILES_LIBRARY_ACCESS_CUSTOM,
  PROFILES_LIBRARY_DECODE_EMPTY,
  PROFILES_LIBRARY_DECODE_ENTRIES_HEADING,
  PROFILES_LIBRARY_DECODE_HELP,
  PROFILES_LIBRARY_LIST_EMPTY,
  PROFILES_LIBRARY_LIST_ERROR,
  PROFILES_LIBRARY_LIST_LOADING,
  PROFILES_LIBRARY_TAB_DECODING,
} from '../../utils/conversionProfilesCopy';
import { Card } from './ui/card';

export type DecodingLibraryPanelProps = {
  accessToken: string;
};

type DecodeEntry = { token: string; explanation: string };

function accessLabel(access: string): string {
  return access === 'first_party'
    ? PROFILES_LIBRARY_ACCESS_BUILTIN
    : PROFILES_LIBRARY_ACCESS_CUSTOM;
}

function entriesFromBody(body: Record<string, unknown> | undefined): DecodeEntry[] {
  const raw = body?.entries;
  if (!Array.isArray(raw)) {
    return [];
  }
  return raw
    .map((item) => {
      if (!item || typeof item !== 'object') {
        return null;
      }
      const row = item as Record<string, unknown>;
      const token = String(row.token ?? '').trim();
      const explanation = String(row.explanation ?? '').trim();
      if (!token) {
        return null;
      }
      return { token, explanation };
    })
    .filter((row): row is DecodeEntry => row !== null);
}

/**
 * List Decoding libraries and show seeded glossary entries.
 *
 * @param props.accessToken - Bearer JWT
 */
export function DecodingLibraryPanel({ accessToken }: DecodingLibraryPanelProps) {
  const [items, setItems] = useState<LibraryAssetOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedId, setSelectedId] = useState('');
  const [filter, setFilter] = useState('');

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await listLibraryAssets(accessToken, 'decoding');
      setItems(res.items);
      setSelectedId(res.items[0]?.id ?? '');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      setItems([]);
    } finally {
      setLoading(false);
    }
  }, [accessToken]);

  /* eslint-disable react-hooks/set-state-in-effect -- refetch when token changes */
  useEffect(() => {
    void load();
  }, [load]);
  /* eslint-enable react-hooks/set-state-in-effect */

  const selected = items.find((item) => item.id === selectedId) ?? items[0];
  const entries = useMemo(() => entriesFromBody(selected?.body), [selected?.body]);
  const filtered = useMemo(() => {
    const q = filter.trim().toUpperCase();
    if (!q) {
      return entries.slice(0, 40);
    }
    return entries
      .filter(
        (row) => row.token.includes(q) || row.explanation.toUpperCase().includes(q),
      )
      .slice(0, 40);
  }, [entries, filter]);

  return (
    <Card className="space-y-3 p-4" data-testid="library-assets-panel-decoding">
      <div>
        <h2 className="text-sm font-medium">{PROFILES_LIBRARY_TAB_DECODING}</h2>
        <p className="mt-1 text-xs text-gray-600 dark:text-gray-400">
          {PROFILES_LIBRARY_DECODE_HELP}
        </p>
      </div>

      {loading ? (
        <p className="flex items-center gap-2 text-sm text-gray-500">
          <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
          {PROFILES_LIBRARY_LIST_LOADING}
        </p>
      ) : error ? (
        <p className="text-sm text-amber-700 dark:text-amber-300">
          {PROFILES_LIBRARY_LIST_ERROR} {error}
        </p>
      ) : items.length === 0 ? (
        <p className="text-sm text-gray-500">{PROFILES_LIBRARY_LIST_EMPTY}</p>
      ) : (
        <>
          <label className="block text-sm">
            <span className="text-gray-700 dark:text-gray-300">
              {PROFILES_LIBRARY_TAB_DECODING}
            </span>
            <select
              className="mt-1 w-full rounded border p-2 dark:border-gray-600 dark:bg-gray-900"
              data-testid="library-assets-select-decoding"
              value={selected?.id ?? ''}
              onChange={(e) => setSelectedId(e.target.value)}
            >
              {items.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.name} ({accessLabel(item.access)})
                </option>
              ))}
            </select>
          </label>
          {selected ? (
            <div className="space-y-2 text-sm text-gray-700 dark:text-gray-300">
              <p>
                National line:{' '}
                <span className="font-medium">{selected.attachedNationalLine}</span>
                {' · '}
                Access:{' '}
                <span className="font-medium">{accessLabel(selected.access)}</span>
                {' · '}
                Entries: <span className="font-medium">{entries.length}</span>
              </p>
              <label className="block text-sm">
                <span className="text-gray-700 dark:text-gray-300">
                  {PROFILES_LIBRARY_DECODE_ENTRIES_HEADING}
                </span>
                <input
                  className="mt-1 w-full rounded border p-2 dark:border-gray-600 dark:bg-gray-900"
                  data-testid="decoding-entries-filter"
                  placeholder="Filter tokens…"
                  value={filter}
                  onChange={(e) => setFilter(e.target.value)}
                />
              </label>
              {filtered.length === 0 ? (
                <p className="text-sm text-gray-500">{PROFILES_LIBRARY_DECODE_EMPTY}</p>
              ) : (
                <ul
                  className="max-h-64 space-y-1 overflow-y-auto text-sm"
                  data-testid="decoding-entries-list"
                >
                  {filtered.map((row) => (
                    <li key={row.token}>
                      <span className="font-medium">{row.token}</span>
                      {row.explanation ? (
                        <span className="text-gray-600 dark:text-gray-400">
                          {' — '}
                          {row.explanation}
                        </span>
                      ) : null}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          ) : null}
        </>
      )}
    </Card>
  );
}

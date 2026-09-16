/**
 * Decoding library panel — glossary maps, units, structured types (EVWB P3).
 */

import { Loader2 } from 'lucide-react';
import { useCallback, useEffect, useMemo, useState } from 'react';

import {
  createLibraryAsset,
  listLibraryAssets,
  updateLibraryAsset,
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

type DecodeEntry = {
  token: string;
  explanation: string;
  unit: string;
  structuredType: string;
};

const STRUCTURED_TYPES = ['text', 'polygon', 'point', 'range'] as const;

function accessLabel(access: string): string {
  return access === 'first_party'
    ? PROFILES_LIBRARY_ACCESS_BUILTIN
    : PROFILES_LIBRARY_ACCESS_CUSTOM;
}

function yamlQuote(value: string): string {
  return JSON.stringify(value);
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
      return {
        token,
        explanation,
        unit: typeof row.unit === 'string' ? row.unit : '',
        structuredType:
          typeof row.structured_type === 'string'
            ? row.structured_type
            : typeof row.structuredType === 'string'
              ? row.structuredType
              : 'text',
      };
    })
    .filter((row): row is DecodeEntry => row !== null);
}

function entriesToBody(entries: DecodeEntry[]): Record<string, unknown>[] {
  return entries.map((e) => ({
    token: e.token,
    explanation: e.explanation,
    ...(e.unit ? { unit: e.unit } : {}),
    structured_type: e.structuredType || 'text',
  }));
}

function entriesToYaml(name: string, entries: DecodeEntry[]): string {
  const lines = ['kind: decoding', `name: ${yamlQuote(name)}`, 'entries:'];
  for (const e of entries) {
    lines.push(`  - token: ${yamlQuote(e.token)}`);
    lines.push(`    explanation: ${yamlQuote(e.explanation)}`);
    if (e.unit) {
      lines.push(`    unit: ${yamlQuote(e.unit)}`);
    }
    lines.push(`    structured_type: ${e.structuredType || 'text'}`);
  }
  return `${lines.join('\n')}\n`;
}

/**
 * List and author Decoding library glossary entries.
 *
 * @param props.accessToken - Bearer JWT
 */
export function DecodingLibraryPanel({ accessToken }: DecodingLibraryPanelProps) {
  const [items, setItems] = useState<LibraryAssetOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedId, setSelectedId] = useState('');
  const [filter, setFilter] = useState('');
  const [entries, setEntries] = useState<DecodeEntry[]>([]);
  const [selectedToken, setSelectedToken] = useState('');
  const [busy, setBusy] = useState(false);
  const [saveNote, setSaveNote] = useState<string | null>(null);

  const selected = items.find((item) => item.id === selectedId) ?? items[0];
  const isBuiltin = selected?.access === 'first_party';
  const editable = Boolean(selected && !isBuiltin);

  const applyAsset = useCallback((asset: LibraryAssetOut) => {
    setSelectedId(asset.id);
    const next = entriesFromBody(asset.body);
    setEntries(next);
    setSelectedToken(next[0]?.token ?? '');
    setSaveNote(null);
  }, []);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await listLibraryAssets(accessToken, 'decoding');
      setItems(res.items);
      if (res.items[0]) {
        applyAsset(res.items[0]);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      setItems([]);
    } finally {
      setLoading(false);
    }
  }, [accessToken, applyAsset]);

  /* eslint-disable react-hooks/set-state-in-effect -- refetch when token changes */
  useEffect(() => {
    void load();
  }, [load]);
  /* eslint-enable react-hooks/set-state-in-effect */

  const filtered = useMemo(() => {
    const q = filter.trim().toUpperCase();
    const list = !q
      ? entries.slice(0, 40)
      : entries
          .filter(
            (row) => row.token.includes(q) || row.explanation.toUpperCase().includes(q),
          )
          .slice(0, 40);
    return list;
  }, [entries, filter]);

  /* eslint-disable react-hooks/set-state-in-effect -- keep selection in filter */
  useEffect(() => {
    if (filtered.length === 0) {
      return;
    }
    if (!filtered.some((e) => e.token === selectedToken)) {
      setSelectedToken(filtered[0]!.token);
    }
  }, [filtered, selectedToken]);
  /* eslint-enable react-hooks/set-state-in-effect */

  const selectedEntry =
    entries.find((e) => e.token === selectedToken) ?? filtered[0] ?? null;

  const updateEntry = (token: string, patch: Partial<DecodeEntry>) => {
    if (!editable) {
      return;
    }
    setEntries((prev) => prev.map((e) => (e.token === token ? { ...e, ...patch } : e)));
    setSaveNote(null);
  };

  const addEntry = () => {
    if (!editable) {
      return;
    }
    const token = `NEW${Date.now().toString(36).toUpperCase().slice(-4)}`;
    const next: DecodeEntry = {
      token,
      explanation: '',
      unit: '',
      structuredType: 'text',
    };
    setEntries((prev) => [next, ...prev]);
    setSelectedToken(token);
    setSaveNote(null);
  };

  const forkSelected = async () => {
    if (!selected) {
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const slug = `fork-decode-${Date.now().toString(36)}`.slice(0, 120);
      const created = await createLibraryAsset(accessToken, {
        slug,
        name: `${selected.name} (custom)`,
        kind: 'decoding',
        engineProfileId: selected.engineProfileId,
        attachedNationalLine: selected.attachedNationalLine,
        body: { ...(selected.body ?? {}), entries: entriesToBody(entries) },
        forkOf: selected.id,
        yamlBody: entriesToYaml(`${selected.name} (custom)`, entries),
        status: 'draft',
      });
      const res = await listLibraryAssets(accessToken, 'decoding');
      setItems(res.items);
      applyAsset(created);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Fork failed');
    } finally {
      setBusy(false);
    }
  };

  const saveSelected = async () => {
    if (!selected || selected.access === 'first_party') {
      setError('Built-in decoding is read-only. Fork to create an editable copy.');
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const updated = await updateLibraryAsset(accessToken, selected.id, {
        body: { ...(selected.body ?? {}), entries: entriesToBody(entries) },
        yamlBody: entriesToYaml(selected.name, entries),
      });
      setItems((prev) => prev.map((a) => (a.id === updated.id ? updated : a)));
      applyAsset(updated);
      setSaveNote('Saved.');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Save failed');
    } finally {
      setBusy(false);
    }
  };

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
        <p
          className="text-sm text-amber-700 dark:text-amber-300"
          data-testid="decoding-panel-error"
        >
          {PROFILES_LIBRARY_LIST_ERROR} {error}
        </p>
      ) : items.length === 0 ? (
        <p className="text-sm text-gray-500">{PROFILES_LIBRARY_LIST_EMPTY}</p>
      ) : selected ? (
        <>
          <label className="block text-sm">
            <span className="text-gray-700 dark:text-gray-300">
              {PROFILES_LIBRARY_TAB_DECODING}
            </span>
            <select
              className="mt-1 w-full rounded border p-2 dark:border-gray-600 dark:bg-gray-900"
              data-testid="library-assets-select-decoding"
              value={selected.id}
              onChange={(e) => {
                const next = items.find((a) => a.id === e.target.value);
                if (next) {
                  applyAsset(next);
                }
              }}
            >
              {items.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.name} ({accessLabel(item.access)})
                </option>
              ))}
            </select>
          </label>

          {isBuiltin ? (
            <p
              className="rounded border border-amber-200 bg-amber-50 p-2 text-xs text-amber-900 dark:border-amber-800 dark:bg-amber-950/40 dark:text-amber-100"
              data-testid="decoding-rules-readonly"
            >
              Built-in decoding is read-only. Fork to create an editable copy.
            </p>
          ) : null}
          {saveNote ? (
            <p className="text-sm text-green-700" data-testid="decoding-rules-saved">
              {saveNote}
            </p>
          ) : null}

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
                className="max-h-40 space-y-1 overflow-y-auto text-sm"
                data-testid="decoding-entries-list"
              >
                {filtered.map((row) => (
                  <li key={row.token}>
                    <button
                      type="button"
                      className={`w-full rounded px-1 py-0.5 text-left hover:bg-gray-100 dark:hover:bg-gray-800 ${
                        selectedEntry?.token === row.token
                          ? 'bg-sky-50 dark:bg-sky-950/40'
                          : ''
                      }`}
                      data-testid={`decoding-entry-${row.token}`}
                      onClick={() => setSelectedToken(row.token)}
                    >
                      <span className="font-medium">{row.token}</span>
                      {row.explanation ? (
                        <span className="text-gray-600 dark:text-gray-400">
                          {' — '}
                          {row.explanation}
                        </span>
                      ) : null}
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>

          {selectedEntry ? (
            <div
              className="space-y-2 rounded border border-gray-200 p-3 dark:border-gray-700"
              data-testid="decoding-entry-editor"
            >
              <label className="block text-xs">
                <span className="text-gray-600 dark:text-gray-400">Token</span>
                <input
                  className="mt-1 w-full rounded border p-1.5 dark:border-gray-600 dark:bg-gray-900"
                  data-testid="decoding-entry-token"
                  value={selectedEntry.token}
                  disabled={!editable}
                  onChange={(e) => {
                    const next = e.target.value.toUpperCase();
                    updateEntry(selectedEntry.token, { token: next });
                    setSelectedToken(next);
                  }}
                />
              </label>
              <label className="block text-xs">
                <span className="text-gray-600 dark:text-gray-400">Meaning</span>
                <input
                  className="mt-1 w-full rounded border p-1.5 dark:border-gray-600 dark:bg-gray-900"
                  data-testid="decoding-entry-explanation"
                  value={selectedEntry.explanation}
                  disabled={!editable}
                  onChange={(e) =>
                    updateEntry(selectedEntry.token, {
                      explanation: e.target.value,
                    })
                  }
                />
              </label>
              <label className="block text-xs">
                <span className="text-gray-600 dark:text-gray-400">Unit</span>
                <input
                  className="mt-1 w-full rounded border p-1.5 dark:border-gray-600 dark:bg-gray-900"
                  data-testid="decoding-entry-unit"
                  value={selectedEntry.unit}
                  disabled={!editable}
                  onChange={(e) =>
                    updateEntry(selectedEntry.token, { unit: e.target.value })
                  }
                />
              </label>
              <label className="block text-xs">
                <span className="text-gray-600 dark:text-gray-400">
                  Structured type
                </span>
                <select
                  className="mt-1 w-full rounded border p-1.5 dark:border-gray-600 dark:bg-gray-900"
                  data-testid="decoding-entry-structured-type"
                  value={selectedEntry.structuredType}
                  disabled={!editable}
                  onChange={(e) =>
                    updateEntry(selectedEntry.token, {
                      structuredType: e.target.value,
                    })
                  }
                >
                  {STRUCTURED_TYPES.map((t) => (
                    <option key={t} value={t}>
                      {t}
                    </option>
                  ))}
                </select>
              </label>
            </div>
          ) : null}

          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              className="rounded border px-3 py-1.5 text-sm disabled:opacity-50"
              data-testid="decoding-rules-fork"
              disabled={busy}
              onClick={() => void forkSelected()}
            >
              Fork to edit
            </button>
            {editable ? (
              <>
                <button
                  type="button"
                  className="rounded border px-3 py-1.5 text-sm disabled:opacity-50"
                  data-testid="decoding-rules-add"
                  disabled={busy}
                  onClick={addEntry}
                >
                  Add entry
                </button>
                <button
                  type="button"
                  className="rounded border border-sky-700 px-3 py-1.5 text-sm text-sky-800 disabled:opacity-50 dark:text-sky-200"
                  data-testid="decoding-rules-save"
                  disabled={busy}
                  onClick={() => void saveSelected()}
                >
                  Save changes
                </button>
              </>
            ) : null}
          </div>
        </>
      ) : null}
    </Card>
  );
}

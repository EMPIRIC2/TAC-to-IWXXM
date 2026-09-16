/**
 * Dissemination library panel — transform enable/CRUD, no secrets (EVWB P3).
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
  PROFILES_LIBRARY_DISSEM_EMPTY_TRANSFORMS,
  PROFILES_LIBRARY_DISSEM_HELP,
  PROFILES_LIBRARY_DISSEM_TRANSFORMS_HEADING,
  PROFILES_LIBRARY_LIST_EMPTY,
  PROFILES_LIBRARY_LIST_ERROR,
  PROFILES_LIBRARY_LIST_LOADING,
  PROFILES_LIBRARY_TAB_DISSEMINATION,
} from '../../utils/conversionProfilesCopy';
import { Card } from './ui/card';

export type DisseminationLibraryPanelProps = {
  accessToken: string;
};

type TransformRow = {
  id: string;
  type: string;
  label: string;
  enabled: boolean;
  note: string;
};

const ALLOWED_TYPES = [
  'envelope',
  'topic_filename',
  'bulletin_rewrap',
  'checksum',
] as const;

function accessLabel(access: string): string {
  return access === 'first_party'
    ? PROFILES_LIBRARY_ACCESS_BUILTIN
    : PROFILES_LIBRARY_ACCESS_CUSTOM;
}

function yamlQuote(value: string): string {
  return JSON.stringify(value);
}

function transformsFromBody(body: Record<string, unknown> | undefined): TransformRow[] {
  const raw = body?.transforms;
  if (!Array.isArray(raw)) {
    return [];
  }
  return raw
    .map((item, index) => {
      if (typeof item === 'string') {
        return {
          id: item,
          type: item,
          label: item,
          enabled: true,
          note: '',
        };
      }
      if (item && typeof item === 'object') {
        const row = item as Record<string, unknown>;
        const type = String(row.type ?? row.id ?? `step-${index}`);
        const id = String(row.id ?? type);
        return {
          id,
          type,
          label: String(row.label ?? type),
          enabled: row.enabled === false ? false : true,
          note: typeof row.note === 'string' ? row.note : '',
        };
      }
      return null;
    })
    .filter((row): row is TransformRow => row !== null);
}

function transformsToBody(rows: TransformRow[]): Record<string, unknown>[] {
  return rows.map((r) => ({
    id: r.id,
    type: r.type,
    label: r.label,
    enabled: r.enabled,
    ...(r.note ? { note: r.note } : {}),
  }));
}

function transformsToYaml(name: string, rows: TransformRow[]): string {
  const lines = ['kind: dissemination', `name: ${yamlQuote(name)}`, 'transforms:'];
  for (const r of rows) {
    lines.push(`  - id: ${yamlQuote(r.id)}`);
    lines.push(`    type: ${r.type}`);
    lines.push(`    label: ${yamlQuote(r.label)}`);
    lines.push(`    enabled: ${r.enabled ? 'true' : 'false'}`);
    if (r.note) {
      lines.push(`    note: ${yamlQuote(r.note)}`);
    }
  }
  return `${lines.join('\n')}\n`;
}

/**
 * List and author Dissemination transforms (pattern-only; no credentials/URIs).
 *
 * @param props.accessToken - Bearer JWT
 */
export function DisseminationLibraryPanel({
  accessToken,
}: DisseminationLibraryPanelProps) {
  const [items, setItems] = useState<LibraryAssetOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedId, setSelectedId] = useState('');
  const [transforms, setTransforms] = useState<TransformRow[]>([]);
  const [selectedTransformId, setSelectedTransformId] = useState('');
  const [busy, setBusy] = useState(false);
  const [saveNote, setSaveNote] = useState<string | null>(null);

  const selected = items.find((item) => item.id === selectedId) ?? items[0];
  const isBuiltin = selected?.access === 'first_party';
  const editable = Boolean(selected && !isBuiltin);

  const applyAsset = useCallback((asset: LibraryAssetOut) => {
    setSelectedId(asset.id);
    const next = transformsFromBody(asset.body);
    setTransforms(next);
    setSelectedTransformId(next[0]?.id ?? '');
    setSaveNote(null);
  }, []);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await listLibraryAssets(accessToken, 'dissemination');
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

  const selectedTransform = useMemo(
    () => transforms.find((t) => t.id === selectedTransformId) ?? transforms[0] ?? null,
    [transforms, selectedTransformId],
  );

  const updateTransform = (id: string, patch: Partial<TransformRow>) => {
    if (!editable) {
      return;
    }
    setTransforms((prev) => prev.map((t) => (t.id === id ? { ...t, ...patch } : t)));
    setSaveNote(null);
  };

  const addTransform = () => {
    if (!editable) {
      return;
    }
    const type = ALLOWED_TYPES[0];
    const id = `${type}_${Date.now().toString(36)}`;
    const next: TransformRow = {
      id,
      type,
      label: type,
      enabled: true,
      note: 'Pattern-only; no destination URIs or credentials.',
    };
    setTransforms((prev) => [...prev, next]);
    setSelectedTransformId(id);
    setSaveNote(null);
  };

  const forkSelected = async () => {
    if (!selected) {
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const slug = `fork-dissem-${Date.now().toString(36)}`.slice(0, 120);
      const created = await createLibraryAsset(accessToken, {
        slug,
        name: `${selected.name} (custom)`,
        kind: 'dissemination',
        engineProfileId: selected.engineProfileId,
        attachedNationalLine: selected.attachedNationalLine,
        body: {
          ...(selected.body ?? {}),
          transforms: transformsToBody(transforms),
        },
        forkOf: selected.id,
        yamlBody: transformsToYaml(`${selected.name} (custom)`, transforms),
        status: 'draft',
      });
      const res = await listLibraryAssets(accessToken, 'dissemination');
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
      setError('Built-in dissemination is read-only. Fork to create an editable copy.');
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const updated = await updateLibraryAsset(accessToken, selected.id, {
        body: {
          ...(selected.body ?? {}),
          transforms: transformsToBody(transforms),
        },
        yamlBody: transformsToYaml(selected.name, transforms),
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
    <Card className="space-y-3 p-4" data-testid="library-assets-panel-dissemination">
      <div>
        <h2 className="text-sm font-medium">{PROFILES_LIBRARY_TAB_DISSEMINATION}</h2>
        <p className="mt-1 text-xs text-gray-600 dark:text-gray-400">
          {PROFILES_LIBRARY_DISSEM_HELP}
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
          data-testid="dissemination-panel-error"
        >
          {PROFILES_LIBRARY_LIST_ERROR} {error}
        </p>
      ) : items.length === 0 ? (
        <p className="text-sm text-gray-500">{PROFILES_LIBRARY_LIST_EMPTY}</p>
      ) : selected ? (
        <>
          <label className="block text-sm">
            <span className="text-gray-700 dark:text-gray-300">
              {PROFILES_LIBRARY_TAB_DISSEMINATION}
            </span>
            <select
              className="mt-1 w-full rounded border p-2 dark:border-gray-600 dark:bg-gray-900"
              data-testid="library-assets-select-dissemination"
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
              data-testid="dissemination-rules-readonly"
            >
              Built-in dissemination is read-only. Fork to create an editable copy.
              Credentials and destination URIs are never stored.
            </p>
          ) : null}
          {saveNote ? (
            <p
              className="text-sm text-green-700"
              data-testid="dissemination-rules-saved"
            >
              {saveNote}
            </p>
          ) : null}

          <div className="space-y-2 text-sm">
            <p className="font-medium text-gray-800 dark:text-gray-200">
              {PROFILES_LIBRARY_DISSEM_TRANSFORMS_HEADING}
            </p>
            {transforms.length === 0 ? (
              <p className="text-sm text-gray-500">
                {PROFILES_LIBRARY_DISSEM_EMPTY_TRANSFORMS}
              </p>
            ) : (
              <ul className="space-y-1" data-testid="dissemination-transforms-list">
                {transforms.map((row) => (
                  <li key={row.id}>
                    <button
                      type="button"
                      className={`w-full rounded px-2 py-1 text-left text-sm hover:bg-gray-100 dark:hover:bg-gray-800 ${
                        selectedTransform?.id === row.id
                          ? 'bg-sky-50 dark:bg-sky-950/40'
                          : ''
                      }`}
                      data-testid={`dissemination-transform-${row.id}`}
                      onClick={() => setSelectedTransformId(row.id)}
                    >
                      <span className="font-medium">{row.type}</span>
                      {row.id !== row.type ? (
                        <span className="text-gray-500"> ({row.id})</span>
                      ) : null}
                      {!row.enabled ? (
                        <span className="ml-1 text-xs text-amber-700">[off]</span>
                      ) : null}
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>

          {selectedTransform ? (
            <div
              className="space-y-2 rounded border border-gray-200 p-3 dark:border-gray-700"
              data-testid="dissemination-transform-editor"
            >
              <label className="flex items-center gap-2 text-xs">
                <input
                  type="checkbox"
                  data-testid="dissemination-transform-enabled"
                  checked={selectedTransform.enabled}
                  disabled={!editable}
                  onChange={(e) =>
                    updateTransform(selectedTransform.id, {
                      enabled: e.target.checked,
                    })
                  }
                />
                <span>Enabled</span>
              </label>
              <label className="block text-xs">
                <span className="text-gray-600 dark:text-gray-400">Type</span>
                <select
                  className="mt-1 w-full rounded border p-1.5 dark:border-gray-600 dark:bg-gray-900"
                  data-testid="dissemination-transform-type"
                  value={selectedTransform.type}
                  disabled={!editable}
                  onChange={(e) =>
                    updateTransform(selectedTransform.id, {
                      type: e.target.value,
                      label: e.target.value,
                    })
                  }
                >
                  {[...new Set([selectedTransform.type, ...ALLOWED_TYPES])].map((t) => (
                    <option key={t} value={t}>
                      {t}
                    </option>
                  ))}
                </select>
              </label>
              <label className="block text-xs">
                <span className="text-gray-600 dark:text-gray-400">Note</span>
                <input
                  className="mt-1 w-full rounded border p-1.5 dark:border-gray-600 dark:bg-gray-900"
                  data-testid="dissemination-transform-note"
                  value={selectedTransform.note}
                  disabled={!editable}
                  onChange={(e) =>
                    updateTransform(selectedTransform.id, {
                      note: e.target.value,
                    })
                  }
                />
              </label>
              <p className="text-xs text-gray-500">
                Destination URIs and credentials cannot be stored here.
              </p>
            </div>
          ) : null}

          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              className="rounded border px-3 py-1.5 text-sm disabled:opacity-50"
              data-testid="dissemination-rules-fork"
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
                  data-testid="dissemination-rules-add"
                  disabled={busy}
                  onClick={addTransform}
                >
                  Add transform
                </button>
                <button
                  type="button"
                  className="rounded border border-sky-700 px-3 py-1.5 text-sm text-sky-800 disabled:opacity-50 dark:text-sky-200"
                  data-testid="dissemination-rules-save"
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

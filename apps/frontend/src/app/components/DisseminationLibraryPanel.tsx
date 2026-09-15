/**
 * Dissemination library panel — ordered transforms preview (EV-bridge AC8).
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

type TransformRow = { id: string; type: string };

function accessLabel(access: string): string {
  return access === 'first_party'
    ? PROFILES_LIBRARY_ACCESS_BUILTIN
    : PROFILES_LIBRARY_ACCESS_CUSTOM;
}

function transformsFromBody(body: Record<string, unknown> | undefined): TransformRow[] {
  const raw = body?.transforms;
  if (!Array.isArray(raw)) {
    return [];
  }
  return raw
    .map((item, index) => {
      if (typeof item === 'string') {
        return { id: item, type: item };
      }
      if (item && typeof item === 'object') {
        const row = item as Record<string, unknown>;
        const type = String(row.type ?? row.id ?? `step-${index}`);
        const id = String(row.id ?? type);
        return { id, type };
      }
      return null;
    })
    .filter((row): row is TransformRow => row !== null);
}

/**
 * List Dissemination libraries and show ordered transform steps.
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

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await listLibraryAssets(accessToken, 'dissemination');
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

  const selected = items.find((item) => item.id === selectedId) ?? items[0]!;
  const transforms = useMemo(
    () => transformsFromBody(selected?.body),
    [selected?.body],
  );

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
        <p className="text-sm text-amber-700 dark:text-amber-300">
          {PROFILES_LIBRARY_LIST_ERROR} {error}
        </p>
      ) : items.length === 0 ? (
        <p className="text-sm text-gray-500">{PROFILES_LIBRARY_LIST_EMPTY}</p>
      ) : (
        <>
          <label className="block text-sm">
            <span className="text-gray-700 dark:text-gray-300">
              {PROFILES_LIBRARY_TAB_DISSEMINATION}
            </span>
            <select
              className="mt-1 w-full rounded border p-2 dark:border-gray-600 dark:bg-gray-900"
              data-testid="library-assets-select-dissemination"
              value={selected.id}
              onChange={(e) => setSelectedId(e.target.value)}
            >
              {items.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.name} ({accessLabel(item.access)})
                </option>
              ))}
            </select>
          </label>
          <div className="space-y-2 text-sm text-gray-700 dark:text-gray-300">
            <p>
              National line:{' '}
              <span className="font-medium">{selected.attachedNationalLine}</span>
              {' · '}
              Access:{' '}
              <span className="font-medium">{accessLabel(selected.access)}</span>
            </p>
            <h3 className="text-xs font-medium uppercase tracking-wide text-gray-500">
              {PROFILES_LIBRARY_DISSEM_TRANSFORMS_HEADING}
            </h3>
            {transforms.length === 0 ? (
              <p className="text-sm text-gray-500">
                {PROFILES_LIBRARY_DISSEM_EMPTY_TRANSFORMS}
              </p>
            ) : (
              <ol
                className="list-decimal space-y-1 pl-5"
                data-testid="dissemination-transforms-list"
              >
                {transforms.map((step, index) => (
                  <li key={`${step.id}-${index}`}>
                    <span className="font-medium">{step.type}</span>
                    {step.id !== step.type ? (
                      <span className="text-gray-500"> ({step.id})</span>
                    ) : null}
                  </li>
                ))}
              </ol>
            )}
          </div>
        </>
      )}
    </Card>
  );
}

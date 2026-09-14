/**
 * Stub list panel for non-Conversion Libraries (TAC/IWXXM validation, Dissemination, Decoding).
 */

import { Loader2 } from 'lucide-react';
import { useCallback, useEffect, useState } from 'react';

import {
  listLibraryAssets,
  type LibraryAssetKind,
  type LibraryAssetOut,
} from '../../utils/conversionProfilesApi';
import {
  PROFILES_LIBRARY_ACCESS_BUILTIN,
  PROFILES_LIBRARY_ACCESS_CUSTOM,
  PROFILES_LIBRARY_LIST_EMPTY,
  PROFILES_LIBRARY_LIST_ERROR,
  PROFILES_LIBRARY_LIST_LOADING,
  PROFILES_LIBRARY_STUB_HELP,
} from '../../utils/conversionProfilesCopy';
import { Card } from './ui/card';

export type LibraryAssetsListPanelProps = {
  accessToken: string;
  kind: Exclude<LibraryAssetKind, 'conversion'>;
  heading: string;
};

function accessLabel(access: string): string {
  return access === 'first_party'
    ? PROFILES_LIBRARY_ACCESS_BUILTIN
    : PROFILES_LIBRARY_ACCESS_CUSTOM;
}

/**
 * List library assets for one non-conversion kind.
 *
 * @param props.accessToken - Bearer JWT
 * @param props.kind - Library kind filter
 * @param props.heading - Operator-visible panel title
 */
export function LibraryAssetsListPanel({
  accessToken,
  kind,
  heading,
}: LibraryAssetsListPanelProps) {
  const [items, setItems] = useState<LibraryAssetOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedId, setSelectedId] = useState('');

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await listLibraryAssets(accessToken, kind);
      setItems(res.items);
      setSelectedId(res.items[0]?.id ?? '');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      setItems([]);
    } finally {
      setLoading(false);
    }
  }, [accessToken, kind]);

  /* eslint-disable react-hooks/set-state-in-effect -- refetch when token/kind changes */
  useEffect(() => {
    void load();
  }, [load]);
  /* eslint-enable react-hooks/set-state-in-effect */

  const selected = items.find((item) => item.id === selectedId) ?? items[0];

  return (
    <Card className="space-y-3 p-4" data-testid={`library-assets-panel-${kind}`}>
      <div>
        <h2 className="text-sm font-medium">{heading}</h2>
        <p className="mt-1 text-xs text-gray-600 dark:text-gray-400">
          {PROFILES_LIBRARY_STUB_HELP}
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
            <span className="text-gray-700 dark:text-gray-300">{heading}</span>
            <select
              className="mt-1 w-full rounded border p-2 dark:border-gray-600 dark:bg-gray-900"
              data-testid={`library-assets-select-${kind}`}
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
            <ul
              className="space-y-1 text-sm text-gray-700 dark:text-gray-300"
              data-testid={`library-assets-detail-${kind}`}
            >
              <li>
                National line:{' '}
                <span className="font-medium">{selected.attachedNationalLine}</span>
              </li>
              <li>
                Access:{' '}
                <span className="font-medium">{accessLabel(selected.access)}</span>
              </li>
            </ul>
          ) : null}
        </>
      )}
    </Card>
  );
}

/**
 * Convert bar — five Libraries pickers (Conversion … Decoding).
 */

import { useCallback, useEffect, useMemo, useState } from 'react';

import {
  listLibraryAssets,
  type LibraryAssetKind,
  type LibraryAssetOut,
} from '../../utils/conversionProfilesApi';
import { defaultLibraryId } from '../../utils/libraryIds';
import {
  PROFILES_LIBRARY_TAB_CONVERSION,
  PROFILES_LIBRARY_TAB_DECODING,
  PROFILES_LIBRARY_TAB_DISSEMINATION,
  PROFILES_LIBRARY_TAB_IWXXM_VALIDATION,
  PROFILES_LIBRARY_TAB_TAC_VALIDATION,
} from '../../utils/conversionProfilesCopy';
import { Label } from './ui/label';

const KIND_META: Array<{
  kind: LibraryAssetKind;
  label: string;
  testId: string;
  field:
    | 'conversionLibraryId'
    | 'tacValidationLibraryId'
    | 'iwxxmValidationLibraryId'
    | 'disseminationLibraryId'
    | 'decodingLibraryId';
}> = [
  {
    kind: 'conversion',
    label: PROFILES_LIBRARY_TAB_CONVERSION,
    testId: 'conversion-library-select',
    field: 'conversionLibraryId',
  },
  {
    kind: 'tac_validation',
    label: PROFILES_LIBRARY_TAB_TAC_VALIDATION,
    testId: 'tac-validation-library-select',
    field: 'tacValidationLibraryId',
  },
  {
    kind: 'iwxxm_validation',
    label: PROFILES_LIBRARY_TAB_IWXXM_VALIDATION,
    testId: 'iwxxm-validation-library-select',
    field: 'iwxxmValidationLibraryId',
  },
  {
    kind: 'dissemination',
    label: PROFILES_LIBRARY_TAB_DISSEMINATION,
    testId: 'dissemination-library-select',
    field: 'disseminationLibraryId',
  },
  {
    kind: 'decoding',
    label: PROFILES_LIBRARY_TAB_DECODING,
    testId: 'decoding-library-select',
    field: 'decodingLibraryId',
  },
];

export type LibraryPickerValues = {
  conversionLibraryId: string;
  tacValidationLibraryId: string;
  iwxxmValidationLibraryId: string;
  disseminationLibraryId: string;
  decodingLibraryId: string;
};

export type LibraryPickersBarProps = {
  accessToken?: string;
  values: LibraryPickerValues;
  disabled?: boolean;
  onChange: (next: LibraryPickerValues, conversionEngineProfileId?: string) => void;
};

function guestDefaults(): LibraryAssetOut[] {
  const lines = ['ICAO_2025', 'US_FAA_NWS', 'CA_ECCC'];
  const kinds: LibraryAssetKind[] = [
    'conversion',
    'tac_validation',
    'iwxxm_validation',
    'dissemination',
    'decoding',
  ];
  const out: LibraryAssetOut[] = [];
  for (const line of lines) {
    for (const kind of kinds) {
      out.push({
        id: defaultLibraryId(kind, line),
        kind,
        name: `${line.replaceAll('_', ' ')}`,
        access: 'first_party',
        engineProfileId: line,
        attachedNationalLine: line,
      });
    }
  }
  return out;
}

/**
 * Five library selects for the Convert product bar.
 *
 * @param props.accessToken - Optional JWT (loads custom + first-party assets)
 * @param props.values - Selected library ids
 * @param props.onChange - Emits ids + Conversion engine profile when Conversion changes
 * @param props.disabled - Read-only workbench
 */
export function LibraryPickersBar({
  accessToken,
  values,
  disabled = false,
  onChange,
}: LibraryPickersBarProps) {
  const [assets, setAssets] = useState<LibraryAssetOut[]>(() => guestDefaults());

  const load = useCallback(async () => {
    const token = accessToken?.trim();
    if (!token) {
      setAssets(guestDefaults());
      return;
    }
    try {
      const res = await listLibraryAssets(token);
      setAssets(res.items.length > 0 ? res.items : guestDefaults());
    } catch {
      setAssets(guestDefaults());
    }
  }, [accessToken]);

  /* eslint-disable react-hooks/set-state-in-effect -- refetch when token changes */
  useEffect(() => {
    void load();
  }, [load]);
  /* eslint-enable react-hooks/set-state-in-effect */

  const byKind = useMemo(() => {
    const map = new Map<LibraryAssetKind, LibraryAssetOut[]>();
    for (const meta of KIND_META) {
      map.set(
        meta.kind,
        assets.filter((a) => a.kind === meta.kind),
      );
    }
    return map;
  }, [assets]);

  return (
    <div
      className="flex min-w-0 flex-col gap-2 lg:flex-row lg:flex-wrap lg:items-center"
      data-testid="library-pickers-bar"
    >
      {KIND_META.map((meta) => {
        const options = byKind.get(meta.kind) ?? [];
        const value = values[meta.field] || options[0]?.id || '';
        return (
          <div key={meta.kind} className="flex min-w-0 items-center gap-1">
            <Label
              htmlFor={`param-library-${meta.kind}`}
              className="shrink-0 text-sm text-gray-700 dark:text-gray-300"
            >
              {meta.label}
            </Label>
            <select
              id={`param-library-${meta.kind}`}
              aria-label={meta.label}
              data-testid={meta.testId}
              value={value}
              disabled={disabled || options.length === 0}
              onChange={(e) => {
                const id = e.target.value;
                const asset = options.find((o) => o.id === id);
                const next = { ...values, [meta.field]: id };
                onChange(
                  next,
                  meta.kind === 'conversion' ? asset?.engineProfileId : undefined,
                );
              }}
              className="min-w-[9.5rem] shrink-0 rounded-md border border-gray-300 bg-white px-2 py-1.5 text-sm text-gray-900 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
            >
              {options.map((opt) => (
                <option key={opt.id} value={opt.id}>
                  {opt.name}
                </option>
              ))}
            </select>
          </div>
        );
      })}
    </div>
  );
}

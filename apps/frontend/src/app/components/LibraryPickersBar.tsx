/**
 * Convert bar — four library selects (Decoding / TAC / IWXXM / Conversion).
 * Options from GET /selection-options (TP-YCL-01 / #1251). Dissemination is Send-drawer only.
 */

import { useCallback, useEffect, useState } from 'react';

import { fetchSelectionOptions, type SelectionOptionKind } from '../../utils/api';
import { defaultLibraryId } from '../../utils/libraryIds';
import {
  CONVERT_LIBRARY_CATALOG_LINK,
  CONVERT_LIBRARY_HELP_CONVERSION,
  CONVERT_LIBRARY_HELP_DECODING,
  CONVERT_LIBRARY_HELP_IWXXM_VALIDATION,
  CONVERT_LIBRARY_HELP_TAC_VALIDATION,
  PROFILES_LIBRARY_TAB_CONVERSION,
  PROFILES_LIBRARY_TAB_DECODING,
  PROFILES_LIBRARY_TAB_IWXXM_VALIDATION,
  PROFILES_LIBRARY_TAB_TAC_VALIDATION,
} from '../../utils/conversionProfilesCopy';
import { BetaBadge } from './BetaBadge';
import { Label } from './ui/label';

type ConvertSelectKind = Exclude<SelectionOptionKind, 'dissemination'>;

type SelectOption = { id: string; label: string };

const KIND_META: Array<{
  kind: ConvertSelectKind;
  label: string;
  help: string;
  catalogFamily: 'conversion' | 'lint' | 'iwxxm' | 'decoding';
  testId: string;
  helpTestId: string;
  catalogTestId: string;
  field:
    | 'conversionLibraryId'
    | 'tacValidationLibraryId'
    | 'iwxxmValidationLibraryId'
    | 'decodingLibraryId';
}> = [
  {
    kind: 'decoding',
    label: PROFILES_LIBRARY_TAB_DECODING,
    help: CONVERT_LIBRARY_HELP_DECODING,
    catalogFamily: 'decoding',
    testId: 'decoding-library-select',
    helpTestId: 'decoding-library-help',
    catalogTestId: 'decoding-library-catalog-link',
    field: 'decodingLibraryId',
  },
  {
    kind: 'tac_validation',
    label: PROFILES_LIBRARY_TAB_TAC_VALIDATION,
    help: CONVERT_LIBRARY_HELP_TAC_VALIDATION,
    catalogFamily: 'lint',
    testId: 'tac-validation-library-select',
    helpTestId: 'tac-validation-library-help',
    catalogTestId: 'tac-validation-library-catalog-link',
    field: 'tacValidationLibraryId',
  },
  {
    kind: 'iwxxm_validation',
    label: PROFILES_LIBRARY_TAB_IWXXM_VALIDATION,
    help: CONVERT_LIBRARY_HELP_IWXXM_VALIDATION,
    catalogFamily: 'iwxxm',
    testId: 'iwxxm-validation-library-select',
    helpTestId: 'iwxxm-validation-library-help',
    catalogTestId: 'iwxxm-validation-library-catalog-link',
    field: 'iwxxmValidationLibraryId',
  },
  {
    kind: 'conversion',
    label: PROFILES_LIBRARY_TAB_CONVERSION,
    help: CONVERT_LIBRARY_HELP_CONVERSION,
    catalogFamily: 'conversion',
    testId: 'conversion-library-select',
    helpTestId: 'conversion-library-help',
    catalogTestId: 'conversion-library-catalog-link',
    field: 'conversionLibraryId',
  },
];

/**
 * Type `LibraryPickerValues`.
 * @example
 * const _ = true;
 */
export type LibraryPickerValues = {
  conversionLibraryId: string;
  tacValidationLibraryId: string;
  iwxxmValidationLibraryId: string;
  /** Kept for Send drawer / convert wire; not shown on Convert bar. */
  disseminationLibraryId: string;
  decodingLibraryId: string;
};

/**
 * Type `LibraryPickersBarProps`.
 * @example
 * const _ = true;
 */
export type LibraryPickersBarProps = {
  accessToken?: string;
  values: LibraryPickerValues;
  disabled?: boolean;
  onChange: (next: LibraryPickerValues, conversionEngineProfileId?: string) => void;
  /** Optional: open Rule catalogs for the matching family. */
  onOpenCatalog?: (family: 'conversion' | 'lint' | 'iwxxm' | 'decoding') => void;
};

/**
 * Guest fallback options when selection-options is unavailable.
 */
function guestOptions(kind: ConvertSelectKind): SelectOption[] {
  const lines = ['ICAO_2025', 'US_FAA_NWS', 'CA_ECCC'];
  return lines.map((line) => ({
    id: defaultLibraryId(kind, line),
    label: `${kind.replaceAll('_', ' ')} · ${line}`,
  }));
}

/**
 * National line from a first-party LIB.* id (LIB.CONVERSION.US_FAA_NWS → US_FAA_NWS).
 */
function nationalLineFromLibId(id: string): string | undefined {
  const parts = id.split('.');
  if (parts.length >= 3 && parts[0] === 'LIB') {
    return parts.slice(2).join('.');
  }
  return undefined;
}

/**
 * Four library selects for the Convert product bar (ADR-044 / #1251).
 *
 * @param props.values - Selected library ids
 * @param props.onChange - Emits ids + Conversion engine profile when Conversion changes
 * @param props.disabled - Read-only workbench
 * @param props.onOpenCatalog - Opens read-only Rule catalogs for the kind's family
 * @example
 * const _ = true;
 */
export function LibraryPickersBar({
  values,
  disabled = false,
  onChange,
  onOpenCatalog,
}: LibraryPickersBarProps) {
  const [byKind, setByKind] = useState<Record<ConvertSelectKind, SelectOption[]>>(
    () => ({
      decoding: guestOptions('decoding'),
      tac_validation: guestOptions('tac_validation'),
      iwxxm_validation: guestOptions('iwxxm_validation'),
      conversion: guestOptions('conversion'),
    }),
  );

  const load = useCallback(async () => {
    const next: Partial<Record<ConvertSelectKind, SelectOption[]>> = {};
    await Promise.all(
      KIND_META.map(async (meta) => {
        try {
          const res = await fetchSelectionOptions({ kind: meta.kind });
          next[meta.kind] =
            res.options.length > 0
              ? res.options.map((o) => ({ id: o.id, label: o.label }))
              : guestOptions(meta.kind);
        } catch {
          next[meta.kind] = guestOptions(meta.kind);
        }
      }),
    );
    setByKind({
      decoding: next.decoding as SelectOption[],
      tac_validation: next.tac_validation as SelectOption[],
      iwxxm_validation: next.iwxxm_validation as SelectOption[],
      conversion: next.conversion as SelectOption[],
    });
  }, []);

  /* eslint-disable react-hooks/set-state-in-effect -- load selection-options once on mount */
  useEffect(() => {
    void load();
  }, [load]);
  /* eslint-enable react-hooks/set-state-in-effect */

  return (
    <div className="flex min-w-0 flex-col gap-3" data-testid="library-pickers-bar">
      <div className="flex flex-wrap items-center gap-2">
        <BetaBadge className="inline-flex shrink-0" />
      </div>
      <div className="grid min-w-0 gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {KIND_META.map((meta) => {
          const options = byKind[meta.kind];
          const value = values[meta.field] || options[0]!.id;
          return (
            <div key={meta.kind} className="flex min-w-0 flex-col gap-1">
              <Label
                htmlFor={`param-library-${meta.kind}`}
                className="text-sm text-gray-700 dark:text-gray-300"
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
                  const next = { ...values, [meta.field]: id };
                  onChange(
                    next,
                    meta.kind === 'conversion' ? nationalLineFromLibId(id) : undefined,
                  );
                }}
                className="min-w-0 rounded-md border border-gray-300 bg-white px-2 py-1.5 text-sm text-gray-900 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
              >
                {options.map((opt) => (
                  <option key={opt.id} value={opt.id}>
                    {opt.label}
                  </option>
                ))}
              </select>
              <p
                className="text-xs text-gray-500 dark:text-gray-400"
                data-testid={meta.helpTestId}
              >
                {meta.help}{' '}
                {onOpenCatalog ? (
                  <button
                    type="button"
                    className="text-blue-700 underline dark:text-blue-300"
                    data-testid={meta.catalogTestId}
                    onClick={() => onOpenCatalog(meta.catalogFamily)}
                  >
                    {CONVERT_LIBRARY_CATALOG_LINK}
                  </button>
                ) : null}
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
}

/**
 * Workbench Mapping bridge — Convert surface preview against conversion templates.
 */

import { Loader2 } from 'lucide-react';
import { useCallback, useEffect, useState } from 'react';

import {
  listConversionTemplates,
  previewConversionTemplate,
  type ConversionTemplateOut,
  type ConversionTemplatePreviewResponse,
} from '../../utils/conversionProfilesApi';
import {
  MAPPING_BRIDGE_HEADING,
  PROFILES_CONV_TEMPLATES_FOCUS,
  PROFILES_CONV_TEMPLATES_LOADING,
  PROFILES_CONV_TEMPLATES_PREVIEW,
  PROFILES_CONV_TEMPLATES_SELECT,
} from '../../utils/conversionProfilesCopy';
import { MappingBridge } from './MappingBridge';
import { Card } from './ui/card';

/**
 * Type `WorkbenchMappingBridgeProps`.
 * @example
 * const _ = true;
 */
export type WorkbenchMappingBridgeProps = {
  accessToken: string;
  /** Optional TAC text to seed focus group (first non-empty token). */
  tacText?: string;
};

/**
 * Function `seedFocusFromTac`.
 */
function seedFocusFromTac(tacText: string | undefined): string {
  if (!tacText?.trim()) {
    return '18012G20KT';
  }
  const tokens = tacText
    .trim()
    .split(/\s+/)
    .map((t) => t.replace(/=+$/, ''))
    .filter(Boolean);
  // Prefer a wind-like group when present; else last token before '='.
  const wind = tokens.find((t) => /^\d{5}/.test(t) || /KT$|MPS$/.test(t));
  if (wind) return wind;
  const last = [...tokens].reverse().find((t) => t !== 'METAR' && t !== 'SPECI');
  return last || '18012G20KT';
}

/**
 * Convert-side Mapping bridge (signed-in).
 *
 * @param props.accessToken - Bearer JWT
 * @param props.tacText - Current workbench TAC for focus seeding
 * @example
 * const _ = true;
 */
export function WorkbenchMappingBridge({
  accessToken,
  tacText,
}: WorkbenchMappingBridgeProps) {
  const [items, setItems] = useState<ConversionTemplateOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedId, setSelectedId] = useState('');
  const [focusGroup, setFocusGroup] = useState(() => seedFocusFromTac(tacText));
  const [preview, setPreview] = useState<ConversionTemplatePreviewResponse | null>(
    null,
  );
  const [busy, setBusy] = useState(false);

  const selected = items.find((t) => t.id === selectedId) ?? items[0];

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await listConversionTemplates(accessToken);
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

  const runPreview = async () => {
    if (!selected) {
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const result = await previewConversionTemplate(accessToken, {
        templateId: selected.id,
        focusGroup,
        slots: selected.slots,
        iwxxmBlock: selected.iwxxmBlock,
      });
      setPreview(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      setPreview(null);
    } finally {
      setBusy(false);
    }
  };

  const skipChips =
    preview?.skipped?.map((s) => ({
      label: s.label || s.slot || 'skip',
      gloss: s.gloss,
    })) ?? [];

  return (
    <Card
      className="space-y-3 p-3"
      data-testid="workbench-mapping-bridge"
      aria-label={MAPPING_BRIDGE_HEADING}
    >
      {loading ? (
        <p className="flex items-center gap-2 text-sm text-gray-500">
          <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
          {PROFILES_CONV_TEMPLATES_LOADING}
        </p>
      ) : (
        <>
          <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
            <label className="block text-sm">
              <span className="text-gray-700 dark:text-gray-300">
                {PROFILES_CONV_TEMPLATES_SELECT}
              </span>
              <select
                className="mt-1 w-full rounded border border-gray-300 bg-white p-2 dark:border-gray-600 dark:bg-gray-900"
                data-testid="workbench-mapping-bridge-template"
                value={selected?.id ?? ''}
                onChange={(e) => {
                  setSelectedId(e.target.value);
                  setPreview(null);
                }}
                disabled={items.length === 0}
              >
                {items.map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.name}
                  </option>
                ))}
              </select>
            </label>
            <label className="block text-sm">
              <span className="text-gray-700 dark:text-gray-300">
                {PROFILES_CONV_TEMPLATES_FOCUS}
              </span>
              <input
                className="mt-1 w-full rounded border border-gray-300 bg-white p-2 dark:border-gray-600 dark:bg-gray-900"
                data-testid="workbench-mapping-bridge-focus"
                value={focusGroup}
                onChange={(e) => setFocusGroup(e.target.value)}
              />
            </label>
          </div>
          <button
            type="button"
            className="rounded bg-sky-700 px-3 py-1.5 text-sm text-white disabled:opacity-50"
            data-testid="workbench-mapping-bridge-preview"
            disabled={busy}
            onClick={() => void runPreview()}
          >
            {busy ? (
              <Loader2 className="mr-1 inline h-4 w-4 animate-spin" aria-hidden />
            ) : null}
            {PROFILES_CONV_TEMPLATES_PREVIEW}
          </button>
          {error ? (
            <p className="text-sm text-amber-700 dark:text-amber-300">{error}</p>
          ) : null}
          <MappingBridge
            tacGroup={focusGroup}
            templateName={selected?.name}
            matched={preview ? preview.matched : null}
            iwxxmBlock={preview?.xmlBlock ?? ''}
            skipChips={skipChips}
          />
        </>
      )}
    </Card>
  );
}

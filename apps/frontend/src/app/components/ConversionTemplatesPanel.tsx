/**
 * Conversion templates authoring panel (parameterizable TAC→IWXXM bridge).
 */

import { Loader2 } from 'lucide-react';
import { useCallback, useEffect, useState } from 'react';

import { Card } from './ui/card';
import { BetaBadge } from './BetaBadge';
import {
  createConversionTemplate,
  listConversionTemplates,
  previewConversionTemplate,
  type ConversionTemplateOut,
  type ConversionTemplatePreviewResponse,
  type ConversionTemplateSlot,
} from '../../utils/conversionProfilesApi';
import { reorderConversionTemplateSlots } from '../../utils/conversionTemplateSlots';
import {
  PROFILES_CONV_TEMPLATES_COMMENTS,
  PROFILES_CONV_TEMPLATES_EMPTY,
  PROFILES_CONV_TEMPLATES_FOCUS,
  PROFILES_CONV_TEMPLATES_FORK,
  PROFILES_CONV_TEMPLATES_HEADING,
  PROFILES_CONV_TEMPLATES_HELP,
  PROFILES_CONV_TEMPLATES_LOADING,
  PROFILES_CONV_TEMPLATES_MOVE_DOWN,
  PROFILES_CONV_TEMPLATES_MOVE_UP,
  PROFILES_CONV_TEMPLATES_PREVIEW,
} from '../../utils/conversionProfilesCopy';

export type ConversionTemplatesPanelProps = {
  accessToken: string;
};

/**
 * Author and preview parameterizable conversion templates.
 *
 * @param props.accessToken - Bearer JWT for profiles APIs
 */
export function ConversionTemplatesPanel({
  accessToken,
}: ConversionTemplatesPanelProps) {
  const [items, setItems] = useState<ConversionTemplateOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedId, setSelectedId] = useState('');
  const [slots, setSlots] = useState<ConversionTemplateSlot[]>([]);
  const [focusGroup, setFocusGroup] = useState('18012G20KT');
  const [comments, setComments] = useState('');
  const [preview, setPreview] = useState<ConversionTemplatePreviewResponse | null>(
    null,
  );
  const [dragIndex, setDragIndex] = useState<number | null>(null);
  const [busy, setBusy] = useState(false);

  const selected = items.find((t) => t.id === selectedId) ?? items[0];

  const applySelection = useCallback((tmpl: ConversionTemplateOut | undefined) => {
    if (!tmpl) return;
    setSelectedId(tmpl.id);
    setSlots(tmpl.slots ?? []);
    setFocusGroup(tmpl.sample || '18012G20KT');
    setPreview(null);
  }, []);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await listConversionTemplates(accessToken);
      setItems(res.items);
      applySelection(res.items[0]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load templates');
    } finally {
      setLoading(false);
    }
  }, [accessToken, applySelection]);

  /* eslint-disable react-hooks/set-state-in-effect -- refetch when token changes */
  useEffect(() => {
    void load();
  }, [load]);
  /* eslint-enable react-hooks/set-state-in-effect */

  const moveSelected = (delta: number) => {
    if (!slots.length) return;
    const idx = 0;
    setSlots(reorderConversionTemplateSlots(slots, idx, idx + delta));
  };

  const onDrop = (toIndex: number) => {
    if (dragIndex === null) return;
    setSlots(reorderConversionTemplateSlots(slots, dragIndex, toIndex));
    setDragIndex(null);
  };

  const runPreview = async () => {
    if (!selected) return;
    setBusy(true);
    setError(null);
    try {
      const res = await previewConversionTemplate(accessToken, {
        templateId: selected.id,
        focusGroup,
        slots,
        iwxxmBlock: selected.iwxxmBlock,
      });
      setPreview(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Preview failed');
    } finally {
      setBusy(false);
    }
  };

  const forkSelected = async () => {
    if (!selected) return;
    setBusy(true);
    setError(null);
    try {
      const slug = `fork-${selected.slug}-${Date.now().toString(36)}`.slice(0, 120);
      await createConversionTemplate(accessToken, {
        slug,
        name: `${selected.name} (custom)`,
        iwxxmBlock: selected.iwxxmBlock,
        slots,
        sample: focusGroup,
        comments: comments || undefined,
        forkOf:
          selected.access === 'first_party'
            ? selected.id
            : selected.forkOf || selected.id,
      });
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Fork failed');
    } finally {
      setBusy(false);
    }
  };

  return (
    <Card className="space-y-3 p-4" data-testid="conversion-templates-panel">
      <div className="flex flex-wrap items-center gap-2">
        <h2 className="text-base font-semibold text-gray-900 dark:text-gray-100">
          {PROFILES_CONV_TEMPLATES_HEADING}
        </h2>
        <BetaBadge showHelp />
      </div>
      <p className="text-sm text-gray-600 dark:text-gray-400">
        {PROFILES_CONV_TEMPLATES_HELP}
      </p>

      {error ? (
        <p className="text-sm text-red-600" data-testid="conversion-templates-error">
          {error}
        </p>
      ) : null}

      {loading ? (
        <p className="flex items-center gap-2 text-sm text-gray-500">
          <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
          {PROFILES_CONV_TEMPLATES_LOADING}
        </p>
      ) : items.length === 0 ? (
        <p className="text-sm text-gray-500">{PROFILES_CONV_TEMPLATES_EMPTY}</p>
      ) : (
        <>
          <label className="block text-sm">
            <span className="text-gray-700 dark:text-gray-300">Template</span>
            <select
              className="mt-1 w-full rounded border border-gray-300 bg-white p-2 dark:border-gray-600 dark:bg-gray-900"
              data-testid="conversion-templates-select"
              value={selected?.id ?? ''}
              onChange={(e) => {
                const next = items.find((t) => t.id === e.target.value);
                applySelection(next);
              }}
            >
              {items.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.name} · {t.access} · {t.id}
                </option>
              ))}
            </select>
          </label>

          <div className="space-y-2" data-testid="conversion-templates-slots">
            {slots.map((slot, index) => (
              <div
                key={slot.id}
                draggable
                onDragStart={() => setDragIndex(index)}
                onDragOver={(e) => e.preventDefault()}
                onDrop={() => onDrop(index)}
                className="flex cursor-grab items-center gap-2 rounded border border-gray-200 p-2 dark:border-gray-700"
                data-testid={`conversion-template-slot-${slot.id}`}
              >
                <span className="text-xs text-gray-400" aria-hidden>
                  ::
                </span>
                <span className="flex-1 text-sm">
                  {slot.label} · {slot.type}
                  {slot.iwxxmField ? ` → ${slot.iwxxmField}` : ''}
                </span>
              </div>
            ))}
            <div className="flex gap-2">
              <button
                type="button"
                className="rounded border px-2 py-1 text-sm"
                data-testid="conversion-templates-move-up"
                aria-label={PROFILES_CONV_TEMPLATES_MOVE_UP}
                onClick={() => moveSelected(-1)}
              >
                ↑
              </button>
              <button
                type="button"
                className="rounded border px-2 py-1 text-sm"
                data-testid="conversion-templates-move-down"
                aria-label={PROFILES_CONV_TEMPLATES_MOVE_DOWN}
                onClick={() => moveSelected(1)}
              >
                ↓
              </button>
            </div>
          </div>

          <label className="block text-sm">
            <span className="text-gray-700 dark:text-gray-300">
              {PROFILES_CONV_TEMPLATES_FOCUS}
            </span>
            <input
              className="mt-1 w-full rounded border border-gray-300 bg-white p-2 dark:border-gray-600 dark:bg-gray-900"
              data-testid="conversion-templates-focus"
              value={focusGroup}
              onChange={(e) => setFocusGroup(e.target.value)}
            />
          </label>

          <label className="block text-sm">
            <span className="text-gray-700 dark:text-gray-300">
              {PROFILES_CONV_TEMPLATES_COMMENTS}
            </span>
            <textarea
              className="mt-1 w-full rounded border border-gray-300 bg-white p-2 dark:border-gray-600 dark:bg-gray-900"
              data-testid="conversion-templates-comments"
              rows={2}
              value={comments}
              onChange={(e) => setComments(e.target.value)}
            />
          </label>

          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              className="rounded bg-sky-700 px-3 py-1.5 text-sm text-white disabled:opacity-50"
              data-testid="conversion-templates-preview"
              disabled={busy}
              onClick={() => void runPreview()}
            >
              {PROFILES_CONV_TEMPLATES_PREVIEW}
            </button>
            <button
              type="button"
              className="rounded border px-3 py-1.5 text-sm disabled:opacity-50"
              data-testid="conversion-templates-fork"
              disabled={busy}
              onClick={() => void forkSelected()}
            >
              {PROFILES_CONV_TEMPLATES_FORK}
            </button>
          </div>

          {preview ? (
            <div
              className="space-y-2 rounded bg-gray-50 p-3 text-sm dark:bg-gray-900"
              data-testid="conversion-templates-preview-result"
            >
              <p>Matched: {preview.matched ? 'yes' : 'no'}</p>
              <pre className="overflow-auto whitespace-pre-wrap text-xs">
                {preview.xmlBlock}
              </pre>
            </div>
          ) : null}
        </>
      )}
    </Card>
  );
}

/**
 * Conversion templates authoring panel (parameterizable TAC→IWXXM bridge).
 * Phase A: hide machine ids, token modes Convert|Decode-only|Skip, Advanced pattern.
 */

import { Loader2 } from 'lucide-react';
import { useCallback, useEffect, useState } from 'react';

import { Card } from './ui/card';
import { BetaBadge } from './BetaBadge';
import { MappingBridge } from './MappingBridge';
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
  PROFILES_CONV_TEMPLATES_ADVANCED,
  PROFILES_CONV_TEMPLATES_ADVANCED_HINT,
  PROFILES_CONV_TEMPLATES_COMMENTS,
  PROFILES_CONV_TEMPLATES_EMPTY,
  PROFILES_CONV_TEMPLATES_FOCUS,
  PROFILES_CONV_TEMPLATES_FORK,
  PROFILES_CONV_TEMPLATES_GLOSS,
  PROFILES_CONV_TEMPLATES_HEADING,
  PROFILES_CONV_TEMPLATES_HELP,
  PROFILES_CONV_TEMPLATES_LOADING,
  PROFILES_CONV_TEMPLATES_MODE,
  PROFILES_CONV_TEMPLATES_MODE_CONVERT,
  PROFILES_CONV_TEMPLATES_MODE_DECODE,
  PROFILES_CONV_TEMPLATES_MODE_SKIP,
  PROFILES_CONV_TEMPLATES_MOVE_DOWN,
  PROFILES_CONV_TEMPLATES_MOVE_UP,
  PROFILES_CONV_TEMPLATES_PREVIEW,
  PROFILES_CONV_TEMPLATES_SELECT,
} from '../../utils/conversionProfilesCopy';

export type ConversionTemplatesPanelProps = {
  accessToken: string;
};

const MODE_OPTIONS = [
  { value: 'convert', label: PROFILES_CONV_TEMPLATES_MODE_CONVERT },
  { value: 'decode_only', label: PROFILES_CONV_TEMPLATES_MODE_DECODE },
  { value: 'skip', label: PROFILES_CONV_TEMPLATES_MODE_SKIP },
] as const;

function accessLabel(access: string): string {
  return access === 'first_party' ? 'built-in' : 'custom';
}

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
  const [selectedSlotId, setSelectedSlotId] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [advancedOpen, setAdvancedOpen] = useState(false);

  const selected = items.find((t) => t.id === selectedId) ?? items[0];

  const applySelection = useCallback((tmpl: ConversionTemplateOut) => {
    setSelectedId(tmpl.id);
    const nextSlots = (tmpl.slots ?? []).map((s) => ({
      ...s,
      mode: s.mode || 'convert',
      gloss: s.gloss || '',
    }));
    setSlots(nextSlots);
    setSelectedSlotId(nextSlots[0]?.id ?? null);
    setFocusGroup(tmpl.sample || '18012G20KT');
    setPreview(null);
  }, []);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await listConversionTemplates(accessToken);
      setItems(res.items);
      const first = res.items[0];
      if (first) applySelection(first);
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
    const idx = selectedSlotId ? slots.findIndex((s) => s.id === selectedSlotId) : 0;
    if (idx < 0) return;
    const nextIdx = idx + delta;
    if (nextIdx < 0 || nextIdx >= slots.length) return;
    const reordered = reorderConversionTemplateSlots(slots, idx, nextIdx);
    setSlots(reordered);
    setSelectedSlotId(reordered[nextIdx]?.id ?? selectedSlotId);
  };

  const onDrop = (toIndex: number) => {
    if (dragIndex === null) return;
    setSlots(reorderConversionTemplateSlots(slots, dragIndex, toIndex));
    setDragIndex(null);
  };

  const updateSlot = (slotId: string, patch: Partial<ConversionTemplateSlot>) => {
    setSlots((prev) => prev.map((s) => (s.id === slotId ? { ...s, ...patch } : s)));
  };

  const runPreview = async (tmpl: ConversionTemplateOut) => {
    setBusy(true);
    setError(null);
    try {
      const res = await previewConversionTemplate(accessToken, {
        templateId: tmpl.id,
        focusGroup,
        slots,
        iwxxmBlock: tmpl.iwxxmBlock,
      });
      setPreview(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Preview failed');
    } finally {
      setBusy(false);
    }
  };

  const forkSelected = async (tmpl: ConversionTemplateOut) => {
    setBusy(true);
    setError(null);
    try {
      const slug = `fork-${tmpl.slug}-${Date.now().toString(36)}`.slice(0, 120);
      await createConversionTemplate(accessToken, {
        slug,
        name: `${tmpl.name} (custom)`,
        iwxxmBlock: tmpl.iwxxmBlock,
        slots,
        sample: focusGroup,
        comments: comments || undefined,
        forkOf: tmpl.access === 'first_party' ? tmpl.id : tmpl.forkOf || tmpl.id,
      });
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Fork failed');
    } finally {
      setBusy(false);
    }
  };

  // mode is normalized in applySelection; treat missing as convert for safety.
  const localSkipChips = slots.filter((s) => s.mode === 'skip');
  const previewSkipped = preview?.skipped?.length
    ? preview.skipped
    : localSkipChips.map((s) => ({
        slot: s.id,
        label: s.label,
        gloss: s.gloss || s.label,
      }));

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
      ) : !selected ? (
        <p className="text-sm text-gray-500">{PROFILES_CONV_TEMPLATES_EMPTY}</p>
      ) : (
        <>
          <label className="block text-sm">
            <span className="text-gray-700 dark:text-gray-300">
              {PROFILES_CONV_TEMPLATES_SELECT}
            </span>
            <select
              className="mt-1 w-full rounded border border-gray-300 bg-white p-2 dark:border-gray-600 dark:bg-gray-900"
              data-testid="conversion-templates-select"
              value={selected.id}
              onChange={(e) => {
                const next = items.find((t) => t.id === e.target.value);
                if (next) applySelection(next);
              }}
            >
              {items.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.name} · {accessLabel(t.access)}
                </option>
              ))}
            </select>
          </label>

          <div className="space-y-2" data-testid="template-block-builder">
            <div className="space-y-2" data-testid="conversion-templates-slots">
              {slots.map((slot, index) => (
                <div
                  key={slot.id}
                  role="button"
                  tabIndex={0}
                  draggable
                  onClick={() => setSelectedSlotId(slot.id)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      e.preventDefault();
                      setSelectedSlotId(slot.id);
                    }
                  }}
                  onDragStart={() => {
                    setDragIndex(index);
                    setSelectedSlotId(slot.id);
                  }}
                  onDragOver={(e) => e.preventDefault()}
                  onDrop={() => onDrop(index)}
                  className={`space-y-2 rounded border p-2 ${
                    selectedSlotId === slot.id
                      ? 'border-blue-500 dark:border-blue-400'
                      : 'border-gray-200 dark:border-gray-700'
                  }`}
                  data-testid={`conversion-template-slot-${slot.id}`}
                  aria-pressed={selectedSlotId === slot.id}
                >
                  <div className="flex cursor-grab items-center gap-2">
                    <span className="text-xs text-gray-400" aria-hidden>
                      ::
                    </span>
                    <span className="flex-1 text-sm">
                      {slot.label} · {slot.type}
                      {slot.iwxxmField ? ` → ${slot.iwxxmField}` : ''}
                    </span>
                  </div>
                  <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
                    <label className="block text-xs">
                      <span className="text-gray-600 dark:text-gray-400">
                        {PROFILES_CONV_TEMPLATES_MODE}
                      </span>
                      <select
                        className="mt-1 w-full rounded border border-gray-300 bg-white p-1.5 dark:border-gray-600 dark:bg-gray-900"
                        data-testid={`conversion-template-slot-mode-${slot.id}`}
                        value={slot.mode}
                        onChange={(e) => updateSlot(slot.id, { mode: e.target.value })}
                      >
                        {MODE_OPTIONS.map((opt) => (
                          <option key={opt.value} value={opt.value}>
                            {opt.label}
                          </option>
                        ))}
                      </select>
                    </label>
                    <label className="block text-xs">
                      <span className="text-gray-600 dark:text-gray-400">
                        {PROFILES_CONV_TEMPLATES_GLOSS}
                      </span>
                      <input
                        className="mt-1 w-full rounded border border-gray-300 bg-white p-1.5 dark:border-gray-600 dark:bg-gray-900"
                        data-testid={`conversion-template-slot-gloss-${slot.id}`}
                        value={slot.gloss || ''}
                        onChange={(e) => updateSlot(slot.id, { gloss: e.target.value })}
                        placeholder="e.g. wind direction degrees"
                      />
                    </label>
                  </div>
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

          <details
            className="rounded border border-gray-200 p-2 dark:border-gray-700"
            data-testid="conversion-templates-advanced"
            open={advancedOpen}
            onToggle={(e) => setAdvancedOpen((e.target as HTMLDetailsElement).open)}
          >
            <summary className="cursor-pointer text-sm font-medium">
              {PROFILES_CONV_TEMPLATES_ADVANCED}
            </summary>
            <p className="mt-2 text-xs text-gray-500">
              {PROFILES_CONV_TEMPLATES_ADVANCED_HINT}
            </p>
            <pre
              className="mt-2 overflow-auto whitespace-pre-wrap text-xs text-gray-600 dark:text-gray-400"
              data-testid="conversion-templates-advanced-pattern"
            >
              {preview?.compiledPattern ||
                '(run Preview mapping to see the compiled pattern)'}
            </pre>
          </details>

          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              className="rounded bg-sky-700 px-3 py-1.5 text-sm text-white disabled:opacity-50"
              data-testid="conversion-templates-preview"
              disabled={busy}
              onClick={() => void runPreview(selected)}
            >
              {PROFILES_CONV_TEMPLATES_PREVIEW}
            </button>
            <button
              type="button"
              className="rounded border px-3 py-1.5 text-sm disabled:opacity-50"
              data-testid="conversion-templates-fork"
              disabled={busy}
              onClick={() => void forkSelected(selected)}
            >
              {PROFILES_CONV_TEMPLATES_FORK}
            </button>
          </div>

          {preview || localSkipChips.length ? (
            <div data-testid="conversion-templates-preview-result">
              <MappingBridge
                tacGroup={focusGroup}
                templateName={selected.name}
                matched={preview ? preview.matched : null}
                iwxxmBlock={preview?.xmlBlock ?? ''}
                skipChips={previewSkipped.map((s) => ({
                  label: s.label || s.slot || 'skip',
                  gloss: s.gloss,
                }))}
              />
            </div>
          ) : null}
        </>
      )}
    </Card>
  );
}

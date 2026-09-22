/**
 * Conversion templates authoring panel (parameterizable TAC→IWXXM bridge).
 * P1: searchable catalog, renamable slots, foundation read-only, custom save.
 */

import { Loader2 } from 'lucide-react';
import { useCallback, useEffect, useMemo, useState } from 'react';

import { Card } from './ui/card';
import { BetaBadge } from './BetaBadge';
import { MappingBridge } from './MappingBridge';
import {
  ConversionCatalogPicker,
  type ConversionCatalogCard,
} from './ConversionCatalogPicker';
import {
  createConversionTemplate,
  listConversionTemplates,
  previewConversionTemplate,
  updateConversionTemplate,
  type ConversionTemplateOut,
  type ConversionTemplatePreviewResponse,
  type ConversionTemplateSlot,
} from '../../utils/conversionProfilesApi';
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
  PROFILES_CONV_TEMPLATES_PREVIEW,
  PROFILES_CONV_TEMPLATES_READONLY,
  PROFILES_CONV_TEMPLATES_SAVE,
  PROFILES_CONV_TEMPLATES_SAVED,
  PROFILES_CONV_TEMPLATES_SEARCH,
  PROFILES_CONV_TEMPLATES_SEARCH_PLACEHOLDER,
  PROFILES_CONV_TEMPLATES_SELECT,
  PROFILES_CONV_TEMPLATES_SLOT_LABEL,
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
  const [selectedSlotId, setSelectedSlotId] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [advancedOpen, setAdvancedOpen] = useState(false);
  const [templateQuery, setTemplateQuery] = useState('');
  const [catalogCardId, setCatalogCardId] = useState<string | null>(null);
  const [saveNote, setSaveNote] = useState<string | null>(null);

  const selected = items.find((t) => t.id === selectedId) ?? items[0];
  const isBuiltin = selected?.access === 'first_party';
  const editable = Boolean(selected && !isBuiltin);

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
    setComments(tmpl.comments || '');
    setPreview(null);
    setSaveNote(null);
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

  const filteredTemplates = useMemo(() => {
    const q = templateQuery.trim().toLowerCase();
    const list = !q
      ? items
      : items.filter(
          (t) =>
            t.name.toLowerCase().includes(q) ||
            t.iwxxmBlock.toLowerCase().includes(q) ||
            t.slug.toLowerCase().includes(q) ||
            t.id.toLowerCase().includes(q),
        );
    if (selected && !list.some((t) => t.id === selected.id)) {
      return [selected, ...list];
    }
    return list;
  }, [items, templateQuery, selected]);

  const groupedTemplates = useMemo(() => {
    const groups = new Map<string, ConversionTemplateOut[]>();
    for (const tmpl of filteredTemplates) {
      const key = tmpl.iwxxmBlock || 'other';
      const list = groups.get(key) ?? [];
      list.push(tmpl);
      groups.set(key, list);
    }
    return Array.from(groups.entries()).sort(([a], [b]) => a.localeCompare(b));
  }, [filteredTemplates]);

  const updateSlot = (slotId: string, patch: Partial<ConversionTemplateSlot>) => {
    /* v8 ignore start -- Save/edit controls are not rendered for first_party */
    if (!editable) {
      return;
    }
    /* v8 ignore stop */
    setSlots((prev) => prev.map((s) => (s.id === slotId ? { ...s, ...patch } : s)));
    setSaveNote(null);
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
      const created = await createConversionTemplate(accessToken, {
        slug,
        name: `${tmpl.name} (custom)`,
        iwxxmBlock: tmpl.iwxxmBlock,
        slots,
        sample: focusGroup,
        comments: comments || tmpl.comments || undefined,
        forkOf: tmpl.id,
      });
      const res = await listConversionTemplates(accessToken);
      setItems(res.items);
      applySelection(created);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Fork failed');
    } finally {
      setBusy(false);
    }
  };

  const saveSelected = async (tmpl: ConversionTemplateOut) => {
    /* v8 ignore start -- Save button is not rendered for first_party */
    if (tmpl.access === 'first_party') {
      setError(PROFILES_CONV_TEMPLATES_READONLY);
      return;
    }
    /* v8 ignore stop */
    setBusy(true);
    setError(null);
    try {
      const updated = await updateConversionTemplate(accessToken, tmpl.id, {
        slots,
        sample: focusGroup,
        comments: comments || null,
        iwxxmBlock: tmpl.iwxxmBlock,
        name: tmpl.name,
      });
      setItems((prev) => prev.map((t) => (t.id === updated.id ? updated : t)));
      applySelection(updated);
      setSaveNote(PROFILES_CONV_TEMPLATES_SAVED);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Save failed');
    } finally {
      setBusy(false);
    }
  };

  const onCatalogSelect = (card: ConversionCatalogCard) => {
    setCatalogCardId(card.id);
    const match =
      items.find((t) => t.iwxxmBlock === card.id) ||
      items.find((t) => t.name.toLowerCase() === card.label.toLowerCase()) ||
      items.find((t) => t.iwxxmBlock.toLowerCase().includes(card.label.toLowerCase()));
    /* v8 ignore start -- catalog cards may not map to a loaded template */
    if (match) {
      applySelection(match);
    }
    /* v8 ignore stop */
    setTemplateQuery(card.label);
  };

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

      <ConversionCatalogPicker
        accessToken={accessToken}
        selectedCardId={catalogCardId}
        onSelectCard={onCatalogSelect}
      />

      {error ? (
        <p className="text-sm text-red-600" data-testid="conversion-templates-error">
          {error}
        </p>
      ) : null}
      {saveNote ? (
        <p className="text-sm text-green-700" data-testid="conversion-templates-saved">
          {saveNote}
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
              {PROFILES_CONV_TEMPLATES_SEARCH}
            </span>
            <input
              type="search"
              className="mt-1 w-full rounded border border-gray-300 bg-white p-2 dark:border-gray-600 dark:bg-gray-900"
              data-testid="conversion-templates-search"
              placeholder={PROFILES_CONV_TEMPLATES_SEARCH_PLACEHOLDER}
              value={templateQuery}
              onChange={(e) => setTemplateQuery(e.target.value)}
            />
          </label>

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
              {groupedTemplates.map(([group, tmpls]) => (
                <optgroup key={group} label={group}>
                  {tmpls.map((t) => (
                    <option key={t.id} value={t.id}>
                      {t.name} · {accessLabel(t.access)}
                    </option>
                  ))}
                </optgroup>
              ))}
            </select>
          </label>

          {isBuiltin ? (
            <p
              className="rounded border border-amber-200 bg-amber-50 p-2 text-xs text-amber-900 dark:border-amber-800 dark:bg-amber-950/40 dark:text-amber-100"
              data-testid="conversion-templates-readonly"
            >
              {PROFILES_CONV_TEMPLATES_READONLY}
            </p>
          ) : null}

          <div className="space-y-2" data-testid="template-block-builder">
            <div className="space-y-2" data-testid="conversion-templates-slots">
              {slots.map((slot) => (
                <div
                  key={slot.id}
                  role="button"
                  tabIndex={0}
                  onClick={() => setSelectedSlotId(slot.id)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      e.preventDefault();
                      setSelectedSlotId(slot.id);
                    }
                  }}
                  className={`space-y-2 rounded border p-2 ${
                    selectedSlotId === slot.id
                      ? 'border-blue-500 dark:border-blue-400'
                      : 'border-gray-200 dark:border-gray-700'
                  }`}
                  data-testid={`conversion-template-slot-${slot.id}`}
                  aria-pressed={selectedSlotId === slot.id}
                >
                  <div className="flex items-center gap-2 text-xs text-gray-500">
                    <span>
                      {slot.type}
                      {slot.iwxxmField ? ` → ${slot.iwxxmField}` : ''}
                    </span>
                  </div>
                  <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
                    <label className="block text-xs">
                      <span className="text-gray-600 dark:text-gray-400">
                        {PROFILES_CONV_TEMPLATES_SLOT_LABEL}
                      </span>
                      <input
                        className="mt-1 w-full rounded border border-gray-300 bg-white p-1.5 dark:border-gray-600 dark:bg-gray-900"
                        data-testid={`conversion-template-slot-label-${slot.id}`}
                        value={slot.label}
                        disabled={!editable}
                        onChange={(e) => updateSlot(slot.id, { label: e.target.value })}
                      />
                    </label>
                    <label className="block text-xs">
                      <span className="text-gray-600 dark:text-gray-400">
                        {PROFILES_CONV_TEMPLATES_MODE}
                      </span>
                      <select
                        className="mt-1 w-full rounded border border-gray-300 bg-white p-1.5 dark:border-gray-600 dark:bg-gray-900"
                        data-testid={`conversion-template-slot-mode-${slot.id}`}
                        value={slot.mode}
                        disabled={!editable}
                        onChange={(e) => updateSlot(slot.id, { mode: e.target.value })}
                      >
                        {MODE_OPTIONS.map((opt) => (
                          <option key={opt.value} value={opt.value}>
                            {opt.label}
                          </option>
                        ))}
                      </select>
                    </label>
                    <label className="block text-xs sm:col-span-2">
                      <span className="text-gray-600 dark:text-gray-400">
                        {PROFILES_CONV_TEMPLATES_GLOSS}
                      </span>
                      <input
                        className="mt-1 w-full rounded border border-gray-300 bg-white p-1.5 dark:border-gray-600 dark:bg-gray-900"
                        data-testid={`conversion-template-slot-gloss-${slot.id}`}
                        value={slot.gloss || ''}
                        disabled={!editable}
                        onChange={(e) => updateSlot(slot.id, { gloss: e.target.value })}
                        placeholder="e.g. wind direction degrees"
                      />
                    </label>
                  </div>
                </div>
              ))}
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
              disabled={!editable}
              onChange={(e) => {
                setComments(e.target.value);
                setSaveNote(null);
              }}
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
            {editable ? (
              <button
                type="button"
                className="rounded border border-sky-700 px-3 py-1.5 text-sm text-sky-800 disabled:opacity-50 dark:text-sky-200"
                data-testid="conversion-templates-save"
                disabled={busy}
                onClick={() => void saveSelected(selected)}
              >
                {PROFILES_CONV_TEMPLATES_SAVE}
              </button>
            ) : null}
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

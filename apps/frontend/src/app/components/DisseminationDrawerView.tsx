/* eslint-disable @typescript-eslint/ban-ts-comment, @typescript-eslint/no-explicit-any, complexity */
// @ts-nocheck — mechanical line-count split
/** Presentational DisseminationDrawer view. */
import { Button } from './ui/button';
import { Label } from './ui/label';
import { BetaBadge } from './BetaBadge';
import { DisseminationProgressRow } from './DisseminationProgressRow';
import { DRAWER_SINK_TYPES, sinkTypeLabel, type SinkType } from '@/utils/dissemination';
import {
  canActOnSelection,
  clearSelection,
  selectAll,
  toggleSelection,
} from '@/utils/exportSelection';
import {
  DISSEMINATION_TEMPLATE_HELP,
  DISSEMINATION_TEMPLATE_LABEL,
  DISSEMINATION_TEMPLATE_NONE,
} from '@/utils/conversionProfilesCopy';
import {
  coerceExchangeProfile,
  EXCHANGE_PROFILE_OPTIONS,
} from '@/utils/exchangeProfile';
import { progressRowState } from '@/utils/disseminationDrawerHelpers';

export type DisseminationDrawerViewProps = Record<string, any>;

/**
 * DisseminationDrawerView.
 */
export function DisseminationDrawerView({
  exchangeProfile,
  onExchangeProfileChange,
  sinkType,
  setSinkType,
  uri,
  setUri,
  ddl,
  setDdl,
  byocParamsJson,
  setByocParamsJson,
  selectionError,
  setForceExpanded,
  setExpandKey,
  error,
  rowState,
  setRowState,
  lastResults,
  setLastResults,
  templates,
  templateLoadError,
  templatesEnabled,
  selectedTemplateId,
  setExchangeProfile,
  candidates,
  selectedIds,
  setSelectedIds,
  needsUri,
  canAct,
  showSelectionPanel,
  candidateKey,
  selectedCandidates,
  applyTemplate,
  runQueue,
  onDropFiles,
  closeDrawer,
  busy: _busy,
}: DisseminationDrawerViewProps) {
  return (
    <div
      className="fixed inset-0 z-50 flex justify-end bg-black/40"
      data-testid="dissemination-drawer"
      role="dialog"
      aria-modal="true"
      aria-labelledby="dissemination-drawer-title"
    >
      <button
        type="button"
        className="absolute inset-0 cursor-default"
        aria-label="Close dissemination drawer backdrop"
        data-testid="dissemination-drawer-backdrop"
        onClick={closeDrawer}
      />
      <aside
        className="relative z-10 flex h-full w-full max-w-md flex-col gap-4 overflow-y-auto border-l border-gray-200 bg-white p-4 shadow-xl dark:border-gray-700 dark:bg-gray-900"
        onClick={(e) => e.stopPropagation()}
      >
        <header className="flex items-start justify-between gap-2">
          <div className="space-y-2">
            <div className="flex flex-wrap items-center gap-2">
              <h2
                id="dissemination-drawer-title"
                className="text-lg font-semibold text-gray-900 dark:text-white"
              >
                Dissemination
              </h2>
              <BetaBadge showHelp />
            </div>
          </div>
          <Button
            type="button"
            variant="ghost"
            size="sm"
            data-testid="dissemination-drawer-close"
            onClick={closeDrawer}
          >
            Close
          </Button>
        </header>

        <div className="space-y-2">
          {templatesEnabled && templates.length > 0 ? (
            <>
              <Label htmlFor="dissemination-template-select">
                {DISSEMINATION_TEMPLATE_LABEL}
              </Label>
              <select
                id="dissemination-template-select"
                data-testid="dissemination-template-select"
                className="w-full rounded border border-gray-300 bg-white px-2 py-2 text-sm dark:border-gray-600 dark:bg-gray-800 dark:text-white"
                value={selectedTemplateId}
                onChange={(e) => applyTemplate(e.target.value)}
              >
                <option value="">{DISSEMINATION_TEMPLATE_NONE}</option>
                {templates.map((template) => (
                  <option key={template.id} value={template.id}>
                    {template.name} ({template.sinkType})
                  </option>
                ))}
              </select>
              <p
                className="text-xs text-gray-500 dark:text-gray-400"
                data-testid="dissemination-template-help"
              >
                {DISSEMINATION_TEMPLATE_HELP}
              </p>
            </>
          ) : null}
          {templatesEnabled && templateLoadError ? (
            <p
              className="text-xs text-amber-700 dark:text-amber-400"
              data-testid="dissemination-template-error"
            >
              {templateLoadError}
            </p>
          ) : null}
          <Label htmlFor="dissemination-sink-type">Destination sink</Label>
          <select
            id="dissemination-sink-type"
            data-testid="dissemination-sink-chooser"
            className="w-full rounded border border-gray-300 bg-white px-2 py-2 text-sm dark:border-gray-600 dark:bg-gray-800 dark:text-white"
            value={sinkType}
            onChange={(e) => {
              setSinkType(e.target.value as SinkType);
              setLastResults([]);
              setRowState({});
            }}
          >
            {DRAWER_SINK_TYPES.map((sink) => (
              <option
                key={sink}
                value={sink}
                data-testid={`dissemination-sink-option-${sink}`}
              >
                {sinkTypeLabel(sink)}
              </option>
            ))}
          </select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="dissemination-exchange-profile">Exchange profile</Label>
          <select
            id="dissemination-exchange-profile"
            data-testid="dissemination-exchange-profile"
            aria-label="Exchange profile"
            className="w-full rounded border border-gray-300 bg-white px-2 py-2 text-sm dark:border-gray-600 dark:bg-gray-800 dark:text-white"
            value={exchangeProfile}
            onChange={(e) => {
              const next = coerceExchangeProfile(e.target.value);
              setExchangeProfile(next);
              onExchangeProfileChange?.(next);
              setLastResults([]);
              setRowState({});
            }}
          >
            {EXCHANGE_PROFILE_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
          <p
            className="text-xs text-gray-500 dark:text-gray-400"
            data-testid="dissemination-exchange-profile-help"
          >
            Used when converting TAC before send. Does not choose destinations or
            credentials.
          </p>
        </div>

        {needsUri ? (
          <div className="space-y-2">
            <Label htmlFor="dissemination-uri">Destination URI</Label>
            <input
              id="dissemination-uri"
              data-testid="dissemination-uri-input"
              type="text"
              autoComplete="off"
              spellCheck={false}
              placeholder="postgresql://user:pass@host:5432/db"
              className="w-full rounded border border-gray-300 bg-white px-2 py-2 font-mono text-sm dark:border-gray-600 dark:bg-gray-800 dark:text-white"
              value={uri}
              onChange={(e) => {
                setUri(e.target.value);
                setLastResults([]);
                setRowState({});
              }}
            />
            <label className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
              <input
                type="checkbox"
                data-testid="dissemination-ddl-toggle"
                checked={ddl}
                onChange={(e) => {
                  setDdl(e.target.checked);
                }}
              />
              Create-if-missing (DDL)
            </label>
          </div>
        ) : (
          <div className="space-y-2">
            <Label htmlFor="dissemination-byoc-params">
              BYOC params (JSON, memory-only) — {sinkTypeLabel(sinkType)}
            </Label>
            <textarea
              id="dissemination-byoc-params"
              data-testid="dissemination-byoc-params"
              className="min-h-[6rem] w-full rounded border border-gray-300 bg-white px-2 py-2 font-mono text-sm dark:border-gray-600 dark:bg-gray-800 dark:text-white"
              spellCheck={false}
              autoComplete="off"
              placeholder='{"endpoint":"…","token":"…"}'
              value={byocParamsJson}
              onChange={(e) => {
                setByocParamsJson(e.target.value);
                setLastResults([]);
                setRowState({});
              }}
            />
            <p
              className="text-xs text-gray-500 dark:text-gray-400"
              data-testid="dissemination-non-db-hint"
            >
              Credentials stay in browser memory for this session only; never stored in
              work history.
            </p>
          </div>
        )}

        <div
          className="rounded border border-dashed border-gray-300 p-3 text-sm dark:border-gray-600"
          data-testid="dissemination-dropzone"
          onDragOver={(e) => {
            e.preventDefault();
          }}
          onDrop={(e) => {
            e.preventDefault();
            onDropFiles(e.dataTransfer.files);
          }}
        >
          <Label htmlFor="dissemination-file-input">
            Drag-drop IWXXM/TAC or choose file
          </Label>
          <input
            id="dissemination-file-input"
            data-testid="dissemination-file-input"
            type="file"
            accept=".xml,.txt,.tac,text/xml,text/plain"
            className="mt-2 block w-full text-sm"
            onChange={(e) => onDropFiles(e.target.files)}
          />
          {candidates.length > 0 && (
            <p
              className="mt-2 text-xs text-gray-600 dark:text-gray-400"
              data-testid="dissemination-payload-status"
            >
              {candidates.length} candidate(s) ready
            </p>
          )}
        </div>

        {candidates.length === 1 && !showSelectionPanel && (
          <button
            type="button"
            className="text-left text-xs text-blue-600 underline dark:text-blue-400"
            data-testid="dissemination-selection-expand"
            onClick={() => {
              setExpandKey(candidateKey);
              setForceExpanded(true);
            }}
          >
            Export selection (1 file selected)
          </button>
        )}

        {showSelectionPanel && (
          <div
            className="space-y-2 rounded border border-gray-200 p-3 dark:border-gray-700"
            data-testid="dissemination-export-selection"
          >
            <div className="flex items-center justify-between gap-2">
              <Label>Export selection</Label>
              <div className="flex gap-2">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  data-testid="dissemination-select-all"
                  onClick={() => {
                    const result = selectAll(candidates);
                    setSelectedIds(result.selected, result.error ?? null);
                  }}
                >
                  Select all
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  data-testid="dissemination-clear-selection"
                  onClick={() => {
                    setSelectedIds(clearSelection(), null);
                  }}
                >
                  Clear
                </Button>
              </div>
            </div>
            <ul className="space-y-1">
              {candidates.map((c) => (
                <li key={c.id}>
                  <label className="flex items-center gap-2 text-sm text-gray-800 dark:text-gray-200">
                    <input
                      type="checkbox"
                      data-testid={`dissemination-candidate-${c.id}`}
                      checked={selectedIds.includes(c.id)}
                      onChange={() => {
                        const result = toggleSelection(selectedIds, c.id);
                        setSelectedIds(result.selected, result.error ?? null);
                      }}
                    />
                    <span className="truncate">
                      {c.name}{' '}
                      <span className="text-xs text-gray-500">({c.source})</span>
                    </span>
                  </label>
                </li>
              ))}
            </ul>
            {!canActOnSelection(selectedIds) && (
              <p
                className="text-xs text-amber-700 dark:text-amber-400"
                data-testid="dissemination-empty-selection"
              >
                Select at least one file to Disseminate or Preflight.
              </p>
            )}
            {selectionError && (
              <p
                className="text-xs text-red-600 dark:text-red-400"
                data-testid="dissemination-selection-cap-error"
                role="alert"
              >
                {selectionError}
              </p>
            )}
          </div>
        )}

        <div className="flex flex-wrap gap-2">
          <Button
            type="button"
            data-testid="dissemination-send-button"
            disabled={!canAct}
            onClick={() => void runQueue('disseminate')}
          >
            Disseminate
          </Button>
          <Button
            type="button"
            variant="outline"
            data-testid="dissemination-preflight-button"
            disabled={!canAct}
            onClick={() => void runQueue('preflight_only')}
          >
            Preflight only
          </Button>
        </div>

        {(Object.keys(rowState).length > 0 || lastResults.length > 0) && (
          <div className="space-y-2" data-testid="dissemination-progress-list">
            {selectedCandidates.map((c) => {
              const state = progressRowState(rowState, c.id);
              return (
                <DisseminationProgressRow
                  key={c.id}
                  candidateId={c.id}
                  name={c.name}
                  status={state.status}
                  detail={state.detail}
                  sinkType={sinkType}
                />
              );
            })}
          </div>
        )}

        {error && (
          <p
            className="text-sm text-red-600 dark:text-red-400"
            data-testid="dissemination-error"
            role="alert"
          >
            {error}
          </p>
        )}

        {lastResults.some((r) => r.status === 'success') && (
          <p
            className="text-sm text-green-700 dark:text-green-400"
            data-testid="dissemination-send-success"
          >
            {lastResults.filter((r) => r.status === 'success').length} file(s) succeeded
          </p>
        )}
      </aside>
    </div>
  );
}

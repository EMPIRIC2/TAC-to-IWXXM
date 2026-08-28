/* eslint-disable react-refresh/only-export-components */
/**
 * Dissemination drawer (F16–F19 / UJ-027–030) — multi-select export, interleaved
 * Disseminate, per-file progress (EV-018 / #785).
 */

import { useCallback, useMemo, useState } from 'react';
import { Button } from './ui/button';
import { Label } from './ui/label';
import {
  DisseminationProgressRow,
  type ProgressRowStatus,
} from './DisseminationProgressRow';
import {
  DRAWER_SINK_TYPES,
  DB_SINK_TYPES,
  disseminationPreflight,
  disseminationSend,
  sinkTypeLabel,
  type SinkType,
} from '/utils/dissemination';
import {
  buildExportCandidates,
  canActOnSelection,
  clearSelection,
  initialSelectedIds,
  selectAll,
  toggleSelection,
  type ExportCandidate,
  type ExportCandidateInput,
} from '/utils/exportSelection';
import {
  runDisseminationQueue,
  type DisseminationFileResult,
} from '/utils/disseminationQueue';
import { firstDropFile, resolveDisseminationProduct } from '@/utils/fileInputHelpers';

export { firstDropFile, resolveDisseminationProduct } from '@/utils/fileInputHelpers';

export interface DisseminationDrawerProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  /** Converted IWXXM XML (convert-then-send path). */
  iwxxmXml?: string;
  /** Optional TAC text for drag-drop / convert paths. */
  tacText?: string;
  product?: string;
  /** Extra current-session outputs (beyond primary convert props). */
  sessionOutputs?: ExportCandidateInput[];
}

interface RowUiState {
  status: ProgressRowStatus;
  detail?: string;
}

/** True when a drop FileList has at least one file. */
export function hasDropFiles(files: FileList | null | undefined): boolean {
  return Boolean(files && files.length > 0);
}

/** Normalize FileReader result to text. */
export function dropReaderText(result: string | ArrayBuffer | null): string {
  return String(result ?? '');
}

/** Progress row state with pending fallback. */
export function progressRowState(
  state: Record<string, RowUiState>,
  id: string,
): RowUiState {
  return state[id] ?? { status: 'pending' };
}

/**
 * Drawer UI for BYOC dissemination with multi-file export selection.
 *
 * @param props.open - Whether the drawer panel is visible
 * @param props.onOpenChange - Open-state callback
 * @param props.iwxxmXml - Optional in-session convert result
 * @param props.tacText - Optional TAC payload
 * @param props.product - Product tag for API (default metar)
 * @param props.sessionOutputs - Additional session candidates
 */
export function DisseminationDrawer({
  open,
  onOpenChange,
  iwxxmXml: propIwxxm,
  tacText: propTac,
  product = 'metar',
  sessionOutputs = [],
}: DisseminationDrawerProps) {
  const [sinkType, setSinkType] = useState<SinkType>('postgres');
  const [uri, setUri] = useState('');
  const [ddl, setDdl] = useState(false);
  const [byocParamsJson, setByocParamsJson] = useState('{}');
  const [dropped, setDropped] = useState<ExportCandidateInput[]>([]);
  const [selectedIdsState, setSelectedIdsState] = useState<string[]>([]);
  const [selectionKey, setSelectionKey] = useState('');
  const [selectionError, setSelectionError] = useState<string | null>(null);
  const [forceExpanded, setForceExpanded] = useState(false);
  const [expandKey, setExpandKey] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [rowState, setRowState] = useState<Record<string, RowUiState>>({});
  const [lastResults, setLastResults] = useState<DisseminationFileResult[]>([]);

  const primarySession: ExportCandidateInput[] = useMemo(() => {
    if (!propIwxxm?.trim() && !propTac?.trim()) return [];
    return [
      {
        id: 'session-primary',
        name: propIwxxm?.trim() ? 'session-convert.xml' : 'session-convert.tac',
        source: 'session',
        product,
        iwxxmXml: propIwxxm,
        tacText: propTac,
        status: 'ready',
      },
    ];
  }, [propIwxxm, propTac, product]);

  const candidates: ExportCandidate[] = useMemo(
    () =>
      buildExportCandidates({
        sessionOutputs: [...primarySession, ...sessionOutputs],
        droppedFiles: dropped,
      }),
    [dropped, primarySession, sessionOutputs],
  );

  const candidateKey = candidates.map((c) => c.id).join('|');
  const selectedIds =
    open && selectionKey === candidateKey
      ? selectedIdsState
      : initialSelectedIds(candidates);
  const selectionExpanded =
    expandKey === candidateKey ? forceExpanded : candidates.length > 1;

  const setSelectedIds = useCallback(
    (ids: string[], err?: string | null) => {
      setSelectionKey(candidateKey);
      setSelectedIdsState(ids);
      setSelectionError(err ?? null);
    },
    [candidateKey],
  );

  const needsUri = DB_SINK_TYPES.includes(sinkType);
  const canAct = canActOnSelection(selectedIds) && !(needsUri && !uri.trim()) && !busy;
  const showSelectionPanel = candidates.length > 1 || selectionExpanded;

  const selectedCandidates = useMemo(
    () => candidates.filter((c) => selectedIds.includes(c.id)),
    [candidates, selectedIds],
  );

  const parseByocParams = useCallback((): Record<string, unknown> | null => {
    if (needsUri) return {};
    try {
      const parsed: unknown = JSON.parse(byocParamsJson || '{}');
      if (parsed === null || typeof parsed !== 'object' || Array.isArray(parsed)) {
        setError('BYOC params must be a JSON object (memory-only).');
        return null;
      }
      return parsed as Record<string, unknown>;
    } catch {
      setError('BYOC params JSON is invalid.');
      return null;
    }
  }, [byocParamsJson, needsUri]);

  const runQueue = useCallback(
    async (mode: 'disseminate' | 'preflight_only') => {
      // Selection emptiness is enforced via canAct / disabled buttons.
      const params = parseByocParams();
      if (params === null) return;

      setBusy(true);
      setError(null);
      setLastResults([]);
      const initial: Record<string, RowUiState> = {};
      for (const c of selectedCandidates) {
        initial[c.id] = { status: 'pending' };
      }
      setRowState(initial);

      try {
        const results: DisseminationFileResult[] = [];
        for await (const event of runDisseminationQueue({
          candidates: selectedCandidates,
          mode,
          sink: {
            sinkType,
            uri: needsUri ? uri : undefined,
            ddl: needsUri ? ddl : false,
            product,
            params,
          },
          preflight: async (candidate, sink) =>
            disseminationPreflight({
              sink_type: sink.sinkType,
              uri: sink.uri,
              ddl: sink.ddl,
              product: sink.product,
              params: sink.params,
            }),
          send: async (candidate, handle) =>
            disseminationSend({
              handle,
              iwxxm_xml: candidate.iwxxmXml?.trim() || undefined,
              tac_text: candidate.tacText?.trim() || undefined,
              product: resolveDisseminationProduct(candidate.product, product),
            }),
        })) {
          if (event.type === 'progress') {
            setRowState((prev) => ({
              ...prev,
              [event.candidateId]: { status: event.phase },
            }));
          } else {
            results.push(event.result);
            setRowState((prev) => ({
              ...prev,
              [event.result.candidateId]: {
                status: event.result.status === 'success' ? 'success' : 'failed',
                detail: event.result.detail,
              },
            }));
          }
        }
        setLastResults(results);
        const failed = results.filter((r) => r.status === 'failed');
        if (failed.length > 0) {
          const firstDetail = failed[0]?.detail;
          setError(
            firstDetail
              ? `${failed.length} of ${results.length} file(s) failed: ${firstDetail}`
              : `${failed.length} of ${results.length} file(s) failed — see progress below.`,
          );
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Dissemination failed');
      } finally {
        setBusy(false);
      }
    },
    [ddl, needsUri, parseByocParams, product, selectedCandidates, sinkType, uri],
  );

  const onDropFiles = useCallback(
    (files: FileList | null) => {
      if (!hasDropFiles(files)) return;
      const file = firstDropFile(files!);
      if (!file) return;
      const reader = new FileReader();
      reader.onload = () => {
        const text = dropReaderText(reader.result);
        const name = file.name.toLowerCase();
        const isXml = name.endsWith('.xml') || text.trimStart().startsWith('<');
        const id = `drop-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
        setDropped((prev) => [
          ...prev,
          {
            id,
            name: file.name || (isXml ? 'drop.xml' : 'drop.tac'),
            source: 'drop',
            product,
            iwxxmXml: isXml ? text : undefined,
            tacText: isXml ? undefined : text,
            status: 'ready',
            sizeBytes: text.length,
          },
        ]);
        setLastResults([]);
        setRowState({});
      };
      reader.readAsText(file);
    },
    [product],
  );

  const closeDrawer = useCallback(() => {
    setDropped([]);
    setSelectionKey('');
    setSelectedIdsState([]);
    setSelectionError(null);
    setExpandKey('');
    setForceExpanded(false);
    setRowState({});
    setLastResults([]);
    setError(null);
    onOpenChange(false);
  }, [onOpenChange]);

  if (!open) return null;

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
          <h2
            id="dissemination-drawer-title"
            className="text-lg font-semibold text-gray-900 dark:text-white"
          >
            Dissemination
          </h2>
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

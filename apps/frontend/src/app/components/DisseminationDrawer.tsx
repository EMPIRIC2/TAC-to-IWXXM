/**
 * Dissemination drawer (F16–F19 / UJ-027–030) — sink chooser, preflight diff, Send gate.
 *
 * T6.1 ships the Vitest contract + minimal UI; T6.2 expands drag-drop polish and
 * workbench wiring (E14-10).
 */

import { useCallback, useMemo, useState } from 'react';
import { Button } from './ui/button';
import { Label } from './ui/label';
import {
  DRAWER_SINK_TYPES,
  DB_SINK_TYPES,
  disseminationPreflight,
  disseminationSend,
  isPreflightGreen,
  sinkTypeLabel,
  type PreflightResponse,
  type SinkType,
} from '/utils/dissemination';

export interface DisseminationDrawerProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  accessToken?: string;
  /** Converted IWXXM XML (convert-then-send path). */
  iwxxmXml?: string;
  /** Optional TAC text for drag-drop / convert paths. */
  tacText?: string;
  product?: string;
}

/**
 * Drawer UI for BYOC dissemination: choose sink → preflight → Send when green.
 *
 * @param props.open - Whether the drawer panel is visible
 * @param props.onOpenChange - Open-state callback
 * @param props.accessToken - Bearer JWT (required for preflight/send)
 * @param props.iwxxmXml - Optional in-session convert result
 * @param props.tacText - Optional TAC payload
 * @param props.product - Product tag for API (default metar)
 */
export function DisseminationDrawer({
  open,
  onOpenChange,
  accessToken,
  iwxxmXml: propIwxxm,
  tacText: propTac,
  product = 'metar',
}: DisseminationDrawerProps) {
  const [sinkType, setSinkType] = useState<SinkType>('postgres');
  const [uri, setUri] = useState('');
  const [ddl, setDdl] = useState(false);
  /** Memory-only BYOC JSON for non-DB sinks (WIS2/EDIS/AMHS/SWIM/AFS). */
  const [byocParamsJson, setByocParamsJson] = useState('{}');
  /** Drag-drop overrides; props win when null. */
  const [droppedIwxxm, setDroppedIwxxm] = useState<string | null>(null);
  const [droppedTac, setDroppedTac] = useState<string | null>(null);
  const [preflight, setPreflight] = useState<PreflightResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [sendResult, setSendResult] = useState<string | null>(null);

  const iwxxmXml = droppedIwxxm ?? propIwxxm ?? '';
  const tacText = droppedTac ?? propTac ?? '';

  const needsUri = DB_SINK_TYPES.includes(sinkType);
  const canSend = isPreflightGreen(preflight);
  const hasPayload = Boolean(iwxxmXml.trim() || tacText.trim());

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

  const diffSummary = useMemo(() => {
    if (!preflight) return null;
    if (preflight.diffs.length === 0 && preflight.ok) {
      return 'Preflight green — no schema diffs.';
    }
    return null;
  }, [preflight]);

  const runPreflight = useCallback(async () => {
    if (!accessToken) {
      setError('Authentication required. Please log in again.');
      return;
    }
    const params = parseByocParams();
    if (params === null) return;
    setBusy(true);
    setError(null);
    setSendResult(null);
    setPreflight(null);
    try {
      const result = await disseminationPreflight(accessToken, {
        sink_type: sinkType,
        uri: needsUri ? uri : undefined,
        ddl: needsUri ? ddl : false,
        product,
        params,
      });
      setPreflight(result);
      if (!isPreflightGreen(result) && result.detail) {
        setError(result.detail);
      }
    } catch (err) {
      setPreflight(null);
      setError(err instanceof Error ? err.message : 'Preflight failed');
    } finally {
      setBusy(false);
    }
  }, [accessToken, ddl, needsUri, parseByocParams, product, sinkType, uri]);

  const runSend = useCallback(async () => {
    if (!accessToken || !canSend || !preflight?.handle) return;
    if (!hasPayload) {
      setError('Provide IWXXM or TAC payload (convert or drag-drop) before Send.');
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const result = await disseminationSend(accessToken, {
        handle: preflight.handle,
        iwxxm_xml: iwxxmXml.trim() || undefined,
        tac_text: tacText.trim() || undefined,
        product,
      });
      setSendResult(result.kv_upload_key ?? result.detail ?? 'sent');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Send failed');
    } finally {
      setBusy(false);
    }
  }, [accessToken, canSend, hasPayload, iwxxmXml, preflight, product, tacText]);

  const onDropFiles = useCallback((files: FileList | null) => {
    if (!files?.length) return;
    const file = files[0];
    const reader = new FileReader();
    reader.onload = () => {
      const text = String(reader.result ?? '');
      const name = file.name.toLowerCase();
      if (name.endsWith('.xml') || text.trimStart().startsWith('<')) {
        setDroppedIwxxm(text);
        setDroppedTac(null);
      } else {
        setDroppedTac(text);
        setDroppedIwxxm(null);
      }
      // Dropping a new payload invalidates prior preflight handle.
      setPreflight(null);
      setSendResult(null);
    };
    reader.readAsText(file);
  }, []);

  const closeDrawer = useCallback(() => {
    setDroppedIwxxm(null);
    setDroppedTac(null);
    setPreflight(null);
    setSendResult(null);
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
              setPreflight(null);
              setSendResult(null);
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
                setPreflight(null);
                setSendResult(null);
              }}
            />
            <label className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
              <input
                type="checkbox"
                data-testid="dissemination-ddl-toggle"
                checked={ddl}
                onChange={(e) => {
                  setDdl(e.target.checked);
                  setPreflight(null);
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
                setPreflight(null);
                setSendResult(null);
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
          {(iwxxmXml || tacText) && (
            <p
              className="mt-2 text-xs text-gray-600 dark:text-gray-400"
              data-testid="dissemination-payload-status"
            >
              Payload ready ({iwxxmXml ? 'IWXXM' : 'TAC'},{' '}
              {(iwxxmXml || tacText).length} chars)
            </p>
          )}
        </div>

        <div className="flex gap-2">
          <Button
            type="button"
            data-testid="dissemination-preflight-button"
            disabled={busy || (needsUri && !uri.trim())}
            onClick={() => void runPreflight()}
          >
            Preflight
          </Button>
          <Button
            type="button"
            data-testid="dissemination-send-button"
            disabled={busy || !canSend || !hasPayload}
            onClick={() => void runSend()}
          >
            Send
          </Button>
        </div>

        {diffSummary && (
          <p
            className="text-sm text-green-700 dark:text-green-400"
            data-testid="dissemination-preflight-green"
          >
            {diffSummary}
          </p>
        )}

        {preflight && preflight.diffs.length > 0 && (
          <ul
            className="space-y-1 rounded border border-amber-300 bg-amber-50 p-3 text-sm dark:border-amber-700 dark:bg-amber-950"
            data-testid="dissemination-preflight-diffs"
          >
            {preflight.diffs.map((diff, idx) => (
              <li
                key={`${diff.table}-${diff.kind}-${idx}`}
                data-testid="dissemination-diff-item"
              >
                <span className="font-medium">{diff.kind}</span>
                {': '}
                {diff.table}
                {diff.column ? `.${diff.column}` : ''} — {diff.detail}
              </li>
            ))}
          </ul>
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

        {sendResult && (
          <p
            className="text-sm text-green-700 dark:text-green-400"
            data-testid="dissemination-send-success"
          >
            Sent — key {sendResult}
          </p>
        )}
      </aside>
    </div>
  );
}

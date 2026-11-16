/* eslint-disable react-refresh/only-export-components */
/**
 * Dissemination drawer (F16–F19) — multi-select export + per-file progress.
 */
import { useCallback, useEffect, useMemo, useState } from 'react';
import { type ProgressRowStatus } from './DisseminationProgressRow';
import {
  DB_SINK_TYPES,
  disseminationPreflight,
  disseminationSend,
  type SinkType,
} from '@/utils/dissemination';
import {
  buildExportCandidates,
  canActOnSelection,
  initialSelectedIds,
  type ExportCandidate,
  type ExportCandidateInput,
} from '@/utils/exportSelection';
import {
  runDisseminationQueue,
  type DisseminationFileResult,
} from '@/utils/disseminationQueue';
import { firstDropFile, resolveDisseminationProduct } from '@/utils/fileInputHelpers';
import {
  listTemplates,
  type DisseminationTemplateOut,
} from '@/utils/conversionProfilesApi';
import {
  coerceExchangeProfile,
  DEFAULT_EXCHANGE_PROFILE,
  type ExchangeProfileId,
} from '@/utils/exchangeProfile';
import {
  hasDropFiles,
  dropReaderText,
  resolveCandidateIwxxmXml,
} from '@/utils/disseminationDrawerHelpers';
import { DisseminationDrawerView } from './DisseminationDrawerView';

export { firstDropFile, resolveDisseminationProduct } from '@/utils/fileInputHelpers';
export {
  hasDropFiles,
  dropReaderText,
  progressRowState,
  resolveCandidateIwxxmXml,
} from '@/utils/disseminationDrawerHelpers';

export type { DisseminationDrawerProps } from '@/models/disseminationDrawer';
import type { DisseminationDrawerProps } from '@/models/disseminationDrawer';

interface RowUiState {
  status: ProgressRowStatus;
  detail?: string;
}

/**
 * DisseminationDrawer.
 * @example
 * const _ = true;
 */
export function DisseminationDrawer({
  open,
  onOpenChange,
  iwxxmXml: propIwxxm,
  tacText: propTac,
  product = 'metar',
  sessionOutputs = [],
  accessToken,
  disseminationTemplateId = '',
  onDisseminationTemplateChange,
  exchangeProfile: exchangeProfileProp,
  onExchangeProfileChange,
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
  const [templates, setTemplates] = useState<DisseminationTemplateOut[]>([]);
  const [templateLoadError, setTemplateLoadError] = useState<string | null>(null);
  const [localSelectedTemplateId, setLocalSelectedTemplateId] = useState('');
  const templatesEnabled = Boolean(accessToken?.trim());
  const selectedTemplateId = onDisseminationTemplateChange
    ? disseminationTemplateId
    : localSelectedTemplateId;
  const [exchangeProfile, setExchangeProfile] = useState<ExchangeProfileId>(() =>
    coerceExchangeProfile(exchangeProfileProp ?? DEFAULT_EXCHANGE_PROFILE),
  );

  useEffect(() => {
    onExchangeProfileChange?.(exchangeProfile);
    // Notify parent once with the initial packaging Exchange (catalog filter).
    // eslint-disable-next-line react-hooks/exhaustive-deps -- mount-only notify
  }, []);

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

  useEffect(() => {
    if (!open || !templatesEnabled) {
      return;
    }
    const token = accessToken!.trim();
    let cancelled = false;
    void listTemplates(token)
      .then((response) => {
        if (cancelled) return;
        setTemplates(response.items);
        setTemplateLoadError(null);
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        setTemplates([]);
        setTemplateLoadError(
          err instanceof Error ? err.message : 'Unable to load templates',
        );
      });
    return () => {
      cancelled = true;
    };
  }, [accessToken, open, templatesEnabled]);

  const applyTemplate = useCallback(
    (templateId: string) => {
      if (onDisseminationTemplateChange) {
        onDisseminationTemplateChange(templateId);
      } else {
        setLocalSelectedTemplateId(templateId);
      }
      const template = templates.find((item) => item.id === templateId);
      if (!template) {
        return;
      }
      setSinkType(template.sinkType as SinkType);
      setDdl(template.ddl);
      setByocParamsJson(JSON.stringify(template.params ?? {}, null, 2));
      setLastResults([]);
      setRowState({});
    },
    [onDisseminationTemplateChange, templates],
  );

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
            disseminationPreflight(
              {
                dissemination_template_id: selectedTemplateId || undefined,
                sink_type: sink.sinkType,
                uri: sink.uri,
                ddl: sink.ddl,
                product: sink.product,
                params: sink.params,
              },
              accessToken,
            ),
          send: async (candidate, handle) => {
            const iwxxmXml = await resolveCandidateIwxxmXml(
              candidate,
              product,
              exchangeProfile,
            );
            return disseminationSend(
              {
                dissemination_template_id: selectedTemplateId || undefined,
                handle,
                iwxxm_xml: iwxxmXml,
                tac_text: candidate.tacText?.trim() || undefined,
                product: resolveDisseminationProduct(candidate.product, product),
              },
              accessToken,
            );
          },
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
    [
      accessToken,
      ddl,
      exchangeProfile,
      needsUri,
      parseByocParams,
      product,
      selectedCandidates,
      selectedTemplateId,
      sinkType,
      uri,
    ],
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
    setTemplates([]);
    setTemplateLoadError(null);
    if (onDisseminationTemplateChange) {
      onDisseminationTemplateChange('');
    } else {
      setLocalSelectedTemplateId('');
    }
    onOpenChange(false);
  }, [onDisseminationTemplateChange, onOpenChange]);

  if (!open) return null;

  return (
    <DisseminationDrawerView
      exchangeProfile={exchangeProfile}
      onExchangeProfileChange={onExchangeProfileChange}
      sinkType={sinkType}
      setSinkType={setSinkType}
      uri={uri}
      setUri={setUri}
      ddl={ddl}
      setDdl={setDdl}
      byocParamsJson={byocParamsJson}
      setByocParamsJson={setByocParamsJson}
      selectionError={selectionError}
      setForceExpanded={setForceExpanded}
      setExpandKey={setExpandKey}
      error={error}
      rowState={rowState}
      setRowState={setRowState}
      lastResults={lastResults}
      setLastResults={setLastResults}
      templates={templates}
      templateLoadError={templateLoadError}
      templatesEnabled={templatesEnabled}
      selectedTemplateId={selectedTemplateId}
      setExchangeProfile={setExchangeProfile}
      candidates={candidates}
      selectedIds={selectedIds}
      setSelectedIds={setSelectedIds}
      needsUri={needsUri}
      canAct={canAct}
      showSelectionPanel={showSelectionPanel}
      candidateKey={candidateKey}
      selectedCandidates={selectedCandidates}
      applyTemplate={applyTemplate}
      runQueue={runQueue}
      onDropFiles={onDropFiles}
      closeDrawer={closeDrawer}
      busy={busy}
    />
  );
}

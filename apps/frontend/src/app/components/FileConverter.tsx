import { useState, useRef, useEffect, useLayoutEffect, useCallback } from 'react';
import { Button } from './ui/button';
import { Card } from './ui/card';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { TacEditor } from './TacEditor';
import { DecodePanel } from './DecodePanel';
import { FailedTacCue } from './FailedTacCue';
import {
  IwxxmPreviewPane,
  type IwxxmPreviewMode,
  type IwxxmPreviewStatus,
} from './IwxxmPreviewPane';
import { SoftPreviewControl } from './SoftPreviewControl';
import { LiveIwxxmToggle } from './LiveIwxxmToggle';
import { WorkbenchConsole } from './WorkbenchConsole';
import { useLintIssueCatalog } from '@/hooks/useLintIssueCatalog';
import {
  Upload,
  X,
  Download,
  Copy,
  FileText,
  Loader2,
  Database,
  Settings,
  ChevronDown,
  ChevronUp,
  AlertCircle,
  XCircle,
} from 'lucide-react';
import JSZip from 'jszip';
import { toast } from 'sonner';
import { ThemeToggle } from './ThemeToggle';
import { GoldenExamplesSelect } from './GoldenExamplesSelect';
import { DatabaseUploadDialog } from './DatabaseUploadDialog';
import { DisseminationDrawer } from './DisseminationDrawer';
import { UserPreferencesDialog } from './UserPreferencesDialog';
import { PrivacyNotice } from './PrivacyNotice';
import { PrivacySettingsDialog } from './PrivacySettingsDialog';
import {
  acknowledgePrivacyNotice,
  shouldShowPrivacyNotice,
} from '@/utils/privacyPreferences';
import { getExampleById } from '@/fixtures/examples/examplesCatalog';
import { IcaoAutocomplete } from './IcaoAutocomplete';
import { AirportDetailsCard } from './AirportDetailsCard';
import {
  convertMetarToIwxxm as callBackendConversion,
  convertBulletin,
  ingestCollect,
  EndpointNotImplementedError,
  type FailedSpan,
} from '/utils/api';
import { useLiveWorkbenchAssist } from '@/hooks/useLiveWorkbenchAssist';
import { isAbortError } from '/utils/liveAssist';
import {
  detectTacProduct,
  resolveConvertProduct,
  type IwxxmProfile,
  type TacProductSelection,
} from '/utils/tacProduct';
import {
  CONVERT_AND_SEND_UPLOAD_OPTIONS,
  uploadConvertedFiles,
} from '/utils/databaseUpload';
import { ErrorLogPanel, type ConversionLog } from './ErrorLogPanel';
import { WorkHistorySidebar } from './WorkHistorySidebar';
import type { WorkSession } from '@metar/shared';
import { useWorkSessionSync } from '@/hooks/useWorkSessionSync';

import {
  type ConverterSnapshot,
  resolveManualLineMetaFromResult,
} from '/utils/workSessionPayload';
import { readGuestConverterState } from '/utils/guestConverterState';
import {
  manualOutputName,
  outputArchiveName,
  sanitizeOutputFilename,
} from '/utils/outputFilename';
import {
  deriveTacDisplayTitle,
  resolveOriginalTac,
  truncateTacSnippet,
} from '/utils/resultTraceability';
import {
  mapOnErrorToStopOnError,
  mapStrictToValidation,
  type ConvertLogLevel,
  type ConvertOnError,
} from '/utils/convertParams';
import {
  detectInputKind,
  kindToMode,
  looksLikeAhlBulletin,
  looksLikeCollectIwxxm,
  type OperatorInputMode,
} from '/utils/inputKind';
import { inflateGzipToText, isGzipFileName } from '/utils/gunzip';

interface ConvertedFile {
  id: string;
  originalName: string;
  originalContent: string;
  convertedContent: string;
  timestamp: number;
  /** TAC-derived card title (e.g. METAR KJFK 121251Z). */
  displayTitle: string;
  /** 1-based index when manual input had multiple lines. */
  manualLineIndex?: number;
  manualLineTotal?: number;
}

interface PendingFile {
  id: string;
  name: string;
  content: string;
}

interface FileConverterProps {
  /** @deprecated F21 public — ignored */
  accessToken?: string;
  onOpenHistory?: () => void;
  onLoadWorkSession?: (session: WorkSession) => void;
  onNewMetar?: () => void;
  onSessionUpdated?: (session: WorkSession) => void;
  onActiveSessionIdChange?: (id: string | null) => void;
  activeWorkSessionId?: string | null;
  loadedWorkSession?: WorkSession | null;
}

type IWXXMVersion = '2025-2' | '2023-1';
type OnErrorBehavior = 'skip' | 'fail' | 'warn';
type LogLevel = 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL';

interface ConversionParams {
  bulletinId: string;
  issuingCenter: string;
  product: TacProductSelection;
  profile: IwxxmProfile;
  iwxxmVersion: IWXXMVersion;
  strictValidation: boolean;
  includeNilReasons: boolean;
  onError: OnErrorBehavior;
  logLevel: LogLevel;
}

export function FileConverter({
  onOpenHistory,
  onLoadWorkSession,
  onNewMetar,
  onSessionUpdated,
  onActiveSessionIdChange,
  activeWorkSessionId,
  loadedWorkSession,
}: FileConverterProps) {
  const [pendingFiles, setPendingFiles] = useState<PendingFile[]>([]);
  const [convertedFiles, setConvertedFiles] = useState<ConvertedFile[]>([]);
  const [manualInput, setManualInput] = useState('');
  const [decodeError, setDecodeError] = useState<string | null>(null);
  const [softPreview, setSoftPreview] = useState(false);
  const [liveIwxxm, setLiveIwxxm] = useState(false);
  const [failedSpans, setFailedSpans] = useState<FailedSpan[]>([]);
  const [previewXml, setPreviewXml] = useState('');
  const [previewStatus, setPreviewStatus] = useState<IwxxmPreviewStatus>('empty');
  const [previewMode, setPreviewMode] = useState<IwxxmPreviewMode>('idle');
  const [previewSoftFailDetail, setPreviewSoftFailDetail] = useState<
    string | undefined
  >();
  const [inputMode, setInputMode] = useState<OperatorInputMode>('tac');
  const [demoExampleLabel, setDemoExampleLabel] = useState<string | null>(null);
  const [bulletinSummary, setBulletinSummary] = useState<string | null>(null);
  const [placeholderNotice, setPlaceholderNotice] = useState<string | null>(null);
  // Restore the guest's custom output filename from the session snapshot (R5).
  const [outputFilename, setOutputFilename] = useState(() => {
    const saved = readGuestConverterState()?.conversionParams?.output_filename;
    return typeof saved === 'string' ? saved : '';
  });
  const [isDragging, setIsDragging] = useState(false);
  const [isConverting, setIsConverting] = useState(false);
  const [isConvertAndSending, setIsConvertAndSending] = useState(false);
  const [conversionStatus, setConversionStatus] = useState<{
    type: 'idle' | 'loading' | 'timeout' | 'error' | 'send_error';
    message?: string;
  }>({ type: 'idle' });
  const [conversionLog, setConversionLog] = useState<ConversionLog | null>(null);
  const [isUploadDialogOpen, setIsUploadDialogOpen] = useState(false);
  const [isDisseminationOpen, setIsDisseminationOpen] = useState(false);
  const [isPreferencesDialogOpen, setIsPreferencesDialogOpen] = useState(false);
  const [isPrivacySettingsOpen, setIsPrivacySettingsOpen] = useState(false);
  const [showPrivacyNotice, setShowPrivacyNotice] = useState(() =>
    shouldShowPrivacyNotice(),
  );
  const [isParamsExpanded, setIsParamsExpanded] = useState(false);
  const [conversionParams, setConversionParams] = useState<ConversionParams>({
    bulletinId: '',
    issuingCenter: '',
    product: 'auto',
    profile: 'annex3',
    iwxxmVersion: '2025-2',
    strictValidation: true,
    includeNilReasons: true,
    onError: 'warn',
    logLevel: 'INFO',
  });
  const fileInputRef = useRef<HTMLInputElement>(null);
  const hydratedWorkSessionIdRef = useRef<string | null>(null);

  const buildSnapshot = (
    overrides?: Partial<ConverterSnapshot>,
  ): ConverterSnapshot => ({
    manualInput,
    pendingFiles: pendingFiles.map((file) => ({
      name: file.name,
      content: file.content,
    })),
    convertedFiles: convertedFiles.map((file) => ({
      originalName: file.originalName,
      originalContent: file.originalContent,
      convertedContent: file.convertedContent,
      manualLineIndex: file.manualLineIndex,
      manualLineTotal: file.manualLineTotal,
    })),
    conversionLog: conversionLog
      ? {
          errors: conversionLog.errors,
          issues: conversionLog.issues as unknown as Record<string, unknown>[],
        }
      : null,
    conversionParams: {
      ...(conversionParams as unknown as Record<string, unknown>),
      output_filename: outputFilename,
    },
    ...overrides,
  });

  const { isReadOnly, saveIndicator, scheduleAutoSave, persistSession } =
    useWorkSessionSync({
      sessionId: activeWorkSessionId ?? null,
      sessionStatus: loadedWorkSession?.status ?? null,
      onSessionSaved: (session) => onSessionUpdated?.(session),
      onSessionIdAssigned: (id) => onActiveSessionIdChange?.(id),
    });

  // Load user preferences on mount from localStorage
  useEffect(() => {
    const loadPreferences = () => {
      try {
        const stored = localStorage.getItem('metar_converter_preferences');
        if (stored) {
          const prefs = JSON.parse(stored);
          // Migrate old version identifiers to new ones
          let iwxxmVersion: IWXXMVersion = '2025-2';
          if (prefs.iwxxmVersion === '2023-1') {
            iwxxmVersion = '2023-1';
          } else {
            // Default any other version (3.0, 2.1, 2021-2) to 2025-2
            iwxxmVersion = '2025-2';
          }

          setConversionParams({
            bulletinId: prefs.bulletinIdExample || 'SAAA00',
            issuingCenter: prefs.issuingCenter || 'KWBC',
            product: (prefs.product as TacProductSelection) || 'auto',
            profile: prefs.profile === 'iwxxm_us' ? 'iwxxm_us' : 'annex3',
            iwxxmVersion,
            strictValidation: prefs.strictValidation ?? true,
            includeNilReasons: prefs.includeNilReasons ?? true,
            onError: prefs.onError || 'warn',
            logLevel: prefs.logLevel || 'INFO',
          });
        }
      } catch (error) {
        console.error('Error loading preferences:', error);
      }
    };

    loadPreferences();
  }, []);

  /* eslint-disable react-hooks/set-state-in-effect -- F5 hydrate converter when user loads a work session */
  useLayoutEffect(() => {
    if (!loadedWorkSession) {
      hydratedWorkSessionIdRef.current = null;
      return;
    }
    // Re-hydrate only when the user selects a different session — not on every
    // autosave/onSessionUpdated refresh (which would undo Remove / Clear).
    if (hydratedWorkSessionIdRef.current === loadedWorkSession.id) {
      return;
    }
    hydratedWorkSessionIdRef.current = loadedWorkSession.id;
    setManualInput(loadedWorkSession.manual_tac || '');
    setPendingFiles(
      (loadedWorkSession.pending_files || []).map((file, index) => ({
        id: `loaded-${index}`,
        name: file.name,
        content: file.content,
      })),
    );
    if (loadedWorkSession.converted_results?.length) {
      const resultNames = loadedWorkSession.converted_results.map((result, index) =>
        String(result.name ?? `result-${index + 1}`),
      );
      setConvertedFiles(
        loadedWorkSession.converted_results.map((result, index) => {
          const originalName = resultNames[index];
          const originalContent = String(result.tac_input ?? '');
          const lineMeta = resolveManualLineMetaFromResult(
            originalName,
            result,
            resultNames,
          );
          return {
            id: `loaded-result-${index}`,
            originalName,
            originalContent,
            displayTitle: deriveTacDisplayTitle(originalContent, originalName),
            manualLineIndex: lineMeta.manualLineIndex,
            manualLineTotal: lineMeta.manualLineTotal,
            convertedContent: String(
              result.iwxxm_xml ?? result.xml ?? result.content ?? '',
            ),
            timestamp: Date.now(),
          };
        }),
      );
    } else {
      setConvertedFiles([]);
    }
    const hasLog =
      (loadedWorkSession.errors?.length ?? 0) > 0 ||
      (loadedWorkSession.issues?.length ?? 0) > 0;
    setConversionLog(
      hasLog
        ? {
            errors: loadedWorkSession.errors ?? [],
            issues: (loadedWorkSession.issues ??
              []) as unknown as ConversionLog['issues'],
          }
        : null,
    );
    const params = loadedWorkSession.conversion_params as
      | Record<string, unknown>
      | undefined;
    const savedName = params?.output_filename;
    setOutputFilename(typeof savedName === 'string' ? savedName : '');
    if (params) {
      setConversionParams((prev) => {
        const next = { ...prev };
        const rawProduct = params.product;
        if (
          typeof rawProduct === 'string' &&
          (rawProduct === 'auto' ||
            ['AIRMET', 'METAR', 'SIGMET', 'SPECI', 'TAF', 'VAA', 'TCA'].includes(
              rawProduct,
            ))
        ) {
          next.product = rawProduct as TacProductSelection;
        }
        if (params.profile === 'iwxxm_us' || params.profile === 'annex3') {
          next.profile = params.profile;
        }
        return next;
      });
    }
  }, [loadedWorkSession]);
  /* eslint-enable react-hooks/set-state-in-effect */

  useEffect(() => {
    if (isReadOnly) {
      return;
    }
    scheduleAutoSave(buildSnapshot());
    // eslint-disable-next-line react-hooks/exhaustive-deps -- debounced save on converter edits
  }, [
    manualInput,
    pendingFiles,
    convertedFiles,
    conversionLog,
    outputFilename,
    isReadOnly,
  ]);

  const handlePreferencesSaved = () => {
    // Reload preferences after saving in the dialog
    try {
      const stored = localStorage.getItem('metar_converter_preferences');
      if (stored) {
        const prefs = JSON.parse(stored);
        // Migrate old version identifiers to new ones
        let iwxxmVersion: IWXXMVersion = '2025-2';
        if (prefs.iwxxmVersion === '2023-1') {
          iwxxmVersion = '2023-1';
        } else {
          // Default any other version (3.0, 2.1, 2021-2) to 2025-2
          iwxxmVersion = '2025-2';
        }

        setConversionParams({
          bulletinId: prefs.bulletinIdExample || 'SAAA00',
          issuingCenter: prefs.issuingCenter || 'KWBC',
          product: (prefs.product as TacProductSelection) || 'auto',
          profile: prefs.profile === 'iwxxm_us' ? 'iwxxm_us' : 'annex3',
          iwxxmVersion,
          strictValidation: prefs.strictValidation ?? true,
          includeNilReasons: prefs.includeNilReasons ?? true,
          onError: prefs.onError || 'warn',
          logLevel: prefs.logLevel || 'INFO',
        });
        toast.info('Conversion parameters updated from preferences');
      }
    } catch (error) {
      console.error('Error reloading preferences:', error);
    }
  };

  const handleFileSelect = async (files: FileList | null) => {
    if (!files || files.length === 0) return;

    const newPendingFiles: PendingFile[] = [];
    let detectedMode: OperatorInputMode | null = null;

    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      try {
        let content: string;
        let displayName = file.name;
        if (isGzipFileName(file.name)) {
          content = await inflateGzipToText(file);
          displayName = file.name.replace(/\.gz$/i, '').replace(/\.gzip$/i, '');
          toast.info(`Decompressed ${file.name}`);
        } else {
          content = await file.text();
        }
        // Classify by decompressed display name + content (not raw .gz → kind "gzip")
        const kind = detectInputKind(displayName, content);
        detectedMode = kindToMode(kind);
        newPendingFiles.push({
          id: `${displayName}-${Date.now()}-${i}`,
          name: displayName,
          content,
        });
      } catch (error) {
        console.error(`Error reading file ${file.name}:`, error);
        toast.error(
          error instanceof Error ? error.message : `Failed to read ${file.name}`,
        );
      }
    }

    if (detectedMode && detectedMode !== inputMode) {
      setInputMode(detectedMode);
      toast.info(
        detectedMode === 'ahl_bulletin'
          ? 'Detected AHL bulletin — switched input mode'
          : detectedMode === 'collect_iwxxm'
            ? 'Detected IWXXM COLLECT — switched input mode'
            : 'Switched to TAC report mode',
      );
    }

    setPendingFiles((prev) => [...prev, ...newPendingFiles]);
    if (newPendingFiles.length > 0) {
      toast.success(`${newPendingFiles.length} file(s) added to queue`);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    handleFileSelect(e.dataTransfer.files);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const performConversion = async (): Promise<{
    files: ConvertedFile[];
    hasErrors: boolean;
    softFail: boolean;
  } | null> => {
    if (pendingFiles.length === 0 && !manualInput.trim()) {
      toast.error('Please add files or enter manual input');
      return null;
    }

    setConversionStatus({ type: 'loading', message: 'Converting...' });
    setConversionLog(null);
    setFailedSpans([]);
    setBulletinSummary(null);
    setPlaceholderNotice(null);

    try {
      const tacForDetect = [manualInput.trim(), ...pendingFiles.map((f) => f.content)]
        .filter(Boolean)
        .join('\n');

      // Auto-switch when paste looks like bulletin / COLLECT (UJ-025 / ADR-024)
      let mode = inputMode;
      if (mode === 'tac' && looksLikeAhlBulletin(tacForDetect)) {
        mode = 'ahl_bulletin';
        setInputMode('ahl_bulletin');
        toast.info('Detected AHL bulletin — switched input mode');
      } else if (mode === 'tac' && looksLikeCollectIwxxm(tacForDetect)) {
        mode = 'collect_iwxxm';
        setInputMode('collect_iwxxm');
        toast.info('Detected IWXXM COLLECT — switched input mode');
      }

      const resolvedProduct = resolveConvertProduct(
        conversionParams.product,
        tacForDetect,
      );
      if (conversionParams.product !== 'auto' && tacForDetect.trim()) {
        const detected = detectTacProduct(tacForDetect);
        if (detected !== resolvedProduct) {
          toast.warning(
            `Selected product ${resolvedProduct} differs from detected ${detected}; converting as ${resolvedProduct}.`,
          );
        }
      }

      const filesToConvert: File[] = pendingFiles.map((file) => {
        return new File([file.content], file.name, { type: 'text/plain' });
      });

      if (mode === 'collect_iwxxm') {
        try {
          await ingestCollect({
            manualText: manualInput.trim() || undefined,
            files: filesToConvert.length > 0 ? filesToConvert : undefined,
            profile: conversionParams.profile,
            iwxxmVersion: conversionParams.iwxxmVersion,
          });
          toast.success('COLLECT ingest succeeded');
          setConversionStatus({ type: 'idle' });
          return { files: [], hasErrors: false, softFail: false };
        } catch (err) {
          if (err instanceof EndpointNotImplementedError) {
            setPlaceholderNotice(err.message);
            setConversionLog({
              errors: [],
              issues: [
                {
                  source: 'ingest-collect',
                  message: err.message,
                  severity: 'info',
                  code: err.code,
                  hint: 'Use AHL bulletin mode for TAC bulletins, or paste single reports in TAC mode.',
                },
              ],
            });
            toast.warning('COLLECT ingest placeholder (not implemented yet)');
            setConversionStatus({ type: 'idle' });
            return { files: [], hasErrors: true, softFail: false };
          }
          throw err;
        }
      }

      if (mode === 'ahl_bulletin') {
        const bulletinResponse = await convertBulletin({
          manualText: manualInput.trim() || undefined,
          files: filesToConvert.length > 0 ? filesToConvert : undefined,
          product: resolvedProduct,
          profile: conversionParams.profile,
          iwxxmVersion: conversionParams.iwxxmVersion,
          lint: true,
        });
        const meta = bulletinResponse.bulletin_meta;
        setBulletinSummary(
          `${meta.ahl} · ${meta.report_count} report(s) · ${meta.cccc} ${meta.yygggg}`,
        );
        const newConvertedFiles: ConvertedFile[] = [];
        const issueBag: ConversionLog['issues'] = [];
        bulletinResponse.results.forEach((result) => {
          result.issues.forEach((issue) => {
            issueBag.push({
              source: `bulletin[${result.report_index}]`,
              message: issue.message,
              code: issue.code,
              severity:
                (issue.severity as ConversionLog['issues'][0]['severity']) || 'warning',
              start: issue.start ?? undefined,
              end: issue.end ?? undefined,
            });
          });
          if (result.ok && result.xml) {
            const originalContent = result.tac_input;
            newConvertedFiles.push({
              id: `bulletin-${Date.now()}-${result.report_index}`,
              originalName: `bulletin_report_${result.report_index + 1}.tac`,
              originalContent,
              displayTitle: deriveTacDisplayTitle(
                originalContent,
                `report ${result.report_index + 1}`,
              ),
              convertedContent: result.xml,
              timestamp: Date.now(),
            });
          }
        });
        const failed = bulletinResponse.results.filter((r) => !r.ok).length;
        setConvertedFiles(newConvertedFiles);
        setPendingFiles([]);
        if (!softPreview) {
          setManualInput('');
        }
        setConversionLog(issueBag.length > 0 ? { errors: [], issues: issueBag } : null);
        setConversionStatus({ type: 'idle' });
        if (failed > 0) {
          toast.warning(`Bulletin: ${newConvertedFiles.length} ok, ${failed} failed`);
        } else {
          toast.success(`Bulletin: ${newConvertedFiles.length} report(s) converted`);
        }
        return {
          files: newConvertedFiles,
          hasErrors: failed > 0,
          softFail: false,
        };
      }

      const newConvertedFiles: ConvertedFile[] = [];

      console.log('[FileConverter] Starting conversion with:', {
        manualInput: manualInput.trim() ? 'provided' : 'none',
        fileCount: filesToConvert.length,
        softPreview,
      });

      const { validateOutput, validationLevel } = mapStrictToValidation(
        conversionParams.strictValidation,
        softPreview,
      );

      const response = await callBackendConversion({
        manualText: manualInput.trim() || undefined,
        files: filesToConvert.length > 0 ? filesToConvert : undefined,
        product: resolvedProduct,
        profile: conversionParams.profile,
        iwxxmVersion: conversionParams.iwxxmVersion,
        validateOutput,
        validationLevel,
        stopOnError: mapOnErrorToStopOnError(
          conversionParams.onError as ConvertOnError,
        ),
        bulletinId: conversionParams.bulletinId || undefined,
        issuingCenter: conversionParams.issuingCenter || undefined,
        includeNilReasons: conversionParams.includeNilReasons,
        logLevel: conversionParams.logLevel,
        preview: softPreview,
      });

      console.log('[FileConverter] Conversion response:', response);

      if (response.results && Array.isArray(response.results)) {
        // Match backend split_manual_entries: manual results precede file results.
        const manualLines = manualInput
          .split(/\r?\n/)
          .map((line) => line.trim())
          .filter(Boolean);
        const manualResultCount = manualLines.length;

        response.results.forEach(
          (
            result: {
              iwxxm_xml?: string;
              xml?: string;
              content?: string;
              tac_input?: string;
              name?: string;
            },
            index: number,
          ) => {
            const isManualResult = index < manualResultCount;
            const fileIndex = index - manualResultCount;
            const pendingFile = pendingFiles[fileIndex];
            const originalName = isManualResult
              ? manualOutputName(outputFilename, index, manualResultCount)
              : (pendingFile?.name ?? result.name ?? 'unknown');
            const originalContent = resolveOriginalTac(
              result.tac_input,
              manualLines[index],
              pendingFile?.content,
            );

            newConvertedFiles.push({
              id: `converted-${Date.now()}-${index}`,
              originalName,
              originalContent,
              displayTitle: deriveTacDisplayTitle(originalContent, originalName),
              manualLineIndex:
                isManualResult && manualResultCount > 1 ? index + 1 : undefined,
              manualLineTotal:
                isManualResult && manualResultCount > 1 ? manualResultCount : undefined,
              convertedContent: result.iwxxm_xml || result.xml || result.content || '',
              timestamp: Date.now(),
            });
          },
        );
      }

      const responseErrors = response.errors ?? [];
      const responseIssues = response.issues ?? [];
      const hasLog = responseErrors.length > 0 || responseIssues.length > 0;
      const softFail = Boolean(softPreview && response.ok === false);
      const spans = response.failed_spans ?? [];

      if (softFail) {
        setFailedSpans(spans);
      }

      if (newConvertedFiles.length === 0) {
        if (hasLog) {
          setConversionLog({ errors: responseErrors, issues: responseIssues });
        }
        const failureMessage = responseErrors[0] ?? 'No files were converted';
        toast.error(failureMessage);
        setConversionStatus({ type: 'error', message: failureMessage });
        return null;
      }

      const latestPreviewXml =
        newConvertedFiles[newConvertedFiles.length - 1]?.convertedContent ?? '';
      if (latestPreviewXml && (softPreview || softFail)) {
        setPreviewXml(latestPreviewXml);
        setPreviewMode('soft-preview');
        if (softFail) {
          setPreviewStatus('soft-fail');
          setPreviewSoftFailDetail(
            'Some groups could not be converted. Fix the highlighted spans in the editor, then retry Soft-preview. This output is not for publish.',
          );
        } else {
          setPreviewStatus('passed');
          setPreviewSoftFailDetail(undefined);
        }
      }

      setConvertedFiles(newConvertedFiles);
      setPendingFiles([]);
      // Keep TAC in editor on soft-fail so Failed-TAC cue stays contextual (UJ-016).
      if (!softFail) {
        setManualInput('');
        setFailedSpans([]);
      }
      setConversionLog(
        hasLog ? { errors: responseErrors, issues: responseIssues } : null,
      );
      setConversionStatus({ type: 'idle' });
      return { files: newConvertedFiles, hasErrors: hasLog || softFail, softFail };
    } catch (error) {
      console.error('[FileConverter] Conversion error:', error);

      const errorMessage =
        error instanceof Error
          ? error.message
          : 'Conversion failed. Please check the input and try again.';
      const isTimeout =
        errorMessage.includes('timeout') || errorMessage.includes('unreachable');
      const isAuthError =
        errorMessage.includes('401') ||
        errorMessage.includes('unauthorized') ||
        errorMessage.includes('Unauthorized');

      if (isTimeout) {
        const timeoutMsg =
          'Conversion timeout - Backend may be unreachable. Please check if the API server is running.';
        setConversionStatus({ type: 'timeout', message: timeoutMsg });
        toast.error(timeoutMsg);
      } else if (isAuthError) {
        const authMsg = 'Authentication failed. Please ensure you are logged in.';
        setConversionStatus({ type: 'error', message: authMsg });
        toast.error(authMsg);
      } else {
        setConversionStatus({ type: 'error', message: errorMessage });
        toast.error(errorMessage);
      }
      return null;
    }
  };

  const handleConvert = async () => {
    if (isReadOnly) {
      return;
    }
    setIsConverting(true);
    try {
      const result = await performConversion();
      if (result) {
        if (result.softFail) {
          toast.warning(
            'Soft-preview returned Failed-TAC markers — not ready to publish',
          );
        } else {
          toast.success(`Successfully converted ${result.files.length} file(s)`);
        }
        const snapshot = buildSnapshot({
          convertedFiles: result.files.map((file) => ({
            originalName: file.originalName,
            originalContent: file.originalContent,
            convertedContent: file.convertedContent,
          })),
          manualInput: '',
          pendingFiles: [],
        });
        await persistSession(snapshot, {
          status: result.hasErrors ? 'failed' : 'wip',
        });
      } else {
        await persistSession(buildSnapshot(), { status: 'failed' });
      }
    } finally {
      setIsConverting(false);
    }
  };

  const handleConvertAndSend = async () => {
    if (isReadOnly) {
      return;
    }
    setIsConvertAndSending(true);
    try {
      const result = await performConversion();
      if (!result) {
        await persistSession(buildSnapshot(), { status: 'failed' });
        return;
      }

      if (result.hasErrors) {
        if (result.softFail) {
          toast.warning('Soft-preview Failed-TAC — fix markers before Convert & Send');
        }
        await persistSession(
          buildSnapshot({
            convertedFiles: result.files.map((file) => ({
              originalName: file.originalName,
              originalContent: file.originalContent,
              convertedContent: file.convertedContent,
            })),
            manualInput: result.softFail ? manualInput : '',
            pendingFiles: [],
          }),
          { status: 'failed' },
        );
        return;
      }

      toast.success(`Successfully converted ${result.files.length} file(s)`);
      setConversionStatus({ type: 'loading', message: 'Sending to database...' });

      const wipSnapshot = buildSnapshot({
        convertedFiles: result.files.map((file) => ({
          originalName: file.originalName,
          originalContent: file.originalContent,
          convertedContent: file.convertedContent,
        })),
        manualInput: '',
        pendingFiles: [],
      });

      try {
        const data = await uploadConvertedFiles({
          files: result.files,
          options: CONVERT_AND_SEND_UPLOAD_OPTIONS,
        });
        setConversionStatus({ type: 'idle' });
        toast.success(data.message || 'Files converted and sent successfully');
        await persistSession(wipSnapshot, { status: 'finished' });
      } catch (error) {
        console.error('[FileConverter] Convert&Send upload error:', error);
        const uploadMessage =
          error instanceof Error ? error.message : 'Failed to upload to database';
        setConversionStatus({
          type: 'send_error',
          message: `Send failed: ${uploadMessage}`,
        });
        toast.error(`Conversion succeeded but send failed: ${uploadMessage}`);
        await persistSession(wipSnapshot, { status: 'wip' });
      }
    } finally {
      setIsConvertAndSending(false);
    }
  };

  const handleNewMetar = () => {
    setPendingFiles([]);
    setManualInput('');
    setDemoExampleLabel(null);
    setOutputFilename('');
    setConvertedFiles([]);
    setConversionLog(null);
    setConversionStatus({ type: 'idle' });
    onActiveSessionIdChange?.(null);
    onNewMetar?.();
    toast.info(
      isReadOnly ? 'Starting a new METAR session' : 'Starting a new METAR draft',
    );
  };

  const handleLoadGoldenExample = useCallback((exampleId: string) => {
    const example = getExampleById(exampleId);
    if (!example) {
      return;
    }
    // Drop prior conversion/preview state so demo TAC is never paired with stale XML.
    setPendingFiles([]);
    setConvertedFiles([]);
    setConversionLog(null);
    setConversionStatus({ type: 'idle' });
    setFailedSpans([]);
    setPreviewXml('');
    setPreviewStatus('empty');
    setPreviewMode('idle');
    setPreviewSoftFailDetail(undefined);
    setBulletinSummary(null);
    setPlaceholderNotice(null);
    setDecodeError(null);

    setManualInput(example.body.replace(/\s+$/, ''));
    setInputMode(example.inputMode);
    // Always set product — omit → auto — so a prior TAF pick cannot stick on AHL/TAC demos.
    setConversionParams((prev) => ({
      ...prev,
      product: example.product ?? 'auto',
    }));
    setDemoExampleLabel(example.label);
    toast.info(`Loaded ${example.label} example`);
  }, []);

  const handleDownloadSingle = (file: ConvertedFile) => {
    const blob = new Blob([file.convertedContent], { type: 'text/xml' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = file.originalName.replace(/\.(txt|metar)$/i, '.xml');
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    toast.success('File downloaded');
  };

  const handleDownloadAll = async () => {
    if (convertedFiles.length === 0) return;

    const zip = new JSZip();

    convertedFiles.forEach((file) => {
      const filename = file.originalName.replace(/\.(txt|metar)$/i, '.xml');
      zip.file(filename, file.convertedContent);
    });

    const content = await zip.generateAsync({ type: 'blob' });
    const url = URL.createObjectURL(content);
    const a = document.createElement('a');
    a.href = url;
    a.download = outputArchiveName(outputFilename);
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    toast.success('All files downloaded as ZIP');
  };

  const handleCopy = (content: string) => {
    // Try modern clipboard API first
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard
        .writeText(content)
        .then(() => {
          toast.success('Copied to clipboard');
        })
        .catch(() => {
          // Fallback to older method
          fallbackCopy(content);
        });
    } else {
      // Fallback for browsers without clipboard API
      fallbackCopy(content);
    }
  };

  const fallbackCopy = (content: string) => {
    try {
      const textarea = document.createElement('textarea');
      textarea.value = content;
      textarea.style.position = 'fixed';
      textarea.style.left = '-9999px';
      textarea.style.top = '-9999px';
      document.body.appendChild(textarea);
      textarea.select();

      const successful = document.execCommand('copy');
      document.body.removeChild(textarea);

      if (successful) {
        toast.success('Copied to clipboard');
      } else {
        toast.error('Failed to copy. Please copy manually.');
      }
    } catch (err) {
      console.error('Copy failed:', err);
      toast.error('Failed to copy. Please copy manually.');
    }
  };

  const removePendingFile = (id: string) => {
    setPendingFiles((prev) => prev.filter((f) => f.id !== id));
  };

  const removeConvertedFile = (id: string) => {
    setConvertedFiles((prev) => prev.filter((f) => f.id !== id));
  };

  const handleClear = () => {
    setPendingFiles([]);
    setManualInput('');
    setDemoExampleLabel(null);
    setOutputFilename('');
    setConvertedFiles([]);
    setConversionLog(null);
    setConversionStatus({ type: 'idle' });
    setFailedSpans([]);
    setPreviewXml('');
    setPreviewStatus('empty');
    setPreviewMode('idle');
    setPreviewSoftFailDetail(undefined);
    setBulletinSummary(null);
    setPlaceholderNotice(null);
    setDecodeError(null);
    toast.info('Queue cleared');
  };

  const isBusy = isConverting || isConvertAndSending;
  const hasInput = pendingFiles.length > 0 || !!manualInput.trim();
  const hasConverted = convertedFiles.length > 0;
  const convertDisabled = isBusy || !hasInput || isReadOnly;

  const liveAssistProduct = resolveConvertProduct(
    conversionParams.product,
    manualInput,
  );

  const liveIwxxmRunner = useCallback(
    async (signal: AbortSignal) => {
      const text = manualInput.trim();
      if (!text) {
        return;
      }
      setDecodeError(null);
      try {
        const response = await callBackendConversion({
          manualText: text,
          product: liveAssistProduct,
          profile: conversionParams.profile,
          iwxxmVersion: conversionParams.iwxxmVersion,
          validateOutput: false,
          preview: true,
          signal,
        });
        if (signal.aborted) {
          return;
        }
        const latestXml =
          response.results?.[0]?.iwxxm_xml ||
          response.results?.[0]?.xml ||
          response.results?.[0]?.content ||
          '';
        if (latestXml) {
          setPreviewXml(latestXml);
          setPreviewMode('live');
        }
        if (response.failed_spans?.length) {
          setFailedSpans(response.failed_spans);
          setPreviewStatus('soft-fail');
          setPreviewSoftFailDetail(
            'Some groups could not be converted. Fix the highlighted spans in the editor, then retry. This Soft preview is not for publish.',
          );
        } else if (response.ok !== false) {
          setFailedSpans([]);
          setPreviewStatus(latestXml ? 'passed' : 'empty');
          setPreviewSoftFailDetail(undefined);
        }
      } catch (err) {
        if (isAbortError(err) || signal.aborted) {
          return;
        }
        setDecodeError(err instanceof Error ? err.message : 'Live IWXXM failed');
      }
    },
    [
      manualInput,
      liveAssistProduct,
      conversionParams.profile,
      conversionParams.iwxxmVersion,
    ],
  );

  const {
    issueSpans,
    lintFixes,
    decodeSegments,
    decodeResiduals,
    decodeProduct,
    decodeSummary,
    loading: decodeLoading,
    consoleLines,
    clearConsole,
    appendConsole,
  } = useLiveWorkbenchAssist({
    text: manualInput,
    product: liveAssistProduct,
    enabled: !isReadOnly,
    liveIwxxm,
    liveIwxxmRunner,
  });

  const { entries: lintCatalogEntries, byCode: lintCatalogByCode } =
    useLintIssueCatalog({
      product: liveAssistProduct,
      enabled: !isReadOnly,
    });

  const applyLintFix = useCallback(
    (fixCode: string) => {
      const fix = lintFixes.find((f) => f.code === fixCode);
      if (!fix?.replacement) {
        return;
      }
      setManualInput(fix.replacement);
    },
    [lintFixes],
  );

  const saveIndicatorLabel =
    saveIndicator === 'pending'
      ? 'Unsaved changes'
      : saveIndicator === 'saving'
        ? 'Saving draft…'
        : saveIndicator === 'saved'
          ? 'Draft saved'
          : saveIndicator === 'error'
            ? 'Save failed'
            : null;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8 px-4 transition-colors">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-3xl font-semibold text-gray-900 dark:text-white">
              METAR → IWXXM Converter
            </h1>
            <div className="flex items-center gap-3">
              <Button
                onClick={() => setIsPreferencesDialogOpen(true)}
                variant="outline"
                size="sm"
                className="dark:bg-gray-700 dark:text-white dark:hover:bg-gray-600 focus:ring-2 focus:ring-gray-500"
                aria-label="Open user preferences"
              >
                <Settings className="w-4 h-4 mr-2" aria-hidden="true" />
                Preferences
              </Button>
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-600 dark:text-gray-400">Theme</span>
                <ThemeToggle />
              </div>
            </div>
          </div>
          <p className="text-base text-gray-600 dark:text-gray-300">
            Enter TAC in the console below (choose product type as needed), then
            Convert. Upload files from the compact drop zone under the console when
            preferred.
          </p>
          <PrivacyNotice
            open={showPrivacyNotice}
            onDismiss={() => {
              acknowledgePrivacyNotice();
              setShowPrivacyNotice(false);
            }}
            onOpenSettings={() => {
              acknowledgePrivacyNotice();
              setShowPrivacyNotice(false);
              setIsPrivacySettingsOpen(true);
            }}
          />
        </div>

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-[minmax(0,1fr)_280px]">
          <div>
            {/* Manual Input — primary workbench */}
            <div className="mb-6">
              {isReadOnly && (
                <p
                  className="mb-2 rounded-md border border-amber-300 bg-amber-50 px-3 py-2 text-sm text-amber-900 dark:border-amber-700 dark:bg-amber-950/40 dark:text-amber-100"
                  role="status"
                >
                  This session is finished and read-only. Use <strong>New METAR</strong>{' '}
                  to start fresh.
                </p>
              )}
              <div className="mb-2 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
                <label
                  htmlFor="manual-input"
                  className="block text-base font-medium text-gray-900 dark:text-white"
                >
                  Manual TAC Input
                </label>
                <div className="flex flex-wrap items-center gap-2">
                  <div
                    className="flex rounded-md border border-gray-300 dark:border-gray-600"
                    role="group"
                    aria-label="Input mode"
                    data-testid="input-mode-group"
                  >
                    {(
                      [
                        ['tac', 'TAC report'],
                        ['ahl_bulletin', 'AHL bulletin'],
                        ['collect_iwxxm', 'IWXXM COLLECT'],
                      ] as const
                    ).map(([value, label]) => (
                      <button
                        key={value}
                        type="button"
                        data-testid={`input-mode-${value}`}
                        disabled={isReadOnly}
                        onClick={() => setInputMode(value)}
                        className={`px-2 py-1 text-xs ${
                          inputMode === value
                            ? 'bg-blue-600 text-white'
                            : 'bg-white text-gray-700 dark:bg-gray-800 dark:text-gray-200'
                        }`}
                      >
                        {label}
                      </button>
                    ))}
                  </div>
                  <Label
                    htmlFor="param-product"
                    className="shrink-0 text-sm text-gray-700 dark:text-gray-300"
                  >
                    Product type
                  </Label>
                  <select
                    id="param-product"
                    aria-label="Product"
                    data-testid="product-type-select"
                    value={conversionParams.product}
                    disabled={isReadOnly}
                    onChange={(e) =>
                      setConversionParams((prev) => ({
                        ...prev,
                        product: e.target.value as TacProductSelection,
                      }))
                    }
                    className="min-w-[9.5rem] rounded-md border border-gray-300 bg-white px-2 py-1.5 text-sm text-gray-900 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                  >
                    <option value="auto">Auto-detect</option>
                    <option value="AIRMET">AIRMET</option>
                    <option value="METAR">METAR</option>
                    <option value="SIGMET">SIGMET</option>
                    <option value="SPECI">SPECI</option>
                    <option value="TAF">TAF</option>
                    <option value="VAA">VAA</option>
                    <option value="TCA">TCA</option>
                  </select>
                  <GoldenExamplesSelect
                    disabled={isReadOnly}
                    onSelectExample={handleLoadGoldenExample}
                  />
                </div>
              </div>
              {demoExampleLabel && (
                <p
                  className="mb-2 rounded border border-amber-200 bg-amber-50 px-2 py-1 text-xs text-amber-900 dark:border-amber-800 dark:bg-amber-950/40 dark:text-amber-100"
                  data-testid="demo-example-banner"
                  role="status"
                >
                  Demo / non-operational example: {demoExampleLabel}
                </p>
              )}
              {inputMode === 'ahl_bulletin' && (
                <p className="mb-2 text-xs text-gray-600 dark:text-gray-400">
                  AHL bulletins are split and converted via{' '}
                  <code>POST /api/v1/convert-bulletin</code>.
                </p>
              )}
              {inputMode === 'collect_iwxxm' && (
                <p className="mb-2 text-xs text-amber-800 dark:text-amber-200">
                  IWXXM COLLECT / FTBP path uses{' '}
                  <code>POST /api/v1/ingest-collect</code> (placeholder — returns 501
                  until member extract ships).
                </p>
              )}
              {bulletinSummary && (
                <p
                  className="mb-2 rounded border border-blue-200 bg-blue-50 px-2 py-1 text-xs text-blue-900 dark:border-blue-800 dark:bg-blue-950/40 dark:text-blue-100"
                  data-testid="bulletin-summary"
                >
                  {bulletinSummary}
                </p>
              )}
              {placeholderNotice && (
                <p
                  className="mb-2 rounded border border-amber-300 bg-amber-50 px-2 py-1 text-xs text-amber-900 dark:border-amber-700 dark:bg-amber-950/40 dark:text-amber-100"
                  data-testid="placeholder-notice"
                  role="status"
                >
                  {placeholderNotice}
                </p>
              )}
              <FailedTacCue failedSpans={failedSpans} />
              <div className="grid grid-cols-1 gap-3 lg:grid-cols-2 lg:items-stretch">
                <div className="min-w-0">
                  <TacEditor
                    id="manual-input"
                    value={manualInput}
                    onChange={setManualInput}
                    readOnly={isReadOnly}
                    placeholder="SPECI BGSF 282350Z 10RMF50MT 9999 SCT110 BKN130 0RN130 NN7/N11 Q1021"
                    aria-label="Enter METAR data manually"
                    className="min-h-[160px] focus-within:ring-2 focus-within:ring-blue-500"
                    failedSpans={failedSpans}
                    issueSpans={issueSpans}
                    onSpanFix={applyLintFix}
                  />
                  <DecodePanel
                    segments={decodeSegments}
                    residuals={decodeResiduals}
                    summary={decodeSummary}
                    product={decodeProduct}
                    loading={decodeLoading}
                    error={decodeError}
                    defaultOpen
                  />
                </div>
                <IwxxmPreviewPane
                  xml={previewXml}
                  status={previewStatus}
                  mode={previewMode}
                  softFailDetail={previewSoftFailDetail}
                  failedSpanCount={failedSpans.length}
                  onFailedSpanFocus={() => {
                    document
                      .querySelector('[data-testid="failed-tac-cue"]')
                      ?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                  }}
                />
              </div>
              <div className="mt-3 flex flex-col gap-2 sm:flex-row sm:items-center sm:gap-6">
                <SoftPreviewControl
                  checked={softPreview}
                  onChange={setSoftPreview}
                  disabled={isReadOnly || isBusy}
                />
                <LiveIwxxmToggle
                  checked={liveIwxxm}
                  onChange={setLiveIwxxm}
                  disabled={isReadOnly || isBusy}
                />
              </div>
              <WorkbenchConsole
                lines={consoleLines}
                minLogLevel={conversionParams.logLevel as ConvertLogLevel}
                onLineAction={applyLintFix}
                catalogByCode={lintCatalogByCode}
                catalogEntries={lintCatalogEntries}
                onClear={() => {
                  clearConsole();
                  appendConsole({
                    level: 'info',
                    source: 'console',
                    message: 'cleared',
                  });
                }}
              />

              {/* Compact file upload — secondary to the TAC console */}
              <Card
                className={`mt-4 border-2 border-dashed p-3 shadow-none transition-colors ${
                  isDragging
                    ? 'border-blue-500 bg-blue-50 dark:border-blue-400 dark:bg-blue-950'
                    : 'border-gray-300 bg-white dark:border-gray-700 dark:bg-gray-800'
                }`}
                onDrop={handleDrop}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                role="button"
                aria-label="File drop zone - Drop files here or click to select files"
                tabIndex={0}
                data-testid="compact-file-drop-zone"
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    fileInputRef.current?.click();
                  }
                }}
              >
                <div className="flex flex-col items-stretch gap-2 sm:flex-row sm:items-center sm:justify-between">
                  <div className="flex min-w-0 items-center gap-2">
                    <Upload
                      className="h-5 w-5 shrink-0 text-gray-400 dark:text-gray-500"
                      aria-hidden="true"
                    />
                    <div className="min-w-0 text-left">
                      <p className="text-sm text-gray-900 dark:text-white">
                        Drop TAC files or select
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        Multiple files · .txt, .metar, .tac, .xml, .gz
                      </p>
                    </div>
                  </div>
                  <input
                    ref={fileInputRef}
                    type="file"
                    multiple
                    accept=".txt,.metar,.tac,.xml,.gz,text/plain,application/gzip,application/xml,text/xml"
                    className="hidden"
                    onChange={(e) => handleFileSelect(e.target.files)}
                    aria-label="Select TAC files to upload"
                  />
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation();
                      fileInputRef.current?.click();
                    }}
                    className="shrink-0 dark:bg-gray-700 dark:text-white dark:hover:bg-gray-600 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                    aria-label="Browse and select files"
                  >
                    Select Files
                  </Button>
                </div>
              </Card>
            </div>

            {/* Output filename for manual input (#664 / EV-005) */}
            <div className="mb-6">
              <Label
                htmlFor="output-filename"
                className="block mb-2 text-base font-medium text-gray-900 dark:text-white"
              >
                Output filename (optional)
              </Label>
              <Input
                id="output-filename"
                data-testid="output-filename-input"
                value={outputFilename}
                onChange={(e) => setOutputFilename(e.target.value)}
                readOnly={isReadOnly}
                placeholder="manual_input"
                className="text-sm dark:bg-gray-800 dark:text-white dark:border-gray-700 focus:ring-2 focus:ring-blue-500"
                aria-label="Output filename for manually entered METAR downloads"
              />
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Applies to manually entered METAR downloads only. The <code>.xml</code>{' '}
                extension is added automatically; leave blank to use{' '}
                <code>manual_input</code>. Saves as{' '}
                <code data-testid="output-filename-preview">
                  {sanitizeOutputFilename(outputFilename)}.xml
                </code>
                .
              </p>
            </div>

            {/* Conversion Parameters */}
            <Card className="mb-6 p-6 bg-white dark:bg-gray-800 dark:border-gray-700">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
                  Conversion Parameters
                </h3>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setIsParamsExpanded(!isParamsExpanded)}
                  className="hover:bg-gray-100 dark:hover:bg-gray-700 focus:ring-2 focus:ring-gray-500"
                  aria-label={
                    isParamsExpanded ? 'Collapse parameters' : 'Expand parameters'
                  }
                >
                  {isParamsExpanded ? (
                    <ChevronUp
                      className="w-4 h-4 text-gray-600 dark:text-gray-400"
                      aria-hidden="true"
                    />
                  ) : (
                    <ChevronDown
                      className="w-4 h-4 text-gray-600 dark:text-gray-400"
                      aria-hidden="true"
                    />
                  )}
                </Button>
              </div>
              <div
                className={`grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 ${isParamsExpanded ? '' : 'hidden'}`}
              >
                {/* Bulletin ID */}
                <div>
                  <Label htmlFor="param-bulletin-id" className="dark:text-white mb-2">
                    Bulletin ID
                  </Label>
                  <Input
                    id="param-bulletin-id"
                    value={conversionParams.bulletinId}
                    onChange={(e) =>
                      setConversionParams((prev) => ({
                        ...prev,
                        bulletinId: e.target.value.toUpperCase(),
                      }))
                    }
                    placeholder="SAAA00"
                    maxLength={6}
                    className="dark:bg-gray-700 dark:text-white dark:border-gray-600"
                  />
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    Format: 4 letters + 2 digits. Sent as <code>bulletin_id</code> on
                    Convert.
                  </p>
                </div>

                {/* Issuing Center */}
                <IcaoAutocomplete
                  label="Issuing Center (ICAO)"
                  id="param-issuing-center"
                  value={conversionParams.issuingCenter}
                  onChange={(value) =>
                    setConversionParams((prev) => ({ ...prev, issuingCenter: value }))
                  }
                  placeholder="KWBC"
                  maxLength={4}
                  helperText="4-letter ICAO code — sent as issuing_center on Convert"
                />
                <AirportDetailsCard icao={conversionParams.issuingCenter} />

                {/* F6.e Product — primary control next to Manual TAC Input (#param-product) */}

                {/* F6.e Profile */}
                <div>
                  <Label htmlFor="param-profile" className="dark:text-white mb-2">
                    Profile
                  </Label>
                  <select
                    id="param-profile"
                    aria-label="Profile"
                    value={conversionParams.profile}
                    onChange={(e) =>
                      setConversionParams((prev) => ({
                        ...prev,
                        profile: e.target.value as IwxxmProfile,
                      }))
                    }
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="annex3">annex3 (International)</option>
                    <option value="iwxxm_us">iwxxm_us (US extensions)</option>
                  </select>
                </div>

                {/* IWXXM Version */}
                <div>
                  <Label htmlFor="param-iwxxm-version" className="dark:text-white mb-2">
                    IWXXM Version
                  </Label>
                  <select
                    id="param-iwxxm-version"
                    value={conversionParams.iwxxmVersion}
                    onChange={(e) =>
                      setConversionParams((prev) => ({
                        ...prev,
                        iwxxmVersion: e.target.value as IWXXMVersion,
                      }))
                    }
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="2025-2">2025-2 (Latest)</option>
                    <option value="2023-1">2023-1 (Previous)</option>
                  </select>
                </div>

                {/* On Error */}
                <div>
                  <Label htmlFor="param-on-error" className="dark:text-white mb-2">
                    On Error Behavior
                  </Label>
                  <select
                    id="param-on-error"
                    value={conversionParams.onError}
                    onChange={(e) =>
                      setConversionParams((prev) => ({
                        ...prev,
                        onError: e.target.value as OnErrorBehavior,
                      }))
                    }
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="skip">Skip - Continue, skip invalid</option>
                    <option value="fail">Fail - Stop on first error</option>
                    <option value="warn">Warn - Continue with warnings</option>
                  </select>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    Fail sets API <code>stop_on_error=true</code>; Skip/Warn leave it
                    false.
                  </p>
                </div>

                {/* Log Level */}
                <div>
                  <Label htmlFor="param-log-level" className="dark:text-white mb-2">
                    Log Level
                  </Label>
                  <select
                    id="param-log-level"
                    value={conversionParams.logLevel}
                    onChange={(e) =>
                      setConversionParams((prev) => ({
                        ...prev,
                        logLevel: e.target.value as LogLevel,
                      }))
                    }
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="DEBUG">DEBUG</option>
                    <option value="INFO">INFO (Default)</option>
                    <option value="WARNING">WARNING</option>
                    <option value="ERROR">ERROR</option>
                    <option value="CRITICAL">CRITICAL</option>
                  </select>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    Filters conversion / validation / lint process messages for input
                    and output (Conversion log + workbench console). Sent as{' '}
                    <code>log_level</code> on Convert. Not the server process env{' '}
                    <code>LOG_LEVEL</code>.
                  </p>
                </div>

                {/* Validation Options */}
                <div className="flex flex-col gap-3">
                  <Label className="dark:text-white">Validation Options</Label>
                  <label className="flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={conversionParams.strictValidation}
                      onChange={(e) =>
                        setConversionParams((prev) => ({
                          ...prev,
                          strictValidation: e.target.checked,
                        }))
                      }
                      className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                      data-testid="strict-validation-checkbox"
                    />
                    <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">
                      Strict Validation
                    </span>
                  </label>
                  <p className="text-xs text-gray-500 dark:text-gray-400 -mt-1 ml-6">
                    When on (and soft-preview off), Convert sets{' '}
                    <code>validate_output=true</code> with{' '}
                    <code>validation_level=comprehensive</code> (XSD + Schematron).
                  </p>
                  <label className="flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={conversionParams.includeNilReasons}
                      onChange={(e) =>
                        setConversionParams((prev) => ({
                          ...prev,
                          includeNilReasons: e.target.checked,
                        }))
                      }
                      className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                      data-testid="include-nil-reasons-checkbox"
                    />
                    <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">
                      Include Nil Reasons
                    </span>
                  </label>
                  <p className="text-xs text-gray-500 dark:text-gray-400 -mt-1 ml-6">
                    Sent as <code>include_nil_reasons</code>. Engine may still emit
                    nilReason on NIL TAC until full honor lands (accepted + logged).
                  </p>
                </div>
              </div>
            </Card>

            {/* Action Buttons — fixed strip; status lives outside so busy/save text cannot reflow */}
            <div className="mb-8" data-testid="action-button-strip">
              <div
                className="mb-2 flex h-5 items-center"
                aria-live="polite"
                data-testid="autosave-indicator"
              >
                {saveIndicatorLabel ? (
                  <span className="text-sm text-gray-600 dark:text-gray-400">
                    {saveIndicatorLabel}
                  </span>
                ) : (
                  <span className="sr-only">Autosave idle</span>
                )}
              </div>
              <div className="flex min-h-10 flex-wrap items-center gap-3">
                <Button
                  type="button"
                  variant="outline"
                  onClick={handleNewMetar}
                  disabled={isBusy}
                  data-testid="new-metar-button"
                  aria-label="Start a new METAR session"
                  className="min-w-[7.5rem]"
                >
                  New METAR
                </Button>
                <Button
                  data-testid="convert-button"
                  onClick={handleConvert}
                  disabled={convertDisabled}
                  className="min-w-[7.5rem] bg-blue-500 hover:bg-blue-600 dark:bg-blue-600 dark:hover:bg-blue-700 text-white text-base disabled:opacity-50 disabled:cursor-not-allowed focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                  aria-busy={isConverting}
                  aria-label={
                    isConverting
                      ? 'Converting files, please wait'
                      : 'Convert METAR files to IWXXM XML'
                  }
                >
                  <Loader2
                    className={`w-4 h-4 animate-spin ${isConverting ? '' : 'invisible'}`}
                    aria-hidden="true"
                  />
                  Convert
                </Button>
                <Button
                  data-testid="convert-and-send-button"
                  onClick={handleConvertAndSend}
                  disabled={convertDisabled}
                  className="min-w-[9.5rem] bg-indigo-500 hover:bg-indigo-600 dark:bg-indigo-600 dark:hover:bg-indigo-700 text-white text-base disabled:opacity-50 disabled:cursor-not-allowed focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                  aria-busy={isConvertAndSending}
                  aria-label={
                    isConvertAndSending
                      ? 'Converting and sending files, please wait'
                      : 'Convert METAR files to IWXXM XML and send to database'
                  }
                >
                  <Loader2
                    className={`w-4 h-4 animate-spin ${isConvertAndSending ? '' : 'invisible'}`}
                    aria-hidden="true"
                  />
                  Convert&Send
                </Button>
                <Button
                  onClick={() => setIsUploadDialogOpen(true)}
                  disabled={isBusy || !hasConverted || isReadOnly}
                  variant="outline"
                  className="min-w-[13.5rem] bg-green-600 text-white hover:bg-green-700 dark:bg-green-700 dark:hover:bg-green-800 text-base disabled:opacity-50 disabled:cursor-not-allowed focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
                  aria-label={`Upload ${convertedFiles.length} converted files to database`}
                >
                  <Database className="w-4 h-4" aria-hidden="true" />
                  Upload to Database
                  <span className="inline-block min-w-[1.75rem] tabular-nums">
                    ({convertedFiles.length})
                  </span>
                </Button>
                <Button
                  type="button"
                  data-testid="open-dissemination-drawer"
                  onClick={() => setIsDisseminationOpen(true)}
                  disabled={isBusy || isReadOnly}
                  variant="outline"
                  className="min-w-[10rem] bg-teal-600 text-white hover:bg-teal-700 dark:bg-teal-700 dark:hover:bg-teal-800 text-base disabled:opacity-50 disabled:cursor-not-allowed focus:ring-2 focus:ring-teal-500 focus:ring-offset-2"
                  aria-label="Open dissemination drawer for BYOC upload or publish"
                >
                  Disseminate
                </Button>
                <Button
                  onClick={handleDownloadAll}
                  disabled={isBusy || !hasConverted}
                  variant="outline"
                  className="min-w-[10rem] bg-gray-600 text-white hover:bg-gray-700 dark:bg-gray-700 dark:hover:bg-gray-600 text-base disabled:opacity-50 disabled:cursor-not-allowed focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
                  aria-label={`Download all ${convertedFiles.length} converted files as ZIP`}
                >
                  Download ZIP
                  <span className="inline-block min-w-[1.75rem] tabular-nums">
                    ({convertedFiles.length})
                  </span>
                </Button>
                <Button
                  onClick={handleClear}
                  variant="outline"
                  className="min-w-[5.5rem] bg-gray-600 text-white hover:bg-gray-700 dark:bg-gray-700 dark:hover:bg-gray-600 text-base focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
                  aria-label="Clear all pending files and manual input"
                >
                  Clear
                </Button>
              </div>
            </div>

            {conversionLog && (
              <ErrorLogPanel
                log={conversionLog}
                minLogLevel={conversionParams.logLevel as ConvertLogLevel}
              />
            )}

            {/* Conversion Status Display */}
            {conversionStatus.type !== 'idle' && (
              <div
                className={`mb-8 p-4 rounded-lg border-2 flex items-start gap-3 ${
                  conversionStatus.type === 'loading'
                    ? 'bg-blue-50 dark:bg-blue-900/20 border-blue-300 dark:border-blue-700'
                    : conversionStatus.type === 'timeout'
                      ? 'bg-red-50 dark:bg-red-900/20 border-red-300 dark:border-red-700'
                      : 'bg-red-50 dark:bg-red-900/20 border-red-300 dark:border-red-700'
                }`}
              >
                <div className="pt-1">
                  {conversionStatus.type === 'loading' ? (
                    <Loader2
                      className="w-5 h-5 text-blue-600 dark:text-blue-400 animate-spin flex-shrink-0"
                      aria-hidden="true"
                    />
                  ) : conversionStatus.type === 'timeout' ? (
                    <AlertCircle
                      className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0"
                      aria-hidden="true"
                    />
                  ) : (
                    <XCircle
                      className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0"
                      aria-hidden="true"
                    />
                  )}
                </div>
                <div className="flex-1">
                  <p
                    className={`font-semibold ${
                      conversionStatus.type === 'loading'
                        ? 'text-blue-900 dark:text-blue-100'
                        : 'text-red-900 dark:text-red-100'
                    }`}
                  >
                    {conversionStatus.type === 'loading'
                      ? 'Converting...'
                      : conversionStatus.type === 'timeout'
                        ? 'Conversion Timeout'
                        : conversionStatus.type === 'send_error'
                          ? 'Send Error'
                          : 'Conversion Error'}
                  </p>
                  {conversionStatus.message && (
                    <p
                      className={`text-sm mt-1 ${
                        conversionStatus.type === 'loading'
                          ? 'text-blue-800 dark:text-blue-200'
                          : 'text-red-800 dark:text-red-200'
                      }`}
                    >
                      {conversionStatus.message}
                    </p>
                  )}
                </div>
              </div>
            )}

            {/* Pending Files */}
            {pendingFiles.length > 0 && (
              <div className="mb-8" role="region" aria-label="Pending files queue">
                <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">
                  Pending Files
                </h2>
                <div className="space-y-2">
                  {pendingFiles.map((file) => (
                    <Card
                      key={file.id}
                      className="p-4 bg-white dark:bg-gray-800 dark:border-gray-700"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <FileText
                            className="w-5 h-5 text-blue-500 dark:text-blue-400"
                            aria-hidden="true"
                          />
                          <div>
                            <p className="text-base font-medium text-gray-900 dark:text-white">
                              {file.name}
                            </p>
                            <p className="text-sm text-gray-500 dark:text-gray-400">
                              {file.content.split('\n').length} line(s)
                            </p>
                          </div>
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => removePendingFile(file.id)}
                          className="hover:bg-gray-100 dark:hover:bg-gray-700 focus:ring-2 focus:ring-red-500"
                          aria-label={`Remove ${file.name} from queue`}
                        >
                          <X
                            className="w-4 h-4 text-gray-600 dark:text-gray-400"
                            aria-hidden="true"
                          />
                        </Button>
                      </div>
                    </Card>
                  ))}
                </div>
              </div>
            )}

            {/* Results */}
            {convertedFiles.length > 0 && (
              <div role="region" aria-label="Conversion results">
                <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">
                  Results
                </h2>
                <div className="space-y-4">
                  {convertedFiles.map((file) => (
                    <Card
                      key={file.id}
                      className="p-4 bg-white dark:bg-gray-800 dark:border-gray-700"
                    >
                      <div className="flex items-center justify-between mb-3 flex-wrap gap-2">
                        <div className="min-w-0 flex-1">
                          <div className="flex flex-wrap items-center gap-2">
                            <p className="text-base font-medium text-gray-900 dark:text-white">
                              {file.displayTitle}
                            </p>
                            {file.manualLineIndex != null &&
                            file.manualLineTotal != null ? (
                              <span className="inline-flex items-center rounded-full bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-800 dark:bg-blue-900/40 dark:text-blue-200">
                                Line {file.manualLineIndex} of {file.manualLineTotal}
                              </span>
                            ) : null}
                          </div>
                          {file.displayTitle !== file.originalName ? (
                            <p className="text-sm text-gray-500 dark:text-gray-400 mt-0.5">
                              Download: {file.originalName}
                            </p>
                          ) : null}
                          {file.originalContent.length > 60 &&
                          file.displayTitle !==
                            file.originalContent.trim().replace(/\s+/g, ' ') ? (
                            <p className="text-xs font-mono text-gray-600 dark:text-gray-400 mt-1 break-all">
                              {truncateTacSnippet(file.originalContent)}
                            </p>
                          ) : null}
                        </div>
                        <div className="flex gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleDownloadSingle(file)}
                            className="bg-blue-500 text-white hover:bg-blue-600 dark:bg-blue-600 dark:hover:bg-blue-700 text-sm border-0 focus:ring-2 focus:ring-blue-500"
                            aria-label={`Download ${file.originalName} as XML`}
                          >
                            <Download className="w-4 h-4 mr-1" aria-hidden="true" />
                            Download
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleCopy(file.convertedContent)}
                            className="bg-blue-500 text-white hover:bg-blue-600 dark:bg-blue-600 dark:hover:bg-blue-700 text-sm border-0 focus:ring-2 focus:ring-blue-500"
                            aria-label={`Copy ${file.originalName} content to clipboard`}
                          >
                            <Copy className="w-4 h-4 mr-1" aria-hidden="true" />
                            Copy
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => removeConvertedFile(file.id)}
                            className="hover:bg-gray-100 dark:hover:bg-gray-700 focus:ring-2 focus:ring-red-500"
                            aria-label={`Remove ${file.originalName} from results`}
                          >
                            <X
                              className="w-4 h-4 text-gray-600 dark:text-gray-400"
                              aria-hidden="true"
                            />
                          </Button>
                        </div>
                      </div>
                      <div
                        className="bg-gray-100 dark:bg-gray-900 text-gray-800 dark:text-gray-200 p-4 rounded text-sm overflow-x-auto mb-3 border border-gray-200 dark:border-gray-700"
                        role="region"
                        aria-label={`Original TAC input for ${file.displayTitle}`}
                      >
                        <p className="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400 mb-2">
                          Source TAC
                        </p>
                        {file.originalContent ? (
                          <pre className="whitespace-pre-wrap break-all font-mono">
                            {file.originalContent}
                          </pre>
                        ) : (
                          <p className="text-sm italic text-gray-500 dark:text-gray-400">
                            Original TAC unavailable for this result.
                          </p>
                        )}
                      </div>
                      <div
                        className="bg-gray-900 dark:bg-gray-950 text-green-400 dark:text-green-300 p-4 rounded text-sm overflow-x-auto"
                        role="region"
                        aria-label={`Converted XML content for ${file.originalName}`}
                      >
                        <pre className="whitespace-pre-wrap break-all font-mono">
                          {file.convertedContent}
                        </pre>
                      </div>
                    </Card>
                  ))}
                </div>
              </div>
            )}

            {/* Footer */}
            <div className="mt-12 text-center text-sm text-gray-500 dark:text-gray-400">
              <p>
                TAC → IWXXM conversion powered by{' '}
                <code className="text-xs">tac2iwxxm</code>, with{' '}
                <code className="text-xs">tac-validate</code> and{' '}
                <code className="text-xs">iwxxm-validate</code>. Downloads are IWXXM{' '}
                <code className="text-xs">.xml</code> files.
              </p>
              <p className="mt-2">
                <button
                  type="button"
                  className="underline underline-offset-2 hover:text-gray-700 dark:hover:text-gray-200"
                  onClick={() => setIsPrivacySettingsOpen(true)}
                  aria-label="Open privacy settings"
                >
                  Privacy settings
                </button>
              </p>
            </div>
          </div>
          {onLoadWorkSession && (
            <aside className="lg:sticky lg:top-8 lg:mt-8 lg:self-start">
              <WorkHistorySidebar
                activeSessionId={activeWorkSessionId}
                onSelectSession={onLoadWorkSession}
                onOpenHistory={onOpenHistory}
              />
            </aside>
          )}
        </div>
      </div>

      {/* Database Upload Dialog */}
      <DatabaseUploadDialog
        convertedFiles={convertedFiles}
        isOpen={isUploadDialogOpen}
        onClose={() => setIsUploadDialogOpen(false)}
      />

      <DisseminationDrawer
        open={isDisseminationOpen}
        onOpenChange={setIsDisseminationOpen}
        iwxxmXml={convertedFiles[0]?.convertedContent}
        tacText={manualInput || undefined}
        product={conversionParams.product === 'SPECI' ? 'speci' : 'metar'}
      />

      {/* User Preferences Dialog */}
      <UserPreferencesDialog
        isOpen={isPreferencesDialogOpen}
        onClose={() => setIsPreferencesDialogOpen(false)}
        userEmail="Operator"
        onPreferencesSaved={handlePreferencesSaved}
      />

      <PrivacySettingsDialog
        isOpen={isPrivacySettingsOpen}
        onClose={() => setIsPrivacySettingsOpen(false)}
      />
    </div>
  );
}

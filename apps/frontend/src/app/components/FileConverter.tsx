import { useState, useRef, useEffect, useLayoutEffect, useCallback } from 'react';
import { Button } from './ui/button';
import { Card } from './ui/card';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { TacEditor } from './TacEditor';
import { DecodePanel } from './DecodePanel';
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
  Shield,
  LogOut,
  AlertCircle,
  XCircle,
} from 'lucide-react';
import JSZip from 'jszip';
import { toast } from 'sonner';
import { ThemeToggle } from './ThemeToggle';
import { DatabaseUploadDialog } from './DatabaseUploadDialog';
import { UserPreferencesDialog } from './UserPreferencesDialog';
import { IcaoAutocomplete } from './IcaoAutocomplete';
import { AirportDetailsCard } from './AirportDetailsCard';
import { signOutWithScope } from '/utils/supabase/logout';
import { convertMetarToIwxxm as callBackendConversion, decodeTac } from '/utils/api';
import type { DecodeResidual, DecodeSegment } from '/utils/api';
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
import {
  readGuestConverterState,
  saveGuestConverterState,
} from '/utils/guestConverterState';
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
  onLogout: () => void;
  userEmail: string;
  accessToken?: string;
  isGuest?: boolean;
  onRequestLogin?: () => void;
  onSwitchToAdmin?: () => void;
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
  onLogout,
  userEmail,
  accessToken,
  isGuest = false,
  onRequestLogin,
  onSwitchToAdmin,
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
  const [decodeSegments, setDecodeSegments] = useState<DecodeSegment[]>([]);
  const [decodeResiduals, setDecodeResiduals] = useState<DecodeResidual[]>([]);
  const [decodeProduct, setDecodeProduct] = useState<string | undefined>();
  const [decodeLoading, setDecodeLoading] = useState(false);
  const [decodeError, setDecodeError] = useState<string | null>(null);
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
  const [isPreferencesDialogOpen, setIsPreferencesDialogOpen] = useState(false);
  const [isParamsExpanded, setIsParamsExpanded] = useState(false);
  const [isLogoutMenuOpen, setIsLogoutMenuOpen] = useState(false);
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
      accessToken,
      sessionId: activeWorkSessionId ?? null,
      sessionStatus: loadedWorkSession?.status ?? null,
      onSessionSaved: (session) => onSessionUpdated?.(session),
      onSessionIdAssigned: (id) => onActiveSessionIdChange?.(id),
    });

  const handleLogoutWithScope = async (scope: 'global' | 'local' | 'others') => {
    const success = await signOutWithScope(scope);
    if (success) {
      setIsLogoutMenuOpen(false);
      setTimeout(() => {
        onLogout();
      }, 500);
    }
  };

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
    if (!accessToken || isReadOnly) {
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
    accessToken,
    isReadOnly,
  ]);

  useEffect(() => {
    if (accessToken || isGuest === false) {
      return;
    }
    saveGuestConverterState(buildSnapshot());
    // eslint-disable-next-line react-hooks/exhaustive-deps -- guest state mirror
  }, [
    manualInput,
    pendingFiles,
    convertedFiles,
    conversionLog,
    outputFilename,
    isGuest,
    accessToken,
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

    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      try {
        const content = await file.text();
        newPendingFiles.push({
          id: `${file.name}-${Date.now()}-${i}`,
          name: file.name,
          content: content,
        });
      } catch (error) {
        console.error(`Error reading file ${file.name}:`, error);
        toast.error(`Failed to read ${file.name}`);
      }
    }

    setPendingFiles((prev) => [...prev, ...newPendingFiles]);
    toast.success(`${newPendingFiles.length} file(s) added to queue`);
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
  } | null> => {
    if (pendingFiles.length === 0 && !manualInput.trim()) {
      toast.error('Please add files or enter manual input');
      return null;
    }

    setConversionStatus({ type: 'loading', message: 'Converting...' });
    setConversionLog(null);

    try {
      const newConvertedFiles: ConvertedFile[] = [];

      const filesToConvert: File[] = pendingFiles.map((file) => {
        return new File([file.content], file.name, { type: 'text/plain' });
      });

      console.log('[FileConverter] Starting conversion with:', {
        manualInput: manualInput.trim() ? 'provided' : 'none',
        fileCount: filesToConvert.length,
        accessToken: accessToken ? `${accessToken.substring(0, 20)}...` : 'MISSING',
      });

      const tacForDetect = [manualInput.trim(), ...pendingFiles.map((f) => f.content)]
        .filter(Boolean)
        .join('\n');
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

      const response = await callBackendConversion({
        manualText: manualInput.trim() || undefined,
        files: filesToConvert.length > 0 ? filesToConvert : undefined,
        product: resolvedProduct,
        profile: conversionParams.profile,
        iwxxmVersion: conversionParams.iwxxmVersion,
        validateOutput: false,
        accessToken: accessToken,
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

      if (newConvertedFiles.length === 0) {
        if (hasLog) {
          setConversionLog({ errors: responseErrors, issues: responseIssues });
        }
        const failureMessage = responseErrors[0] ?? 'No files were converted';
        toast.error(failureMessage);
        setConversionStatus({ type: 'error', message: failureMessage });
        return null;
      }

      setConvertedFiles(newConvertedFiles);
      setPendingFiles([]);
      setManualInput('');
      setConversionLog(
        hasLog ? { errors: responseErrors, issues: responseIssues } : null,
      );
      setConversionStatus({ type: 'idle' });
      return { files: newConvertedFiles, hasErrors: hasLog };
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
        toast.success(`Successfully converted ${result.files.length} file(s)`);
        if (accessToken) {
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
        }
      } else if (accessToken) {
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
    if (!accessToken) {
      toast.error('Authentication required. Please log in again.');
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
        await persistSession(
          buildSnapshot({
            convertedFiles: result.files.map((file) => ({
              originalName: file.originalName,
              originalContent: file.originalContent,
              convertedContent: file.convertedContent,
            })),
            manualInput: '',
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
          accessToken,
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
    setOutputFilename('');
    setConvertedFiles([]);
    setConversionLog(null);
    setConversionStatus({ type: 'idle' });
    toast.info('Queue cleared');
  };

  const isBusy = isConverting || isConvertAndSending;
  const hasInput = pendingFiles.length > 0 || !!manualInput.trim();
  const hasConverted = convertedFiles.length > 0;
  const convertDisabled = isBusy || !hasInput || isReadOnly;

  const runDecode = useCallback(
    async (open: boolean) => {
      if (!open) {
        return;
      }
      const text = manualInput.trim();
      if (!text) {
        setDecodeSegments([]);
        setDecodeResiduals([]);
        setDecodeProduct(undefined);
        setDecodeError(null);
        return;
      }
      const product = resolveConvertProduct(conversionParams.product, text);
      setDecodeLoading(true);
      setDecodeError(null);
      try {
        const result = await decodeTac({
          manualText: text,
          product,
          accessToken,
        });
        setDecodeSegments(result.segments);
        setDecodeResiduals(result.residuals);
        setDecodeProduct(result.product);
      } catch (err) {
        setDecodeError(err instanceof Error ? err.message : 'Decode failed');
        setDecodeSegments([]);
        setDecodeResiduals([]);
      } finally {
        setDecodeLoading(false);
      }
    },
    [manualInput, conversionParams.product, accessToken],
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
              {onSwitchToAdmin && (
                <div className="flex items-center gap-2">
                  <Shield
                    className="w-4 h-4 text-purple-600 dark:text-purple-400"
                    aria-hidden="true"
                  />
                  <select
                    value="converter"
                    onChange={(e) => {
                      if (e.target.value === 'admin') {
                        console.log('User selected admin view from dropdown');
                        onSwitchToAdmin?.();
                      }
                    }}
                    className="px-3 py-1.5 text-sm font-medium bg-purple-600 text-white border-0 rounded-md hover:bg-purple-700 dark:bg-purple-700 dark:hover:bg-purple-800 focus:ring-2 focus:ring-purple-500 focus:outline-none cursor-pointer"
                    aria-label="Switch view"
                  >
                    <option
                      value="converter"
                      className="bg-white text-gray-900 dark:bg-gray-800 dark:text-white"
                    >
                      File Converter
                    </option>
                    <option
                      value="admin"
                      className="bg-white text-gray-900 dark:bg-gray-800 dark:text-white"
                    >
                      Admin Dashboard
                    </option>
                  </select>
                </div>
              )}
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

              {/* Logout Menu */}
              <div className="relative">
                <Button
                  variant="outline"
                  className="bg-red-500 text-white hover:bg-red-600 dark:bg-red-600 dark:hover:bg-red-700 border-0"
                  aria-label={isGuest ? 'Sign in to save work' : 'Logout options'}
                  onClick={() => {
                    if (isGuest) {
                      onRequestLogin?.();
                      return;
                    }
                    setIsLogoutMenuOpen(!isLogoutMenuOpen);
                  }}
                >
                  <LogOut className="w-4 h-4 mr-2" aria-hidden="true" />
                  {isGuest ? 'Sign in' : 'Logout'}
                  <ChevronDown className="w-4 h-4 ml-1" aria-hidden="true" />
                </Button>

                {isLogoutMenuOpen && !isGuest && (
                  <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-md shadow-lg z-10">
                    <div className="p-3 space-y-2">
                      <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 px-2 py-1">
                        Sign out scope:
                      </p>

                      <button
                        onClick={() => handleLogoutWithScope('local')}
                        className="w-full text-left px-3 py-2 rounded-md text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                        aria-label="Sign out from this device only"
                      >
                        <div className="font-medium">This Device</div>
                        <div className="text-xs text-gray-500 dark:text-gray-400">
                          Only this session
                        </div>
                      </button>

                      <button
                        onClick={() => handleLogoutWithScope('global')}
                        className="w-full text-left px-3 py-2 rounded-md text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                        aria-label="Sign out from all devices"
                      >
                        <div className="font-medium">All Devices</div>
                        <div className="text-xs text-gray-500 dark:text-gray-400">
                          Every logged-in session
                        </div>
                      </button>

                      <button
                        onClick={() => handleLogoutWithScope('others')}
                        className="w-full text-left px-3 py-2 rounded-md text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                        aria-label="Sign out from other devices"
                      >
                        <div className="font-medium">Other Devices</div>
                        <div className="text-xs text-gray-500 dark:text-gray-400">
                          Keep this session active
                        </div>
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
          <p className="text-base text-gray-600 dark:text-gray-300">
            Drag & drop one or more METAR TAC files, or type a METAR manually below.
            Click Convert to produce IWXXM XML (downloadable as XML).
          </p>
        </div>

        {/* Drop Zone */}
        <Card
          className={`mb-6 p-12 border-2 border-dashed transition-colors ${
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
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault();
              fileInputRef.current?.click();
            }
          }}
        >
          <div className="flex flex-col items-center justify-center text-center">
            <Upload
              className="w-12 h-12 text-gray-400 dark:text-gray-500 mb-4"
              aria-hidden="true"
            />
            <p className="text-lg mb-2 text-gray-900 dark:text-white">
              Drop files here or click to select
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
              Supports multiple files
            </p>
            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept=".txt,.metar"
              className="hidden"
              onChange={(e) => handleFileSelect(e.target.files)}
              aria-label="Select METAR files to upload"
            />
            <Button
              variant="outline"
              onClick={() => fileInputRef.current?.click()}
              className="dark:bg-gray-700 dark:text-white dark:hover:bg-gray-600 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              aria-label="Browse and select files"
            >
              Select Files
            </Button>
          </div>
        </Card>

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-[minmax(0,1fr)_280px]">
          <div>
            {/* Manual Input */}
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
              <label
                htmlFor="manual-input"
                className="block mb-2 text-base font-medium text-gray-900 dark:text-white"
              >
                Manual TAC Input
              </label>
              <TacEditor
                id="manual-input"
                value={manualInput}
                onChange={setManualInput}
                readOnly={isReadOnly}
                placeholder="SPECI BGSF 282350Z 10RMF50MT 9999 SCT110 BKN130 0RN130 NN7/N11 Q1021"
                aria-label="Enter METAR data manually"
                className="min-h-[120px] focus-within:ring-2 focus-within:ring-blue-500"
              />
              <DecodePanel
                segments={decodeSegments}
                residuals={decodeResiduals}
                product={decodeProduct}
                loading={decodeLoading}
                error={decodeError}
                onOpenChange={runDecode}
              />
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
                    Format: 4 letters + 2 digits
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
                  helperText="4-letter ICAO code"
                />
                <AirportDetailsCard icao={conversionParams.issuingCenter} />

                {/* F6.e Product */}
                <div>
                  <Label htmlFor="param-product" className="dark:text-white mb-2">
                    Product
                  </Label>
                  <select
                    id="param-product"
                    aria-label="Product"
                    value={conversionParams.product}
                    onChange={(e) =>
                      setConversionParams((prev) => ({
                        ...prev,
                        product: e.target.value as TacProductSelection,
                      }))
                    }
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
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
                </div>

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
                    />
                    <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">
                      Strict Validation
                    </span>
                  </label>
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
                    />
                    <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">
                      Include Nil Reasons
                    </span>
                  </label>
                </div>
              </div>
            </Card>

            {/* Action Buttons */}
            <div className="flex flex-wrap items-center gap-3 mb-8 bg-[rgba(0,0,0,0)]">
              {accessToken && saveIndicatorLabel && (
                <span
                  className="text-sm text-gray-600 dark:text-gray-400"
                  aria-live="polite"
                  data-testid="autosave-indicator"
                >
                  {saveIndicatorLabel}
                </span>
              )}
              {accessToken && (
                <Button
                  type="button"
                  variant="outline"
                  onClick={handleNewMetar}
                  disabled={isBusy}
                  data-testid="new-metar-button"
                  aria-label="Start a new METAR session"
                >
                  New METAR
                </Button>
              )}
              <Button
                data-testid="convert-button"
                onClick={handleConvert}
                disabled={convertDisabled}
                className="bg-blue-500 hover:bg-blue-600 dark:bg-blue-600 dark:hover:bg-blue-700 text-white text-base disabled:opacity-50 disabled:cursor-not-allowed focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                aria-label={
                  isConverting
                    ? 'Converting files, please wait'
                    : 'Convert METAR files to IWXXM XML'
                }
              >
                {isConverting ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" aria-hidden="true" />
                    Converting...
                  </>
                ) : (
                  'Convert'
                )}
              </Button>
              <Button
                data-testid="convert-and-send-button"
                onClick={handleConvertAndSend}
                disabled={convertDisabled || !accessToken}
                className="bg-indigo-500 hover:bg-indigo-600 dark:bg-indigo-600 dark:hover:bg-indigo-700 text-white text-base disabled:opacity-50 disabled:cursor-not-allowed focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                aria-label={
                  isConvertAndSending
                    ? 'Converting and sending files, please wait'
                    : 'Convert METAR files to IWXXM XML and send to database'
                }
              >
                {isConvertAndSending ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" aria-hidden="true" />
                    Converting & Sending...
                  </>
                ) : (
                  'Convert&Send'
                )}
              </Button>
              <Button
                onClick={() => setIsUploadDialogOpen(true)}
                disabled={isBusy || !hasConverted || isReadOnly}
                variant="outline"
                className="bg-green-600 text-white hover:bg-green-700 dark:bg-green-700 dark:hover:bg-green-800 text-base disabled:opacity-50 disabled:cursor-not-allowed focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
                aria-label={`Upload ${convertedFiles.length} converted files to database`}
              >
                <Database className="w-4 h-4 mr-2" aria-hidden="true" />
                Upload to Database{' '}
                {convertedFiles.length > 0 && `(${convertedFiles.length})`}
              </Button>
              <Button
                onClick={handleDownloadAll}
                disabled={isBusy || !hasConverted}
                variant="outline"
                className="bg-gray-600 text-white hover:bg-gray-700 dark:bg-gray-700 dark:hover:bg-gray-600 text-base disabled:opacity-50 disabled:cursor-not-allowed focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
                aria-label={`Download all ${convertedFiles.length} converted files as ZIP`}
              >
                Download ZIP {convertedFiles.length > 0 && `(${convertedFiles.length})`}
              </Button>
              <Button
                onClick={handleClear}
                variant="outline"
                className="bg-gray-600 text-white hover:bg-gray-700 dark:bg-gray-700 dark:hover:bg-gray-600 text-base focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
                aria-label="Clear all pending files and manual input"
              >
                Clear
              </Button>
            </div>

            {conversionLog && <ErrorLogPanel log={conversionLog} />}

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
                Conversion powered by GIFS library Outputs.java raw IWXXM XML serialized
                to .txt for convenience.
              </p>
            </div>
          </div>
          {accessToken && onLoadWorkSession && (
            <aside className="lg:sticky lg:top-8 lg:self-start">
              <WorkHistorySidebar
                accessToken={accessToken}
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
        accessToken={accessToken}
      />

      {/* User Preferences Dialog */}
      <UserPreferencesDialog
        isOpen={isPreferencesDialogOpen}
        onClose={() => setIsPreferencesDialogOpen(false)}
        userEmail={userEmail}
        onPreferencesSaved={handlePreferencesSaved}
      />
    </div>
  );
}

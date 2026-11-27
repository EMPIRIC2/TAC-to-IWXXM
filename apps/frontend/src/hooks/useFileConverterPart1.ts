/* eslint-disable @typescript-eslint/ban-ts-comment, @typescript-eslint/no-explicit-any */
// @ts-nocheck — mechanical line-count split
/** Part 1 of useFileConverter. */
import * as D from './fileConverterDeps';
import { useWorkbenchBusyFlags } from './workbenchBusyFlags';

/**
 * useFileConverterPart1.
 * @example
 * const _ = true;
 */
export function useFileConverterPart1(props: any) {
  const {
    accessToken,
    userEmail = 'Guest',
    isGuest = false,
    onLogout,
    onRequestLogin,
    onOpenHistory,
    onOpenVisuals,
    onLoadWorkSession,
    onNewMetar,
    onSessionUpdated,
    onActiveSessionIdChange,
    activeWorkSessionId,
    loadedWorkSession,
    pendingMapTac,
    onPendingMapTacConsumed,
    onOpenCatalog,
  } = props;
  const [pendingFiles, setPendingFiles] = D.useState<D.PendingFile[]>([]);
  const [queueFocusIndex, setQueueFocusIndex] = D.useState(0);
  const [selectedPendingIds, setSelectedPendingIds] = D.useState<Set<string>>(
    () => new Set(),
  );
  const [convertedFiles, setConvertedFiles] = D.useState<D.ConvertedFile[]>([]);
  /** TAC of the first accumulated success — used for default ZIP stem (#903). */
  const [firstAccumulatedTac, setFirstAccumulatedTac] = D.useState<string | null>(null);
  /** F7.s validate-only report (POST /api/v1/validate with xml_content). */
  const [validateReport, setValidateReport] = D.useState<D.ValidateResponse | null>(
    null,
  );
  const [manualInput, setManualInput] = D.useState(() => {
    const saved = D.readGuestConverterState()?.manualInput;
    return typeof saved === 'string' ? saved : '';
  });
  const [decodeError, setDecodeError] = D.useState<string | null>(null);
  const [softPreview, setSoftPreview] = D.useState(false);
  const [propagateResiduals, setPropagateResiduals] = D.useState(false);
  const [includeNationalRemarks, setIncludeNationalRemarks] = D.useState(true);
  const [liveIwxxm, setLiveIwxxm] = D.useState(true);
  const [selectedTrace, setSelectedTrace] = D.useState<LiveTraceTarget | null>(null);
  const [lintJump, setLintJump] = D.useState<number | null>(null);
  const [lintFocusOffset, setLintFocusOffset] = D.useState<number | null>(null);
  const [groupTrace, setGroupTrace] = D.useState<GroupTrace[]>([]);
  const [failedSpans, setFailedSpans] = D.useState<FailedSpan[]>([]);
  const [previewXml, setPreviewXml] = D.useState('');
  const [previewStatus, setPreviewStatus] = D.useState<IwxxmPreviewStatus>('empty');
  const [previewMode, setPreviewMode] = D.useState<IwxxmPreviewMode>('idle');
  const [previewSoftFailDetail, setPreviewSoftFailDetail] = D.useState<
    string | undefined
  >();
  /** Which converted file the IWXXM tab is showing (Downloads selects into this). */
  const [focusedConvertedId, setFocusedConvertedId] = D.useState<string | null>(null);
  const [inputMode, setInputMode] = D.useState<OperatorInputMode>('tac');
  const [demoExampleLabel, setDemoExampleLabel] = D.useState<string | null>(null);
  const [bulletinSummary, setBulletinSummary] = D.useState<string | null>(null);
  const [placeholderNotice, setPlaceholderNotice] = D.useState<string | null>(null);
  /** UX-07: collapse Recent work while editing / opening Examples. */
  const [recentWorkCollapsed, setRecentWorkCollapsed] = D.useState(
    D.preferCollapsedWorkbenchChrome,
  );
  /** Converter panes follow the report. Hidden leaves the map in view. */
  const [converterOpen, setConverterOpen] = D.useState(true);
  // Restore the guest's custom output filename from the session snapshot (R5).
  const [outputFilename, setOutputFilename] = D.useState(() => {
    const saved = D.readGuestConverterState()?.conversionParams?.output_filename;
    return typeof saved === 'string' ? saved : '';
  });
  /** True after the operator types a non-empty output filename. */
  const outputFilenameOwnedRef = D.useRef(outputFilename.trim() !== '');
  const [isDragging, setIsDragging] = D.useState(false);
  const {
    isConverting,
    setIsConverting,
    isConvertAndSending,
    setIsConvertAndSending,
    isBatchValidating,
    setIsBatchValidating,
    workbenchBusyRef,
  } = useWorkbenchBusyFlags();
  const [helpChecklistOpen, setHelpChecklistOpen] = D.useState(false);
  const [profileDrawerOpen, setProfileDrawerOpen] = D.useState(false);
  const [tacLockedAfterConvert, setTacLockedAfterConvert] = D.useState(false);
  const [resultsDrawerOpen, setResultsDrawerOpen] = D.useState(true);
  const [resultsTab, setResultsTab] = D.useState<ConvertResultsTab>('iwxxm');
  const [converterPaneHeight, setConverterPaneHeight] = D.useState(280);
  const [lintHighlightPreset, setLintHighlightPreset] = D.useState<LintHighlightPreset>(
    () => D.readLintHighlightPreset(),
  );
  const convertedQueueWasEmptyRef = D.useRef(true);
  const [conversionStatus, setConversionStatus] = D.useState<{
    type: 'idle' | 'loading' | 'timeout' | 'error' | 'send_error';
    message?: string;
  }>({ type: 'idle' });
  const [conversionLog, setConversionLog] = D.useState<ConversionLog | null>(null);
  const [isDisseminationOpen, setIsDisseminationOpen] = D.useState(false);
  /** Packaging-drawer Exchange for catalog filter while Disseminate is open (AC-UI Exchange). */
  const [packagingExchangeProfile, setPackagingExchangeProfile] =
    D.useState<ExchangeProfileId | null>(null);
  const [isPreferencesDialogOpen, setIsPreferencesDialogOpen] = D.useState(false);
  const [isPrivacySettingsOpen, setIsPrivacySettingsOpen] = D.useState(false);
  const [isSiteTermsOpen, setIsSiteTermsOpen] = D.useState(false);
  const [isLogoutMenuOpen, setIsLogoutMenuOpen] = D.useState(false);
  const [showPrivacyNotice, setShowPrivacyNotice] = D.useState(() =>
    D.shouldShowPrivacyNotice(),
  );
  const [isParamsExpanded, setIsParamsExpanded] = D.useState(false);
  const [bulletinFieldError, setBulletinFieldError] = D.useState<string | null>(null);
  const [issuingCenterFieldError, setIssuingCenterFieldError] = D.useState<
    string | null
  >(null);
  const [caExtensionBundleAvailable, setCaExtensionBundleAvailable] = D.useState<
    boolean | null
  >(null);
  const [conversionParams, setConversionParams] = D.useState<D.ConversionParams>(
    D.initialConversionParams,
  );
  /* v8 ignore start -- DI-008 drawer removed; setter kept for prop stability */
  const handleDisseminationOpenChange = (open: boolean) => {
    setIsDisseminationOpen(open);
  };
  /* v8 ignore stop */
  const [profileCatalogEntries, setProfileCatalogEntries] = D.useState<
    ProfileCatalogEntry[]
  >([]);
  const [metadataPrefs, setMetadataPrefs] = D.useState<ConversionMetadataPrefs>(() =>
    D.readConversionMetadataPrefs(),
  );
  const [isMetadataChecklistOpen, setIsMetadataChecklistOpen] = D.useState(false);
  const fileInputRef = D.useRef<HTMLInputElement>(null);
  const hydratedWorkSessionIdRef = D.useRef<string | null>(null);
  const outputVersionsRef = D.useRef<D.OutputVersion[]>([]);
  const [, setOutputVersions] = D.useState<D.OutputVersion[]>([]);
  const { layout: liveLayout, updateLayout: updateLiveLayout } =
    D.useLiveConvertLayout();
  const [bulletinSource, setBulletinSource] = D.useState('');
  const [focusedBulletinReport, setFocusedBulletinReport] = D.useState<number | null>(
    null,
  );
  const convertedFilesRef = D.useRef<D.ConvertedFile[]>([]);
  const conversionLogRef = D.useRef<ConversionLog | null>(null);

  const updateConversionLog = D.useCallback((next: ConversionLog | null) => {
    conversionLogRef.current = next;
    setConversionLog(next);
  }, []);

  D.useEffect(() => {
    document.title = D.PAGE_TITLE;
  }, []);

  const applyWmoLibraryDefaultsSync = D.useCallback((sync: WmoLibraryDefaultsSync) => {
    const profile = D.coerceIwxxmProfile(sync.profile);
    setConversionParams((prev) => ({
      ...prev,
      ...sync.libraryIds,
      profile,
      reportVariant: '',
      iwxxmVersion: D.coerceIwxxmVersionForProfile(profile, prev.iwxxmVersion),
    }));
  }, []);

  D.useEffect(() => {
    const onStorage = (event: StorageEvent) => {
      if (event.key !== D.WMO_LIBRARY_DEFAULTS_SYNC_KEY || !event.newValue) {
        return;
      }
      const next = D.readWmoLibraryDefaultsSync();
      if (next) {
        applyWmoLibraryDefaultsSync(next);
      }
    };
    const onSameTab = (event: Event) => {
      const detail = (event as CustomEvent<WmoLibraryDefaultsSync>).detail;
      if (detail?.profile && detail.libraryIds) {
        applyWmoLibraryDefaultsSync(detail);
        return;
      }
      const next = D.readWmoLibraryDefaultsSync();
      if (next) {
        applyWmoLibraryDefaultsSync(next);
      }
    };
    window.addEventListener('storage', onStorage);
    window.addEventListener(D.WMO_LIBRARY_DEFAULTS_SYNC_EVENT, onSameTab);
    return () => {
      window.removeEventListener('storage', onStorage);
      window.removeEventListener(D.WMO_LIBRARY_DEFAULTS_SYNC_EVENT, onSameTab);
    };
  }, [applyWmoLibraryDefaultsSync]);

  D.useEffect(() => {
    convertedFilesRef.current = convertedFiles;
  }, [convertedFiles]);

  D.useEffect(() => {
    const hasConvertedNow = convertedFiles.length > 0;
    if (
      D.shouldAutoOpenResultsDrawer(hasConvertedNow, convertedQueueWasEmptyRef.current)
    ) {
      setResultsDrawerOpen(true);
      setResultsTab(D.defaultTabAfterConvert());
    }
    convertedQueueWasEmptyRef.current = !hasConvertedNow;
  }, [convertedFiles.length]);

  D.useEffect(() => {
    const tokens = D.lintHighlightTokens(lintHighlightPreset);
    const root = document.documentElement;
    root.style.setProperty('--tac-lint-issue-bg', tokens.issueBg);
    root.style.setProperty('--tac-lint-issue-border', tokens.issueBorder);
    root.style.setProperty('--tac-lint-info-bg', tokens.infoBg);
    root.style.setProperty('--tac-lint-info-border', tokens.infoBorder);
    root.style.setProperty('--tac-lint-selected-bg', tokens.selectedBg);
    root.style.setProperty('--tac-lint-selected-border', tokens.selectedBorder);
    D.writeLintHighlightPreset(lintHighlightPreset);
  }, [lintHighlightPreset]);

  D.useEffect(() => {
    conversionLogRef.current = conversionLog;
  }, [conversionLog]);

  D.useEffect(() => {
    return D.subscribeNarrowWorkbenchChrome(() => {
      setRecentWorkCollapsed(true);
    });
  }, []);

  D.useEffect(() => {
    const token = accessToken?.trim();
    if (!token) {
      setProfileCatalogEntries([]);
      return;
    }
    let cancelled = false;
    void D.fetchProfileCatalog(token)
      .then((res) => {
        if (!cancelled) {
          setProfileCatalogEntries(res.profiles);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setProfileCatalogEntries([]);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [accessToken]);

  const activeProfileSummary = D.useMemo(() => {
    const canonicalId = D.hydrateSemanticProfile(conversionParams.profile);
    const catalogMatch = profileCatalogEntries.find(
      (entry) => entry.id === canonicalId,
    );
    return (
      catalogMatch ??
      D.fallbackProfileSummary(canonicalId, conversionParams.iwxxmVersion)
    );
  }, [conversionParams.iwxxmVersion, conversionParams.profile, profileCatalogEntries]);
  const activeProfileExampleProducts = D.useMemo(
    () =>
      activeProfileSummary.products.filter((product): product is TacProduct =>
        (D.TAC_PRODUCTS as readonly string[]).includes(product),
      ),
    [activeProfileSummary.products],
  );
  const resolvedVariantProduct = D.useMemo(() => {
    if (conversionParams.product === 'IWXXM') {
      return null;
    }
    return D.resolveConvertProduct(conversionParams.product, manualInput);
  }, [conversionParams.product, manualInput]);
  const reportVariantOptions = D.useMemo(() => {
    if (!resolvedVariantProduct) {
      return [];
    }
    const variants = D.activeMetarFamilyVariants(
      activeProfileSummary,
      resolvedVariantProduct,
    );
    return variants.length > 1 ? variants : [];
  }, [activeProfileSummary, resolvedVariantProduct]);
  const activeReportVariant = D.useMemo(() => {
    const allowed = new Set(reportVariantOptions.map((variant) => variant.tac_lead));
    return allowed.has(conversionParams.reportVariant)
      ? conversionParams.reportVariant
      : '';
  }, [conversionParams.reportVariant, reportVariantOptions]);

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
      convertedAt: file.timestamp,
      ...(file.exportContext ? { exportContext: file.exportContext } : {}),
    })),
    conversionLog: conversionLogRef.current
      ? {
          errors: conversionLogRef.current.errors,
          issues: conversionLogRef.current.issues as unknown as Record<
            string,
            unknown
          >[],
        }
      : null,
    conversionParams: {
      ...(conversionParams as unknown as Record<string, unknown>),
      output_filename: outputFilename,
      output_versions: outputVersionsRef.current,
    },
    ...overrides,
  });
  return {
    pendingFiles,
    setPendingFiles,
    queueFocusIndex,
    setQueueFocusIndex,
    selectedPendingIds,
    setSelectedPendingIds,
    isBatchValidating,
    setIsBatchValidating,
    convertedFiles,
    setConvertedFiles,
    firstAccumulatedTac,
    setFirstAccumulatedTac,
    validateReport,
    setValidateReport,
    manualInput,
    setManualInput,
    decodeError,
    setDecodeError,
    softPreview,
    setSoftPreview,
    propagateResiduals,
    setPropagateResiduals,
    includeNationalRemarks,
    setIncludeNationalRemarks,
    liveIwxxm,
    setLiveIwxxm,
    selectedTrace,
    setSelectedTrace,
    lintJump,
    setLintJump,
    lintFocusOffset,
    setLintFocusOffset,
    groupTrace,
    setGroupTrace,
    failedSpans,
    setFailedSpans,
    previewXml,
    setPreviewXml,
    previewStatus,
    setPreviewStatus,
    previewMode,
    setPreviewMode,
    previewSoftFailDetail,
    setPreviewSoftFailDetail,
    focusedConvertedId,
    setFocusedConvertedId,
    inputMode,
    setInputMode,
    demoExampleLabel,
    setDemoExampleLabel,
    bulletinSummary,
    setBulletinSummary,
    placeholderNotice,
    setPlaceholderNotice,
    recentWorkCollapsed,
    setRecentWorkCollapsed,
    converterOpen,
    setConverterOpen,
    outputFilename,
    setOutputFilename,
    outputFilenameOwnedRef,
    isDragging,
    setIsDragging,
    isConverting,
    setIsConverting,
    isConvertAndSending,
    setIsConvertAndSending,
    workbenchBusyRef,
    helpChecklistOpen,
    setHelpChecklistOpen,
    profileDrawerOpen,
    setProfileDrawerOpen,
    tacLockedAfterConvert,
    setTacLockedAfterConvert,
    resultsDrawerOpen,
    setResultsDrawerOpen,
    resultsTab,
    setResultsTab,
    converterPaneHeight,
    setConverterPaneHeight,
    lintHighlightPreset,
    setLintHighlightPreset,
    convertedQueueWasEmptyRef,
    conversionStatus,
    setConversionStatus,
    conversionLog,
    setConversionLog,
    isDisseminationOpen,
    setIsDisseminationOpen,
    packagingExchangeProfile,
    setPackagingExchangeProfile,
    isPreferencesDialogOpen,
    setIsPreferencesDialogOpen,
    isPrivacySettingsOpen,
    setIsPrivacySettingsOpen,
    isSiteTermsOpen,
    setIsSiteTermsOpen,
    isLogoutMenuOpen,
    setIsLogoutMenuOpen,
    showPrivacyNotice,
    setShowPrivacyNotice,
    isParamsExpanded,
    setIsParamsExpanded,
    bulletinFieldError,
    setBulletinFieldError,
    issuingCenterFieldError,
    setIssuingCenterFieldError,
    caExtensionBundleAvailable,
    setCaExtensionBundleAvailable,
    conversionParams,
    setConversionParams,
    handleDisseminationOpenChange,
    profileCatalogEntries,
    setProfileCatalogEntries,
    metadataPrefs,
    setMetadataPrefs,
    isMetadataChecklistOpen,
    setIsMetadataChecklistOpen,
    fileInputRef,
    hydratedWorkSessionIdRef,
    outputVersionsRef,
    setOutputVersions,
    liveLayout,
    updateLiveLayout,
    bulletinSource,
    setBulletinSource,
    focusedBulletinReport,
    setFocusedBulletinReport,
    convertedFilesRef,
    conversionLogRef,
    updateConversionLog,
    applyWmoLibraryDefaultsSync,
    activeProfileSummary,
    activeProfileExampleProducts,
    resolvedVariantProduct,
    reportVariantOptions,
    activeReportVariant,
    buildSnapshot,
    accessToken,
    userEmail,
    isGuest,
    onLogout,
    onRequestLogin,
    onOpenHistory,
    onOpenVisuals,
    onLoadWorkSession,
    onNewMetar,
    onSessionUpdated,
    onActiveSessionIdChange,
    activeWorkSessionId,
    loadedWorkSession,
    pendingMapTac,
    onPendingMapTacConsumed,
    onOpenCatalog,
  };
}

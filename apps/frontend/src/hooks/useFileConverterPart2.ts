/* eslint-disable @typescript-eslint/ban-ts-comment, @typescript-eslint/no-explicit-any, complexity */
// @ts-nocheck — mechanical line-count split
/** Part 2 of useFileConverter. */
import * as D from './fileConverterDeps';

/**
 * useFileConverterPart2.
 */
export function useFileConverterPart2(ctx: any) {
  const {
    pendingFiles,
    setPendingFiles,
    convertedFiles,
    setConvertedFiles,
    setFirstAccumulatedTac,
    manualInput,
    setManualInput,
    setSelectedTrace,
    setLintJump,
    setLintFocusOffset,
    setPreviewXml,
    setPreviewStatus,
    setPreviewMode,
    setPreviewSoftFailDetail,
    setFocusedConvertedId,
    setInputMode,
    setConverterOpen,
    outputFilename,
    setOutputFilename,
    outputFilenameOwnedRef,
    setResultsDrawerOpen,
    conversionLog,
    setIsLogoutMenuOpen,
    setCaExtensionBundleAvailable,
    setConversionParams,
    hydratedWorkSessionIdRef,
    outputVersionsRef,
    setOutputVersions,
    updateConversionLog,
    buildSnapshot,
    accessToken,
    isGuest,
    onLogout,
    onSessionUpdated,
    onActiveSessionIdChange,
    activeWorkSessionId,
    loadedWorkSession,
    pendingMapTac,
    onPendingMapTacConsumed,
  } = ctx;
  const { isReadOnly, saveIndicator, scheduleAutoSave, persistSession } =
    D.useWorkSessionSync({
      accessToken,
      sessionId: activeWorkSessionId ?? null,
      sessionStatus: loadedWorkSession?.status ?? null,
      onSessionSaved: (session) => onSessionUpdated?.(session),
      onSessionIdAssigned: (id) => onActiveSessionIdChange?.(id),
    });

  const handleLogoutWithScope = async (scope: 'global' | 'local' | 'others') => {
    const success = await D.signOutWithScope(scope);
    if (success) {
      setIsLogoutMenuOpen(false);
      setTimeout(() => {
        onLogout?.();
      }, 500);
    }
  };

  const hasLocalUnsavedWork =
    pendingFiles.length > 0 ||
    Boolean(manualInput.trim()) ||
    convertedFiles.length > 0 ||
    Boolean(activeWorkSessionId);

  const showGuestLossNotice = D.shouldShowGuestLossOfProgressNotice({
    isLoggedIn: !isGuest,
    hasLocalUnsavedWork,
  });

  // Load user preferences on mount from localStorage (WMO sync wins for libraries)
  D.useEffect(() => {
    const loadPreferences = () => {
      try {
        const stored = localStorage.getItem('metar_converter_preferences');
        if (stored) {
          setConversionParams(
            D.conversionParamsFromStoredPreferences(
              JSON.parse(stored) as Record<string, unknown>,
            ),
          );
        }
      } catch (error) {
        console.error('Error loading preferences:', error);
      }
    };

    loadPreferences();
  }, []);

  D.useEffect(() => {
    let cancelled = false;
    void D.fetchSchemaStatus()
      .then((status) => {
        if (cancelled) {
          return;
        }
        setCaExtensionBundleAvailable(D.caExtensionBundleAvailableFromStatus(status));
      })
      .catch(() => {
        if (cancelled) {
          return;
        }
        setCaExtensionBundleAvailable(null);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  D.useLayoutEffect(() => {
    if (!loadedWorkSession) {
      hydratedWorkSessionIdRef.current = null;
      if (outputVersionsRef.current.length > 0) {
        outputVersionsRef.current = [];
        setOutputVersions([]);
      }
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
        D.hydratedResultName(result.name as string | undefined, index),
      );
      const hydratedFiles = loadedWorkSession.converted_results.map((result, index) => {
        const originalName = resultNames[index] as string;
        const originalContent = String(result.tac_input ?? '');
        const lineMeta = D.resolveManualLineMetaFromResult(
          originalName,
          result,
          resultNames,
        );
        return {
          id: `loaded-result-${index}`,
          originalName,
          originalContent,
          displayTitle: D.deriveTacDisplayTitle(originalContent, originalName),
          manualLineIndex: lineMeta.manualLineIndex,
          manualLineTotal: lineMeta.manualLineTotal,
          convertedContent: String(
            result.iwxxm_xml ?? result.xml ?? result.content ?? '',
          ),
          timestamp:
            typeof result.converted_at === 'number' ? result.converted_at : Date.now(),
          ...(result.export_context &&
          typeof result.export_context === 'object' &&
          !Array.isArray(result.export_context)
            ? {
                exportContext: result.export_context as ConversionExportContext,
              }
            : {}),
        };
      });
      setConvertedFiles(hydratedFiles);
      const latestHydrated = hydratedFiles[hydratedFiles.length - 1]!;
      setFocusedConvertedId(latestHydrated.id);
      const hydratedXml = D.coalescePreviewXml(latestHydrated.convertedContent);
      if (hydratedXml) {
        setPreviewXml(hydratedXml);
        setPreviewMode('live');
        setPreviewStatus('passed');
        setPreviewSoftFailDetail(undefined);
      }
      const firstTac = String(loadedWorkSession.converted_results[0]?.tac_input ?? '');
      setFirstAccumulatedTac(firstTac || null);
    } else {
      setConvertedFiles([]);
      setFocusedConvertedId(null);
      setFirstAccumulatedTac(null);
    }
    const hasLog =
      (loadedWorkSession.errors?.length ?? 0) > 0 ||
      (loadedWorkSession.issues?.length ?? 0) > 0;
    updateConversionLog(
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
    const restoredName = typeof savedName === 'string' ? savedName : '';
    outputFilenameOwnedRef.current = restoredName.trim() !== '';
    setOutputFilename(restoredName);
    if (params) {
      setConversionParams((prev) => {
        const next = { ...prev };
        const rawProduct = params.product;
        if (typeof rawProduct === 'string' && D.isConvertProductSelection(rawProduct)) {
          next.product = rawProduct;
        }
        if (typeof params.profile === 'string') {
          next.profile = D.hydrateSemanticProfile(params.profile);
        }
        if (typeof params.report_variant === 'string') {
          next.reportVariant = params.report_variant;
        } else if (typeof params.reportVariant === 'string') {
          next.reportVariant = params.reportVariant;
        }
        if (typeof params.preset_id === 'string') {
          next.presetId = params.preset_id;
        } else if (typeof params.presetId === 'string') {
          next.presetId = params.presetId;
        }
        if (typeof params.dissemination_template_id === 'string') {
          next.disseminationTemplateId = params.dissemination_template_id;
        } else if (typeof params.disseminationTemplateId === 'string') {
          next.disseminationTemplateId = params.disseminationTemplateId;
        }
        const rawIwxxmVersion =
          typeof params.iwxxm_version === 'string'
            ? params.iwxxm_version
            : typeof params.iwxxmVersion === 'string'
              ? params.iwxxmVersion
              : next.iwxxmVersion;
        next.iwxxmVersion = D.coerceIwxxmVersionForProfile(
          next.profile,
          rawIwxxmVersion,
        );
        if (typeof params.exchange_profile === 'string') {
          next.exchangeProfile = D.coerceExchangeProfile(params.exchange_profile);
        } else if (typeof params.exchangeProfile === 'string') {
          next.exchangeProfile = D.coerceExchangeProfile(params.exchangeProfile);
        }
        if (typeof params.overlay_id === 'string') {
          next.overlayId = params.overlay_id;
        } else if (typeof params.overlayId === 'string') {
          next.overlayId = params.overlayId;
        }
        Object.assign(next, D.libraryIdsFromSessionParams(params));
        return next;
      });
      const storedVersions = D.readOutputVersions(params);
      outputVersionsRef.current = storedVersions;
      setOutputVersions(storedVersions);
    } else {
      outputVersionsRef.current = [];
      setOutputVersions([]);
    }
  }, [loadedWorkSession, updateConversionLog]);

  D.useLayoutEffect(() => {
    const tac = pendingMapTac?.trim() ?? '';
    if (!tac) {
      return;
    }
    setInputMode('tac');
    setManualInput(tac);
    setSelectedTrace(null);
    setLintJump(null);
    setLintFocusOffset(null);
    setConversionParams((prev) => ({
      ...prev,
      product: D.detectTacProduct(tac),
    }));
    setConverterOpen(true);
    // Keep Map/results open after Send to converter (BUG-2026-11-10).
    setResultsDrawerOpen(true);
    onPendingMapTacConsumed?.();
    document
      .querySelector('[data-testid="live-convert-panes"]')
      ?.scrollIntoView({ behavior: 'auto', block: 'start' });
  }, [pendingMapTac, onPendingMapTacConsumed]);

  D.useEffect(() => {
    if (isReadOnly) {
      return;
    }
    scheduleAutoSave(buildSnapshot());
  }, [manualInput, pendingFiles, convertedFiles, conversionLog, outputFilename]);

  const handlePreferencesSaved = () => {
    // Reload preferences after saving in the dialog
    try {
      const stored = localStorage.getItem('metar_converter_preferences');
      if (stored) {
        setConversionParams(
          D.conversionParamsFromStoredPreferences(
            JSON.parse(stored) as Record<string, unknown>,
          ),
        );
        D.toast.info('Conversion parameters updated from preferences');
      }
    } catch (error) {
      console.error('Error reloading preferences:', error);
    }
  };

  const applyLoadedReportName = (tac: string) => {
    setOutputFilename((current) =>
      D.outputFilenameAfterReportLoad(current, outputFilenameOwnedRef.current, tac),
    );
  };
  return {
    handleLogoutWithScope,
    hasLocalUnsavedWork,
    showGuestLossNotice,
    handlePreferencesSaved,
    applyLoadedReportName,
    isReadOnly,
    saveIndicator,
    scheduleAutoSave,
    persistSession,
  };
}

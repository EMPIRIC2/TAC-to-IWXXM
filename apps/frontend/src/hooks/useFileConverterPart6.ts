/* eslint-disable @typescript-eslint/ban-ts-comment, @typescript-eslint/no-explicit-any, complexity */
// @ts-nocheck — mechanical line-count split
/** Part 6 of useFileConverter. */
import * as D from './fileConverterDeps';

/**
 * useFileConverterPart6.
 */
export function useFileConverterPart6(ctx: any) {
  const {
    saveIndicator,

    isReadOnly,

    pendingFiles,
    setPendingFiles,
    queueFocusIndex,
    setQueueFocusIndex,
    selectedPendingIds,
    setSelectedPendingIds,
    isBatchValidating,
    convertedFiles,
    setConvertedFiles,
    setFirstAccumulatedTac,
    validateReport,
    setValidateReport,
    manualInput,
    setManualInput,
    setDecodeError,
    softPreview,
    propagateResiduals,
    liveIwxxm,
    selectedTrace,
    setSelectedTrace,
    setLintJump,
    setLintFocusOffset,
    setGroupTrace,
    failedSpans,
    setFailedSpans,
    setPreviewXml,
    setPreviewStatus,
    setPreviewMode,
    setPreviewSoftFailDetail,
    focusedConvertedId,
    setFocusedConvertedId,
    inputMode,
    setInputMode,
    setDemoExampleLabel,
    setBulletinSummary,
    setPlaceholderNotice,
    setConverterOpen,
    setOutputFilename,
    outputFilenameOwnedRef,
    isConverting,
    isConvertAndSending,
    tacLockedAfterConvert,
    setTacLockedAfterConvert,
    setResultsDrawerOpen,
    conversionStatus,
    setConversionStatus,
    conversionLog,
    packagingExchangeProfile,
    caExtensionBundleAvailable,
    conversionParams,
    setConversionParams,
    bulletinSource,
    updateConversionLog,
    activeReportVariant,
    accessToken,
    pendingMapTac,
    onPendingMapTacConsumed,
  } = ctx;
  const handleClear = () => {
    setPendingFiles([]);
    setSelectedPendingIds(new Set());
    setQueueFocusIndex(0);
    setManualInput('');
    setDemoExampleLabel(null);
    outputFilenameOwnedRef.current = false;
    setOutputFilename('');
    setConvertedFiles([]);
    setFocusedConvertedId(null);
    setTacLockedAfterConvert(false);
    setFirstAccumulatedTac(null);
    setValidateReport(null);
    updateConversionLog(null);
    setConversionStatus({ type: 'idle' });
    setFailedSpans([]);
    setSelectedTrace(null);
    setPreviewXml('');
    setPreviewStatus('empty');
    setPreviewMode('idle');
    setPreviewSoftFailDetail(undefined);
    setBulletinSummary(null);
    setPlaceholderNotice(null);
    setDecodeError(null);
    D.toast.info('Queue cleared');
  };

  const isBusy = isConverting || isConvertAndSending || isBatchValidating;
  const hasInput = pendingFiles.length > 0 || !!manualInput.trim();
  const hasConverted = convertedFiles.length > 0;
  const latestConverted = convertedFiles[0];
  const focusedConverted =
    convertedFiles.find((file) => file.id === focusedConvertedId) ??
    convertedFiles[convertedFiles.length - 1] ??
    null;
  const focusedAssessment = focusedConverted
    ? D.assessConvertedFile(focusedConverted)
    : null;
  const latestAssessment = latestConverted
    ? D.assessConvertedFile(latestConverted)
    : null;
  const latestReadyToDownload = Boolean(
    latestConverted && latestAssessment && !latestAssessment.publishBlocked,
  );
  const calmUi = D.deriveCalmConvertUi({
    hasInput,
    hasConverted,
    latestReadyToDownload,
  });
  const calmProfileLabel = D.resolveCalmProfileLabel(
    conversionParams.profile,
    D.SEMANTIC_PROFILE_OPTIONS,
  );
  const caProfileBlocked =
    D.isCaEcccProfile(conversionParams.profile) && caExtensionBundleAvailable === false;
  const convertDisabled = isBusy || !hasInput || isReadOnly || caProfileBlocked;
  const calmTacReadOnly = isReadOnly || (tacLockedAfterConvert && hasConverted);
  const safeQueueFocusIndex = D.clampQueueIndex(queueFocusIndex, pendingFiles.length);
  const activeSelectedCount = pendingFiles.filter((f) =>
    selectedPendingIds.has(f.id),
  ).length;

  const liveAssistProduct = D.resolveConvertProduct(
    conversionParams.product,
    manualInput,
  );

  const liveIwxxmRunner = D.useCallback(
    async (signal: AbortSignal) => {
      setDecodeError(null);
      setGroupTrace([]);
      try {
        const response = await D.callBackendConversion({
          manualText: manualInput.trim(),
          product: liveAssistProduct,
          ...D.convertFieldsFromParamsBar(
            D.paramsBarFromState(conversionParams, activeReportVariant),
            { softPreview: true, propagateResidualsToRemarks: propagateResiduals },
          ),
          extensions: D.nationalExtensionsForProfile(conversionParams.profile),
          exchangeOutput: D.exchangeOutputForProfile(conversionParams.profile),
          ...(accessToken?.trim() ? { accessToken: accessToken.trim() } : {}),
          ...D.convertOverlayFields(conversionParams.overlayId, accessToken),
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
        const posted = manualInput.trim();
        setGroupTrace(
          D.readGroupTrace(response).map((row) => ({
            ...row,
            ...D.formFieldSpanInEditor(manualInput, posted, row.start, row.end),
          })),
        );
        if (latestXml) {
          setPreviewXml(latestXml);
          setPreviewMode('live');
        }
        if (response.failed_spans?.length) {
          setFailedSpans(
            response.failed_spans.map((span) => ({
              ...D.formFieldSpanInEditor(manualInput, posted, span.start, span.end),
              code: span.code ?? undefined,
              message: span.message ?? undefined,
            })),
          );
          setPreviewStatus('soft-fail');
          setPreviewSoftFailDetail(
            'Some groups could not be converted. Fix the highlighted spans in the editor, then retry. This preview is not for publishing.',
          );
        } else if (response.ok !== false) {
          setFailedSpans([]);
          setPreviewStatus(latestXml ? 'passed' : 'empty');
          setPreviewSoftFailDetail(undefined);
        }
      } catch (err) {
        if (D.isAbortError(err) || signal.aborted) {
          return;
        }
        setDecodeError(err instanceof Error ? err.message : 'Live IWXXM failed');
      }
    },
    [
      manualInput,
      liveAssistProduct,
      conversionParams,
      activeReportVariant,
      accessToken,
      propagateResiduals,
    ],
  );

  const {
    issueSpans,
    lintIssues,
    lintFixes,
    decodeSegments,
    decodeResiduals,
    decodeProduct,
    decodeSummary,
    loading: decodeLoading,
  } = D.useLiveWorkbenchAssist({
    text: manualInput,
    product: liveAssistProduct,
    enabled: !isReadOnly && inputMode !== 'validate_iwxxm',
    liveIwxxm,
    liveIwxxmRunner,
  });

  D.useEffect(() => {
    D.publishDecodeVisuals({
      station: D.stationFromReport(manualInput),
      segments: decodeSegments.map((segment) => ({
        code: segment.code,
        explanation: segment.explanation,
      })),
    });
  }, [manualInput, decodeSegments]);

  D.useEffect(() => {
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
  }, [pendingMapTac, onPendingMapTacConsumed]);

  const tacLintSummary =
    manualInput.trim().length === 0
      ? 'TAC input: not checked yet'
      : D.lintSummaryLabel(lintIssues);
  const bulletinReports =
    inputMode === 'ahl_bulletin'
      ? D.listBulletinReports(bulletinSource || manualInput)
      : [];
  const previewIncomplete = D.previewIsIncomplete(
    lintIssues.filter((issue) => issue.severity === 'error').length,
    decodeResiduals.length,
    failedSpans.length,
  );
  const editorSpans = D.spansWithSelection(issueSpans, selectedTrace);
  const jumpIssues = D.jumpableLintIssues(lintIssues);
  const applyLintJump = (issue: JumpableLintIssue) => {
    setLintJump(jumpIssues.indexOf(issue));
    setLintFocusOffset(issue.start);
    setSelectedTrace({
      start: issue.start,
      end: issue.end,
      code: manualInput.slice(issue.start, issue.end),
    });
  };
  const lintCounts = D.lintIssueCounts(lintIssues);
  const convertIssueLayers = D.errorLayerNames(conversionLog);
  const strictLayersRan = D.strictConvertRan({
    strict: conversionParams.strictValidation,
    softPreview,
    convertedCount: convertedFiles.length,
    status: conversionStatus.type,
  });
  const consoleSchemaStatus = D.outputLayerStatus(
    'schema',
    validateReport,
    convertIssueLayers,
    strictLayersRan,
  );
  const consoleSchematronStatus = D.outputLayerStatus(
    'schematron',
    validateReport,
    convertIssueLayers,
    strictLayersRan,
  );

  const { byCode: lintCatalogByCode } = D.useLintIssueCatalog({
    product: liveAssistProduct,
    semanticProfile: conversionParams.profile,
    exchangeProfile: packagingExchangeProfile ?? conversionParams.exchangeProfile,
    enabled: !isReadOnly,
  });

  const applyLintFix = D.useCallback(
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
  return {
    handleClear,
    isBusy,
    hasInput,
    hasConverted,
    latestConverted,
    focusedConverted,
    focusedAssessment,
    latestAssessment,
    latestReadyToDownload,
    calmUi,
    calmProfileLabel,
    caProfileBlocked,
    convertDisabled,
    calmTacReadOnly,
    safeQueueFocusIndex,
    activeSelectedCount,
    liveAssistProduct,
    liveIwxxmRunner,
    tacLintSummary,
    bulletinReports,
    previewIncomplete,
    editorSpans,
    jumpIssues,
    applyLintJump,
    lintCounts,
    convertIssueLayers,
    strictLayersRan,
    consoleSchemaStatus,
    consoleSchematronStatus,
    applyLintFix,
    saveIndicatorLabel,
    decodeLoading,
    decodeSegments,
    decodeResiduals,
    decodeProduct,
    decodeSummary,
    lintCatalogByCode,
    lintIssues,
    lintFixes,
    issueSpans,
  };
}

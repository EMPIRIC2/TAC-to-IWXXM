/* eslint-disable @typescript-eslint/ban-ts-comment, @typescript-eslint/no-explicit-any, complexity */
// @ts-nocheck — mechanical line-count split
/** Part 4 of useFileConverter. */
import * as D from './fileConverterDeps';

/**
 * useFileConverterPart4.
 * @example
 * const _ = true;
 */
export function useFileConverterPart4(ctx: any) {
  const {
    isReadOnly,
    persistSession,

    pendingFiles,
    setPendingFiles,
    setConvertedFiles,
    setFirstAccumulatedTac,
    setValidateReport,
    manualInput,
    setManualInput,
    setDecodeError,
    setFailedSpans,
    setPreviewXml,
    setPreviewStatus,
    setPreviewMode,
    setPreviewSoftFailDetail,
    inputMode,
    setInputMode,
    setDemoExampleLabel,
    setBulletinSummary,
    setPlaceholderNotice,
    outputFilename,
    setOutputFilename,
    outputFilenameOwnedRef,
    setIsConverting,
    setIsConvertAndSending,
    setTacLockedAfterConvert,
    setConversionStatus,
    conversionLog,
    setBulletinFieldError,
    setIssuingCenterFieldError,
    conversionParams,
    setConversionParams,
    metadataPrefs,
    setMetadataPrefs,
    updateConversionLog,
    buildSnapshot,
    applyLoadedReportName,
    performConversion,
    accessToken,
    userEmail,
    isGuest,
    onNewMetar,
    onActiveSessionIdChange,
  } = ctx;
  const handleValidateOnly = async () => {
    // Read-only sessions cannot enter validate mode (mode buttons disabled).
    const xmlFromPaste = manualInput.trim();
    const xmlFiles = pendingFiles.filter((f) => f.name.toLowerCase().endsWith('.xml'));
    if (xmlFiles.length > 1) {
      D.toast.error('Validate mode accepts one .xml file at a time.');
      return;
    }
    const xmlContent = xmlFromPaste || xmlFiles[0]?.content?.trim() || '';
    if (!xmlContent) {
      D.toast.error('Paste IWXXM XML or upload one .xml file to validate.');
      return;
    }
    if (D.looksLikeTacNotXml(xmlContent)) {
      D.toast.error(
        'That looks like TAC, not IWXXM XML. Convert first, then validate the XML output.',
      );
      return;
    }
    setIsConverting(true);
    setValidateReport(null);
    setConversionStatus({ type: 'loading', message: 'Validating IWXXM…' });
    try {
      const report = await D.validateIwxxm({
        xmlContent,
        profile: conversionParams.profile,
        iwxxmVersion: conversionParams.iwxxmVersion,
        stopOnError: true,
        extensions: D.nationalExtensionsForProfile(conversionParams.profile),
      });
      setValidateReport(report);
      setConversionStatus({ type: 'idle' });
      if (report.is_valid) {
        D.toast.success('IWXXM validation passed');
      } else {
        D.toast.warning('IWXXM validation reported failures');
      }
    } catch (error) {
      const message = D.iwxxmValidationErrorMessage(error);
      setConversionStatus({ type: 'error', message });
      D.toast.error(message);
    } finally {
      setIsConverting(false);
    }
  };

  const handleConvert = async () => {
    // Close D.Settings so the right-aligned panel cannot intercept Results clicks.
    document
      .querySelector<HTMLDetailsElement>('[data-testid="convert-settings"]')
      ?.removeAttribute('open');

    if (isReadOnly) {
      return;
    }
    if (inputMode === 'validate_iwxxm') {
      await handleValidateOnly();
      return;
    }
    const bulletinOk = D.isValidBulletinId(conversionParams.bulletinId);
    const centerOk = D.isValidIssuingCenter(conversionParams.issuingCenter);
    setBulletinFieldError(bulletinOk ? null : D.BULLETIN_ID_FIELD_ERROR);
    setIssuingCenterFieldError(centerOk ? null : D.ISSUING_CENTER_FIELD_ERROR);
    if (!bulletinOk || !centerOk) {
      return;
    }
    setIsConverting(true);
    try {
      const result = await performConversion();
      if (result) {
        if (result.softFail) {
          D.toast.warning(
            'Soft preview found groups that failed. This result is not ready to publish.',
          );
        } else if (result.files.length > 0) {
          D.toast.success(`Successfully converted ${result.files.length} file(s)`);
          setTacLockedAfterConvert(true);
        }
        // A mode that produced no files already explained itself. Do not mark
        // the current draft failed or announce a zero-file success.
        if (result.files.length > 0 || !result.hasErrors) {
          const snapshot = buildSnapshot({
            convertedFiles: result.files.map((file) => ({
              originalName: file.originalName,
              originalContent: file.originalContent,
              convertedContent: file.convertedContent,
            })),
            manualInput,
            pendingFiles: [],
          });
          await persistSession(snapshot, {
            status: result.hasErrors ? 'failed' : 'wip',
          });
        }
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
          D.toast.warning(
            'Soft preview found failed groups. Fix them before Convert & Send.',
          );
        }
        await persistSession(
          buildSnapshot({
            convertedFiles: result.files.map((file) => ({
              originalName: file.originalName,
              originalContent: file.originalContent,
              convertedContent: file.convertedContent,
            })),
            manualInput,
            pendingFiles: [],
          }),
          { status: 'failed' },
        );
        return;
      }

      D.toast.success(`Successfully converted ${result.files.length} file(s)`);
      setConversionStatus({ type: 'loading', message: 'Sending to database...' });

      const wipSnapshot = buildSnapshot({
        convertedFiles: result.files.map((file) => ({
          originalName: file.originalName,
          originalContent: file.originalContent,
          convertedContent: file.convertedContent,
        })),
        manualInput,
        pendingFiles: [],
      });

      try {
        const data = await D.uploadConvertedFiles({
          files: result.files,
          options: D.CONVERT_AND_SEND_UPLOAD_OPTIONS,
        });
        setConversionStatus({ type: 'idle' });
        D.toast.success(data.message || 'Files converted and sent successfully');
        await persistSession(wipSnapshot, { status: 'finished' });
      } catch (error) {
        console.error('[FileConverter] Convert&Send upload error:', error);
        const uploadMessage =
          error instanceof Error ? error.message : 'Failed to upload to database';
        setConversionStatus({
          type: 'send_error',
          message: `Send failed: ${uploadMessage}`,
        });
        D.toast.error(`Conversion succeeded but send failed: ${uploadMessage}`);
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
    outputFilenameOwnedRef.current = false;
    setOutputFilename('');
    setConvertedFiles([]);
    setTacLockedAfterConvert(false);
    setFirstAccumulatedTac(null);
    setValidateReport(null);
    updateConversionLog(null);
    setConversionStatus({ type: 'idle' });
    setInputMode('tac');
    setConversionParams((prev) => ({ ...prev, product: 'auto' }));
    setFailedSpans([]);
    setPreviewXml('');
    setPreviewStatus('empty');
    setPreviewMode('idle');
    setPreviewSoftFailDetail(undefined);
    onActiveSessionIdChange?.(null);
    onNewMetar?.();
    D.toast.info(
      isReadOnly ? 'Starting a new TAC session' : 'Starting a new TAC draft',
    );
  };

  const handleLoadGoldenExample = D.useCallback(
    (exampleId: string) => {
      const example = D.getExampleById(exampleId);
      if (!example) {
        return;
      }
      // Drop prior conversion/preview state so demo TAC is never paired with stale XML.
      setPendingFiles([]);
      setConvertedFiles([]);
      setTacLockedAfterConvert(false);
      setFirstAccumulatedTac(null);
      setValidateReport(null);
      updateConversionLog(null);
      setConversionStatus({ type: 'idle' });
      setFailedSpans([]);
      setPreviewXml('');
      setPreviewStatus('empty');
      setPreviewMode('idle');
      setPreviewSoftFailDetail(undefined);
      setBulletinSummary(null);
      setPlaceholderNotice(null);
      setDecodeError(null);

      const exampleTac = example.body.replace(/\s+$/, '');
      setManualInput(exampleTac);
      applyLoadedReportName(exampleTac);
      setInputMode(example.inputMode);
      // Demo bodies are WMO / Annex 3 goldens, so load them under the Annex 3 line.
      // Resetting the profile stops a sticky national overlay (e.g. US_FAA_NWS) from
      // flagging valid Annex 3 constructs like BECMG on the official samples.
      const { profile: demoProfile, libraryIds: demoLibraryIds } =
        D.libraryResetForProfile(D.DEFAULT_SEMANTIC_PROFILE);
      // Always set product — omit → auto — so a prior TAF pick cannot stick on AHL/TAC demos.
      setConversionParams((prev) => ({
        ...prev,
        ...demoLibraryIds,
        profile: demoProfile,
        product: example.product ?? 'auto',
        reportVariant: '',
        iwxxmVersion: D.coerceIwxxmVersionForProfile(demoProfile, prev.iwxxmVersion),
      }));
      setDemoExampleLabel(example.label);
      D.toast.info(`Loaded ${example.label} example`);
    },
    [updateConversionLog],
  );

  const resolveDownloadXmlName = (file: D.ConvertedFile): string => {
    /* v8 ignore next 8 -- live vs original download name paths */
    if (file.liveOutputSlot) {
      return D.manualDownloadXmlName(
        outputFilename,
        file.liveOutputSlot.index,
        file.liveOutputSlot.total,
      );
    }
    return D.toIwxxmDownloadName(file.originalName ?? '');
  };

  const includeConversionMetadata = D.isConversionMetadataExportEnabled(metadataPrefs);

  const persistMetadataPrefs = D.useCallback((next: ConversionMetadataPrefs) => {
    setMetadataPrefs(next);
    D.writeConversionMetadataPrefs(next);
  }, []);

  const updateMetadataChecklist = D.useCallback(
    (key: ConversionMetadataChecklistKey, checked: boolean) => {
      persistMetadataPrefs({
        ...metadataPrefs,
        checklist: {
          ...metadataPrefs.checklist,
          [key]: checked,
        },
      });
    },
    [metadataPrefs, persistMetadataPrefs],
  );

  const buildFileExportMetadata = D.useCallback(
    (file: D.ConvertedFile) => {
      const ctx = file.exportContext;
      return D.buildConversionExportMetadata({
        tacContent: file.originalContent ?? '',
        convertedAt: file.timestamp,
        product: ctx?.product ?? conversionParams.product,
        iwxxmVersion: ctx?.iwxxmVersion ?? conversionParams.iwxxmVersion,
        reportVariant: ctx?.reportVariant ?? conversionParams.reportVariant,
        libraries: ctx
          ? {
              conversionLibraryId: ctx.conversionLibraryId,
              tacValidationLibraryId: ctx.tacValidationLibraryId,
              iwxxmValidationLibraryId: ctx.iwxxmValidationLibraryId,
              disseminationLibraryId: ctx.disseminationLibraryId,
              decodingLibraryId: ctx.decodingLibraryId,
            }
          : {
              conversionLibraryId: conversionParams.conversionLibraryId,
              tacValidationLibraryId: conversionParams.tacValidationLibraryId,
              iwxxmValidationLibraryId: conversionParams.iwxxmValidationLibraryId,
              disseminationLibraryId: conversionParams.disseminationLibraryId,
              decodingLibraryId: conversionParams.decodingLibraryId,
            },
        checklist: metadataPrefs.checklist,
        isGuest,
        userEmail,
        accessToken,
        conversionLog,
        lintSessionBatch: conversionLog != null,
      });
    },
    [
      accessToken,
      conversionLog,
      conversionParams,
      isGuest,
      metadataPrefs.checklist,
      userEmail,
    ],
  );
  return {
    handleValidateOnly,
    handleConvert,
    handleConvertAndSend,
    handleNewMetar,
    handleLoadGoldenExample,
    resolveDownloadXmlName,
    includeConversionMetadata,
    persistMetadataPrefs,
    updateMetadataChecklist,
    buildFileExportMetadata,
  };
}

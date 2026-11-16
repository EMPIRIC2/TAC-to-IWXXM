/* eslint-disable @typescript-eslint/ban-ts-comment, @typescript-eslint/no-explicit-any, complexity */
// @ts-nocheck — mechanical line-count split
/** useFileConverterPart3b — performConversion (restored from stage). */
import * as D from './fileConverterDeps';

/**
 * useFileConverterPart3b.
 * @example
 * const _ = true;
 */
export function useFileConverterPart3b(ctx: any) {
  const {
    pendingFiles,
    setPendingFiles,
    setSelectedPendingIds,
    setConvertedFiles,
    setFirstAccumulatedTac,
    manualInput,
    softPreview,
    propagateResiduals,
    setFailedSpans,
    setPreviewXml,
    setPreviewStatus,
    setPreviewMode,
    setPreviewSoftFailDetail,
    setFocusedConvertedId,
    inputMode,
    setInputMode,
    setBulletinSummary,
    setPlaceholderNotice,
    setConversionStatus,
    conversionParams,
    outputVersionsRef,
    setOutputVersions,
    bulletinSource,
    focusedBulletinReport,
    convertedFilesRef,
    updateConversionLog,
    accessToken,
    outputFilename,
    activeReportVariant,
  } = ctx;
  const performConversion = async (opts?: {
    pendingSubset?: D.PendingFile[];
    includeManual?: boolean;
  }): Promise<{
    files: D.ConvertedFile[];
    hasErrors: boolean;
    softFail: boolean;
  } | null> => {
    const queueFiles = opts?.pendingSubset ?? pendingFiles;
    const includeManual = opts?.includeManual !== false;
    const manualText = includeManual
      ? inputMode === 'ahl_bulletin' && focusedBulletinReport !== null
        ? bulletinSource.trim()
        : manualInput.trim()
      : '';
    const rememberHardConvert = (files: D.ConvertedFile[]) => {
      if (softPreview) {
        return;
      }
      const next = D.appendOutputVersion(outputVersionsRef.current, {
        at: Date.now(),
        tac: manualText || files[0]?.originalContent || '',
        xml: files.map((file) => file.convertedContent).join('\n'),
        conversionProfile:
          conversionParams.conversionLibraryId || conversionParams.profile,
        decodingProfile: conversionParams.decodingLibraryId,
      });
      outputVersionsRef.current = next;
      setOutputVersions(next);
    };

    if (queueFiles.length === 0 && !manualText) {
      D.toast.error('Please add files or enter manual input');
      return null;
    }

    const clearConvertedFromQueue = () => {
      if (opts?.pendingSubset) {
        const done = new Set(opts.pendingSubset.map((f) => f.id));
        setPendingFiles((prev) => prev.filter((f) => !done.has(f.id)));
        setSelectedPendingIds((prev) => {
          const next = new Set(prev);
          for (const id of done) next.delete(id);
          return next;
        });
      } else {
        setPendingFiles([]);
        setSelectedPendingIds(new Set());
      }
    };

    setConversionStatus({ type: 'loading', message: 'Converting...' });
    updateConversionLog(null);
    setFailedSpans([]);
    setBulletinSummary(null);
    setPlaceholderNotice(null);

    try {
      const tacForDetect = [manualText, ...queueFiles.map((f) => f.content)]
        .filter(Boolean)
        .join('\n');

      // Auto-switch when paste looks like bulletin / COLLECT (UJ-025)
      let mode = inputMode;
      if (mode === 'tac' && D.looksLikeAhlBulletin(tacForDetect)) {
        mode = 'ahl_bulletin';
        setInputMode('ahl_bulletin');
        D.toast.info('Detected an AHL bulletin. Switched input mode.');
      } else if (mode === 'tac' && D.looksLikeCollectIwxxm(tacForDetect)) {
        mode = 'collect_iwxxm';
        setInputMode('collect_iwxxm');
        D.toast.info('Detected an IWXXM COLLECT file. Switched input mode.');
      }

      const resolvedProduct = D.resolveConvertProduct(
        conversionParams.product,
        tacForDetect,
      );
      if (
        conversionParams.product !== 'auto' &&
        conversionParams.product !== 'IWXXM' &&
        tacForDetect.trim()
      ) {
        const detected = D.detectTacProduct(tacForDetect);
        if (detected !== resolvedProduct) {
          D.toast.warning(
            `Selected product ${resolvedProduct} differs from detected ${detected}; converting as ${resolvedProduct}.`,
          );
        }
      }

      const filesToConvert: File[] = queueFiles.map((file) => {
        return new File([file.content], file.name, { type: 'text/plain' });
      });

      if (mode === 'collect_iwxxm') {
        try {
          await D.ingestCollect({
            manualText: manualText || undefined,
            files: filesToConvert.length > 0 ? filesToConvert : undefined,
            profile: conversionParams.profile,
            iwxxmVersion: conversionParams.iwxxmVersion,
          });
          D.toast.success('COLLECT ingest succeeded');
          setConversionStatus({ type: 'idle' });
          return { files: [], hasErrors: false, softFail: false };
        } catch (err) {
          if (err instanceof D.EndpointNotImplementedError) {
            setPlaceholderNotice(err.message);
            updateConversionLog({
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
            D.toast.warning('COLLECT ingest placeholder (not implemented yet)');
            setConversionStatus({ type: 'idle' });
            return { files: [], hasErrors: true, softFail: false };
          }
          throw err;
        }
      }

      if (mode === 'ahl_bulletin') {
        const bulletinResponse = await D.convertBulletin({
          manualText: manualText || undefined,
          files: filesToConvert.length > 0 ? filesToConvert : undefined,
          product: resolvedProduct,
          conversionLibraryId: D.optionalFormField(
            conversionParams.conversionLibraryId,
          ),
          disseminationLibraryId: D.optionalFormField(
            conversionParams.disseminationLibraryId,
          ),
          profile: conversionParams.profile,
          exchangeProfile: conversionParams.exchangeProfile,
          iwxxmVersion: conversionParams.iwxxmVersion,
          lint: true,
          propagateResidualsToRemarks: propagateResiduals,
          extensions: D.nationalExtensionsForProfile(conversionParams.profile),
          ...(accessToken?.trim() ? { accessToken: accessToken.trim() } : {}),
        });
        const meta = bulletinResponse.bulletin_meta;
        setBulletinSummary(
          `${meta.ahl} · ${meta.report_count} report(s) · ${meta.cccc} ${meta.yygggg}`,
        );
        const newConvertedFiles: D.ConvertedFile[] = [];
        const issueBag: D.ConversionLog['issues'] = [];
        bulletinResponse.results.forEach((result) => {
          result.issues.forEach((issue) => {
            issueBag.push({
              source: `bulletin[${result.report_index}]`,
              message: issue.message,
              code: issue.code,
              severity:
                (issue.severity as D.ConversionLog['issues'][0]['severity']) ||
                'warning',
              start: issue.start,
              end: issue.end,
            });
          });
          if (result.ok && result.xml) {
            const originalContent = result.tac_input;
            newConvertedFiles.push({
              id: `bulletin-${Date.now()}-${result.report_index}`,
              originalName: `bulletin_report_${result.report_index + 1}.tac`,
              originalContent,
              displayTitle: D.deriveTacDisplayTitle(
                originalContent,
                `report ${result.report_index + 1}`,
              ),
              convertedContent: result.xml,
              timestamp: Date.now(),
              exportContext: D.snapshotExportContext(conversionParams, resolvedProduct),
              resultCard: {
                errors: [],
                issues: result.issues,
                ok: result.ok,
              },
            });
          }
        });
        const failed = bulletinResponse.results.filter((r) => !r.ok).length;
        if (newConvertedFiles.length > 0) {
          const { files, overCap } = D.appendConvertedWithinCap(
            convertedFilesRef.current,
            newConvertedFiles,
          );
          if (overCap) {
            D.toast.error(
              `Cannot keep more than ${D.ACCUMULATE_RESULT_CAP} conversions. Clear the batch, then convert again.`,
            );
          } else {
            setConvertedFiles(files);
            convertedFilesRef.current = files;
            setFirstAccumulatedTac((stem) =>
              D.nextFirstAccumulatedTac(stem, newConvertedFiles[0]?.originalContent),
            );
            rememberHardConvert(newConvertedFiles);
          }
          const latestBulletin = newConvertedFiles[newConvertedFiles.length - 1]!;
          setFocusedConvertedId(latestBulletin.id);
          setPreviewXml(latestBulletin.convertedContent);
          setPreviewMode('live');
          setPreviewStatus('passed');
          setPreviewSoftFailDetail(undefined);
        }
        clearConvertedFromQueue();
        // EV-040: keep manual TAC input after convert (do not clear).
        updateConversionLog(
          issueBag.length > 0 ? { errors: [], issues: issueBag } : null,
        );
        setConversionStatus({ type: 'idle' });
        if (failed > 0) {
          D.toast.warning(`Bulletin: ${newConvertedFiles.length} ok, ${failed} failed`);
        } else {
          D.toast.success(`Bulletin: ${newConvertedFiles.length} report(s) converted`);
        }
        return {
          files: newConvertedFiles,
          hasErrors: failed > 0,
          softFail: false,
        };
      }

      const newConvertedFiles: D.ConvertedFile[] = [];

      console.log('[FileConverter] Starting conversion with:', {
        manualInput: manualText ? 'provided' : 'none',
        fileCount: filesToConvert.length,
        softPreview,
      });

      const barFields = D.convertFieldsFromParamsBar(
        D.paramsBarFromState(conversionParams, activeReportVariant),
        { softPreview, propagateResidualsToRemarks: propagateResiduals },
      );

      const response = await D.callBackendConversion({
        manualText: manualText || undefined,
        files: filesToConvert.length > 0 ? filesToConvert : undefined,
        product: resolvedProduct,
        ...barFields,
        extensions: D.nationalExtensionsForProfile(conversionParams.profile),
        exchangeOutput: D.exchangeOutputForProfile(conversionParams.profile),
        ...(accessToken?.trim() ? { accessToken: accessToken.trim() } : {}),
        ...D.convertOverlayFields(conversionParams.overlayId, accessToken),
      });

      console.log('[FileConverter] Conversion response:', response);

      if (response.results && Array.isArray(response.results)) {
        // Match backend split_manual_entries (SIGMET/AIRMET/VAA/TCA stay one doc).
        const manualLines = D.splitManualEntries(manualText, resolvedProduct);
        const manualResultCount = manualLines.length;

        response.results.forEach((result, index) => {
          const isManualResult = index < manualResultCount;
          const fileIndex = index - manualResultCount;
          const pendingFile = queueFiles[fileIndex];
          const originalName = isManualResult
            ? D.manualOutputName(outputFilename, index, manualResultCount)
            : D.queueResultOriginalName(pendingFile?.name, result.name);
          const originalContent = D.resolveOriginalTac(
            result.tac_input ?? undefined,
            manualLines[index],
            pendingFile?.content,
          );

          newConvertedFiles.push({
            id: `converted-${Date.now()}-${index}`,
            originalName,
            originalContent,
            displayTitle: D.deriveTacDisplayTitle(originalContent, originalName),
            manualLineIndex:
              isManualResult && manualResultCount > 1 ? index + 1 : undefined,
            manualLineTotal:
              isManualResult && manualResultCount > 1 ? manualResultCount : undefined,
            liveOutputSlot: isManualResult
              ? { index, total: manualResultCount }
              : undefined,
            convertedContent: result.iwxxm_xml || result.xml || result.content || '',
            timestamp: Date.now(),
            exportContext: D.snapshotExportContext(
              conversionParams,
              resolvedProduct,
              D.optionalFormField(activeReportVariant),
            ),
          });
        });
      }

      const responseErrors = response.errors ?? [];
      const responseIssues = response.issues ?? [];
      const hasLog = responseErrors.length > 0 || responseIssues.length > 0;
      const softFail = Boolean(softPreview && response.ok === false);
      const spans = (response.failed_spans ?? []).map((span) => ({
        start: span.start,
        end: span.end,
        code: span.code ?? undefined,
        message: span.message ?? undefined,
      }));

      if (softFail) {
        setFailedSpans(spans);
      }

      const resultOk = response.ok !== false;
      for (const file of newConvertedFiles) {
        file.resultCard = {
          errors: responseErrors,
          issues: responseIssues,
          ok: resultOk,
        };
      }

      if (newConvertedFiles.length === 0) {
        if (hasLog) {
          updateConversionLog({ errors: responseErrors, issues: responseIssues });
        }
        const failureMessage = responseErrors[0] ?? 'No files were converted';
        D.toast.error(failureMessage);
        setConversionStatus({ type: 'error', message: failureMessage });
        return null;
      }

      const latestFile = newConvertedFiles[newConvertedFiles.length - 1]!;
      const latestPreviewXml = D.coalescePreviewXml(latestFile.convertedContent);
      if (latestPreviewXml) {
        setPreviewXml(latestPreviewXml);
        setFocusedConvertedId(latestFile.id);
        if (softPreview || softFail) {
          setPreviewMode('soft-preview');
          if (softFail) {
            setPreviewStatus('soft-fail');
            setPreviewSoftFailDetail(
              'Some groups could not be converted. Fix the highlighted spans in the editor, then retry the preview. This output is not for publishing.',
            );
          } else {
            setPreviewStatus('passed');
            setPreviewSoftFailDetail(undefined);
          }
        } else {
          setPreviewMode('live');
          setPreviewStatus(resultOk ? 'passed' : 'soft-fail');
          setPreviewSoftFailDetail(undefined);
        }
      }

      {
        const { files, overCap } = D.appendConvertedWithinCap(
          convertedFilesRef.current,
          newConvertedFiles,
        );
        if (overCap) {
          D.toast.error(
            `Cannot keep more than ${D.ACCUMULATE_RESULT_CAP} conversions. Clear the batch, then convert again.`,
          );
        } else {
          setConvertedFiles(files);
          convertedFilesRef.current = files;
          setFirstAccumulatedTac((stem) =>
            D.nextFirstAccumulatedTac(stem, newConvertedFiles[0]?.originalContent),
          );
          rememberHardConvert(newConvertedFiles);
        }
      }
      clearConvertedFromQueue();
      // EV-040: keep manual TAC input after convert. Clear failed spans only on hard success.
      if (!softFail) {
        setFailedSpans([]);
      }
      updateConversionLog(
        hasLog ? { errors: responseErrors, issues: responseIssues } : null,
      );
      setConversionStatus({ type: 'idle' });
      // Info notes stay in the log. They do not fail a conversion that produced files.
      return {
        files: newConvertedFiles,
        hasErrors: responseErrors.length > 0 || softFail,
        softFail,
      };
    } catch (error) {
      console.error('[FileConverter] Conversion error:', error);

      if (
        D.isStructuredConvertError(error) &&
        (error.errors.length > 0 || error.issues.length > 0)
      ) {
        updateConversionLog({
          errors: D.mergeVisibleConvertErrors(error.message, error.errors),
          issues: error.issues,
        });
      }

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
        D.toast.error(timeoutMsg);
      } else if (isAuthError) {
        const authMsg = 'Authentication failed. Please ensure you are logged in.';
        setConversionStatus({ type: 'error', message: authMsg });
        D.toast.error(authMsg);
      } else {
        setConversionStatus({ type: 'error', message: errorMessage });
        D.toast.error(errorMessage);
      }
      return null;
    }
  };

  return {
    performConversion,
  };
}

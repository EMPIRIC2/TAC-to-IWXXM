/* eslint-disable @typescript-eslint/ban-ts-comment, @typescript-eslint/no-explicit-any */
// @ts-nocheck — mechanical line-count split
/** Part 5 of useFileConverter. */
import * as D from './fileConverterDeps';

/**
 * useFileConverterPart5.
 * @example
 * const _ = true;
 */
export function useFileConverterPart5(ctx: any) {
  const {
    isReadOnly,
    workbenchBusyRef,
    pendingFiles,
    setPendingFiles,
    queueFocusIndex,
    setQueueFocusIndex,
    selectedPendingIds,
    setSelectedPendingIds,
    setIsBatchValidating,
    convertedFiles,
    setConvertedFiles,
    firstAccumulatedTac,
    setManualInput,
    setPreviewXml,
    setPreviewStatus,
    setPreviewMode,
    setPreviewSoftFailDetail,
    focusedConvertedId,
    setFocusedConvertedId,
    outputFilename,
    setIsConverting,
    setResultsDrawerOpen,
    setResultsTab,
    conversionParams,
    applyLoadedReportName,
    performConversion,
    resolveDownloadXmlName,
    includeConversionMetadata,
    buildFileExportMetadata,
  } = ctx;
  const handleDownloadSingle = async (file: D.ConvertedFile) => {
    const xmlName = resolveDownloadXmlName(file);
    if (!includeConversionMetadata) {
      D.downloadBlob(new Blob([file.convertedContent], { type: 'text/xml' }), xmlName);
      D.toast.success('File downloaded');
      return;
    }

    const zip = new D.JSZip();
    zip.file(xmlName, file.convertedContent);
    zip.file(
      D.metaSidecarFileName(xmlName),
      D.serializeConversionMetadata(buildFileExportMetadata(file)),
    );
    const content = await zip.generateAsync({ type: 'blob' });
    const zipStem = xmlName.replace(/\.xml$/i, '') || 'download';
    D.downloadBlob(content, `${zipStem}.zip`);
    D.toast.success('File downloaded with metadata');
  };

  const handleDownloadAll = async () => {
    if (convertedFiles.length === 0) return;

    const zip = new D.JSZip();
    const pairs = D.alignConversionZipPairs(
      convertedFiles.map((file) => ({
        xmlName: resolveDownloadXmlName(file),
        tacName: D.toTacSourceName(
          file.liveOutputSlot
            ? D.manualOutputName(
                outputFilename,
                file.liveOutputSlot.index,
                file.liveOutputSlot.total,
              )
            : file.originalName,
        ),
      })),
    );

    convertedFiles.forEach((file, index) => {
      const { xmlName, tacName } = pairs[index]!;
      zip.file(xmlName, file.convertedContent);
      zip.file(tacName, file.originalContent);
      if (includeConversionMetadata) {
        zip.file(
          D.metaSidecarFileName(xmlName),
          D.serializeConversionMetadata(buildFileExportMetadata(file)),
        );
      }
    });

    const content = await zip.generateAsync({ type: 'blob' });
    D.downloadBlob(
      content,
      D.outputArchiveName(outputFilename, {
        firstTac: D.firstTacForArchive(
          firstAccumulatedTac,
          convertedFiles[0]?.originalContent,
        ),
      }),
    );
    D.toast.success(
      includeConversionMetadata
        ? 'All files downloaded as ZIP with metadata'
        : 'All files downloaded as ZIP',
    );
  };

  const handleCopy = (content: string) => {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard
        .writeText(content)
        .then(() => {
          D.toast.success('Copied to clipboard');
        })
        .catch(() => {
          fallbackCopy(content);
        });
    } else {
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
        D.toast.success('Copied to clipboard');
      } else {
        D.toast.error('Failed to copy. Please copy manually.');
      }
    } catch (err) {
      console.error('D.Copy failed:', err);
      D.toast.error('Failed to copy. Please copy manually.');
    }
  };

  const removePendingFile = (id: string) => {
    setPendingFiles((prev) => prev.filter((f) => f.id !== id));
    setSelectedPendingIds((prev) => {
      if (!prev.has(id)) return prev;
      const next = new Set(prev);
      next.delete(id);
      return next;
    });
  };

  const focusQueueItem = (index: number) => {
    const clamped = D.clampQueueIndex(index, pendingFiles.length);
    setQueueFocusIndex(clamped);
    const focusedFile = pendingFiles[clamped];
    D.applyFocusedQueueContent(focusedFile, (content) => {
      setManualInput(content);
      if (!focusedFile!.name.toLowerCase().endsWith('.xml')) {
        applyLoadedReportName(content);
      }
    });
  };

  const handleQueueConvertFocused = async () => {
    const focused =
      pendingFiles[D.clampQueueIndex(queueFocusIndex, pendingFiles.length)];
    if (!focused || isReadOnly || workbenchBusyRef.current) return;
    setIsConverting(true);
    try {
      const result = await performConversion({
        pendingSubset: [focused],
        includeManual: false,
      });
      if (result && !result.softFail) {
        D.toast.success(`Converted ${focused.name}`);
      }
    } finally {
      setIsConverting(false);
    }
  };

  const handleQueueValidateFocused = async () => {
    const focused =
      pendingFiles[D.clampQueueIndex(queueFocusIndex, pendingFiles.length)];
    if (!focused || workbenchBusyRef.current) return;
    setIsBatchValidating(true);
    const progressId = D.toast.loading(`Validating ${focused.name}…`);
    try {
      const product = D.resolveConvertProduct(
        conversionParams.product,
        focused.content,
      );
      const report = await D.lintTac({
        manualText: focused.content,
        product,
      });
      if (report.ok) {
        D.toast.success(`${focused.name}: lint OK`, { id: progressId });
      } else {
        const issueCount = D.lintIssueCount(report.issues);
        D.toast.error(`${focused.name}: ${issueCount} lint issue(s)`, {
          id: progressId,
        });
      }
    } catch (error) {
      D.toast.error(D.focusedValidateErrorMessage(error, focused.name), {
        id: progressId,
      });
    } finally {
      setIsBatchValidating(false);
    }
  };

  const handleBatchConvertSelected = async () => {
    const selected = pendingFiles.filter((f) => selectedPendingIds.has(f.id));
    if (selected.length === 0) {
      D.toast.error('Select one or more queue items to batch convert');
      return;
    }
    if (isReadOnly || workbenchBusyRef.current) return;
    setIsConverting(true);
    try {
      const result = await performConversion({
        pendingSubset: selected,
        includeManual: false,
      });
      if (result) {
        D.toast.success(`Batch converted ${result.files.length} file(s)`);
      }
    } finally {
      setIsConverting(false);
    }
  };

  const handleBatchValidateSelected = async () => {
    const selected = pendingFiles.filter((f) => selectedPendingIds.has(f.id));
    if (selected.length === 0) {
      D.toast.error('Select one or more queue items to batch validate');
      return;
    }
    if (workbenchBusyRef.current) return;
    setIsBatchValidating(true);
    const progressId = D.toast.loading(`Batch validating ${selected.length} file(s)…`);
    let okCount = 0;
    let failCount = 0;
    try {
      for (const file of selected) {
        try {
          const product = D.resolveConvertProduct(
            conversionParams.product,
            file.content,
          );
          const report = await D.lintTac({
            manualText: file.content,
            product,
          });
          if (report.ok) okCount += 1;
          else failCount += 1;
        } catch {
          failCount += 1;
        }
      }
      D.toast.success(`Batch validate: ${okCount} ok, ${failCount} with issues`, {
        id: progressId,
      });
    } finally {
      setIsBatchValidating(false);
    }
  };

  const handleWorkQueueKeyDown = (e: React.KeyboardEvent) => {
    // Queue only mounts when pendingFiles.length > 0 (see JSX below).
    const focus = D.clampQueueIndex(queueFocusIndex, pendingFiles.length);
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      focusQueueItem(D.nextQueueIndex(focus, pendingFiles.length));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      focusQueueItem(D.prevQueueIndex(focus, pendingFiles.length));
    } else if (e.key === 'Enter' && e.shiftKey) {
      e.preventDefault();
      void handleQueueValidateFocused();
    } else if (e.key === 'Enter') {
      e.preventDefault();
      void handleQueueConvertFocused();
    }
  };

  const removeConvertedFile = (id: string) => {
    setConvertedFiles((prev) => {
      const next = prev.filter((f) => f.id !== id);
      if (focusedConvertedId === id) {
        const fallback = next[next.length - 1];
        setFocusedConvertedId(fallback?.id ?? null);
        if (fallback?.convertedContent) {
          setPreviewXml(fallback.convertedContent);
        } else {
          setPreviewXml('');
          setPreviewStatus('empty');
          setPreviewMode('idle');
        }
      }
      return next;
    });
  };

  /**
   * Show one converted file on the IWXXM tab (Downloads is manage-only).
   *
   * @param file - Converted batch entry to preview
   */
  const focusConvertedForPreview = (file: D.ConvertedFile) => {
    setFocusedConvertedId(file.id);
    const xml = D.coalescePreviewXml(file.convertedContent);
    if (xml) {
      setPreviewXml(xml);
      setPreviewMode('live');
      const assessment = D.assessConvertedFile(file);
      setPreviewStatus(assessment.publishBlocked ? 'soft-fail' : 'passed');
      setPreviewSoftFailDetail(undefined);
    }
    setResultsTab('iwxxm');
    setResultsDrawerOpen(true);
  };
  return {
    handleDownloadSingle,
    handleDownloadAll,
    handleCopy,
    fallbackCopy,
    removePendingFile,
    focusQueueItem,
    handleQueueConvertFocused,
    handleQueueValidateFocused,
    handleBatchConvertSelected,
    handleBatchValidateSelected,
    handleWorkQueueKeyDown,
    removeConvertedFile,
    focusConvertedForPreview,
  };
}

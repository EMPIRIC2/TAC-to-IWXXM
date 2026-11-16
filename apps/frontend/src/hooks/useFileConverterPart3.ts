/* eslint-disable @typescript-eslint/ban-ts-comment, @typescript-eslint/no-explicit-any */
// @ts-nocheck — mechanical line-count split
/** useFileConverterPart3 of useFileConverter. */
import * as D from './fileConverterDeps';

/**
 * useFileConverterPart3.
 */
export function useFileConverterPart3(ctx: any) {
  const { setPendingFiles, inputMode, setInputMode, setIsDragging } = ctx;
  const handleFileSelect = async (files: FileList | null) => {
    if (!files || files.length === 0) return;

    const newPendingFiles: D.PendingFile[] = [];
    let detectedMode: D.OperatorInputMode | null = null;

    await Promise.all(
      D.forEachFileInList(files, async (file, i) => {
        try {
          let content: string;
          let displayName = file.name;
          if (D.isGzipFileName(file.name)) {
            content = await D.inflateGzipToText(file);
            displayName = file.name.replace(/\.gz$/i, '').replace(/\.gzip$/i, '');
            D.toast.info(`Decompressed ${file.name}`);
          } else {
            content = await file.text();
          }
          // Classify by decompressed display name + content (not raw .gz → kind "gzip")
          const kind = D.detectInputKind(displayName, content);
          detectedMode = D.kindToMode(kind);
          newPendingFiles.push({
            id: `${displayName}-${Date.now()}-${i}`,
            name: displayName,
            content,
          });
        } catch (error) {
          console.error(`Error reading file ${file.name}:`, error);
          D.toast.error(
            error instanceof Error ? error.message : `Failed to read ${file.name}`,
          );
        }
      }),
    );

    if (detectedMode && detectedMode !== inputMode) {
      setInputMode(detectedMode);
      D.toast.info(
        detectedMode === 'ahl_bulletin'
          ? 'Detected an AHL bulletin. Switched input mode.'
          : detectedMode === 'collect_iwxxm'
            ? 'Detected an IWXXM COLLECT file. Switched input mode.'
            : 'Switched to TAC report mode',
      );
    }

    setPendingFiles((prev) => [...prev, ...newPendingFiles]);
    if (newPendingFiles.length > 0) {
      D.toast.success(`${newPendingFiles.length} file(s) added to queue`);
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

  return {
    handleFileSelect,
    handleDrop,
    handleDragOver,
    handleDragLeave,
  };
}

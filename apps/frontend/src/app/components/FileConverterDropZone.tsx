/** FileConverterDropZone */
import type { FileConverterViewProps } from './FileConverterViewProps';
import * as S from './fileConverterViewScope';

/**
 * FileConverterDropZone.
 */
export function FileConverterDropZone(props: FileConverterViewProps) {
  const {
    fileInputRef,
    handleDragLeave,
    handleDragOver,
    handleDrop,
    handleFileSelect,
    inputMode,
    isBusy,
    isDragging,
    isReadOnly,
  } = props;
  return (
    <S.Card
      className={`mb-1 border-2 border-dashed p-2 shadow-none transition-colors ${
        isDragging
          ? 'border-blue-500 bg-blue-50 dark:border-blue-400 dark:bg-blue-950'
          : 'border-gray-300 bg-white dark:border-gray-700 dark:bg-gray-800'
      }`}
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      role="button"
      aria-label={
        inputMode === 'validate_iwxxm'
          ? 'XML file drop zone - Drop one XML file or click to select it'
          : 'File drop zone - Drop files here or click to select files'
      }
      tabIndex={0}
      data-testid="compact-file-drop-zone"
      onKeyDown={(e) => {
        if (S.isDropZoneActivateKey(e.key)) {
          e.preventDefault();
          fileInputRef.current?.click();
        }
      }}
    >
      <div className="flex flex-col items-stretch gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex min-w-0 items-center gap-2">
          <S.Upload
            className="h-5 w-5 shrink-0 text-gray-400 dark:text-gray-500"
            aria-hidden="true"
          />
          <div className="min-w-0 text-left">
            <p className="text-sm font-medium text-gray-900 dark:text-white">
              {inputMode === 'validate_iwxxm'
                ? S.VALIDATE_IWXXM_DROP_TITLE
                : 'Drop TAC files here'}
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              {inputMode === 'validate_iwxxm'
                ? S.VALIDATE_IWXXM_DROP_HELP
                : 'Or pick files below · .txt, .metar, .tac, .xml, .gz'}
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
          aria-label={
            inputMode === 'validate_iwxxm'
              ? 'Select one XML file to validate'
              : 'Select TAC files to upload'
          }
        />
        <div className="flex flex-wrap items-stretch gap-2 sm:items-center">
          <S.Button
            variant="default"
            size="sm"
            onClick={(e) => {
              e.stopPropagation();
              fileInputRef.current?.click();
            }}
            disabled={isBusy || isReadOnly}
            className="shrink-0 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            aria-label="Browse and select files"
            data-testid="select-files-button"
          >
            <S.FileText className="h-4 w-4" aria-hidden="true" />
            Select files
          </S.Button>
        </div>
      </div>
    </S.Card>
  );
}

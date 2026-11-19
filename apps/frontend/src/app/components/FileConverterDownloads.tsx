/* eslint-disable @typescript-eslint/ban-ts-comment */
// @ts-nocheck — mechanical line-count split
/** FileConverterDownloads */
import type { FileConverterViewProps } from './FileConverterViewProps';
import * as S from './fileConverterViewScope';

/**
 * FileConverterDownloads.
 * @example
 * const _ = true;
 */
export function FileConverterDownloads(props: FileConverterViewProps) {
  const {
    convertedFiles,
    focusConvertedForPreview,
    focusedConverted,
    focusedConvertedId,
    handleCopy,
    handleDownloadAll,
    handleDownloadSingle,
    includeConversionMetadata,
    removeConvertedFile,
    resolveDownloadXmlName,
  } = props;
  return (
    <div data-testid="convert-downloads-panel" className="space-y-3">
      {convertedFiles.length === 0 ? (
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Converted IWXXM files will appear here for download.
        </p>
      ) : (
        <div className="space-y-3" role="region" aria-label="Conversion results">
          {convertedFiles.map((file) => {
            const resultAssessment = S.assessConvertedFile(file);
            const isFocused = (focusedConvertedId ?? focusedConverted?.id) === file.id;
            return (
              <div
                key={file.id}
                className={`rounded-lg border bg-white p-3 dark:bg-gray-800 ${
                  isFocused
                    ? 'border-blue-400 dark:border-blue-500'
                    : 'border-gray-200 dark:border-gray-700'
                }`}
                data-testid={`result-item-${file.id}`}
              >
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <button
                    type="button"
                    className="min-w-0 flex-1 text-left"
                    aria-label={`Show ${file.displayTitle} on IWXXM tab`}
                    aria-pressed={isFocused}
                    data-testid={`convert-download-select-${file.id}`}
                    onClick={() => focusConvertedForPreview(file)}
                  >
                    <div className="flex flex-wrap items-center gap-2">
                      <p className="text-sm font-medium text-gray-900 dark:text-white">
                        {file.displayTitle}
                      </p>
                      <span
                        className="inline-flex items-center rounded-full bg-gray-100 px-2 py-0.5 text-xs font-medium text-gray-800 dark:bg-gray-700 dark:text-gray-100"
                        data-testid={`convert-download-status-${file.id}`}
                      >
                        {resultAssessment.statusLabel}
                      </span>
                      {file.manualLineIndex != null && file.manualLineTotal != null ? (
                        <span className="inline-flex items-center rounded-full bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-800 dark:bg-blue-900/40 dark:text-blue-200">
                          Line {file.manualLineIndex} of {file.manualLineTotal}
                        </span>
                      ) : null}
                    </div>
                    {file.displayTitle !== resolveDownloadXmlName(file) ? (
                      <p className="mt-0.5 text-xs text-gray-500 dark:text-gray-400">
                        Download: {resolveDownloadXmlName(file)}
                      </p>
                    ) : null}
                  </button>
                  <div className="flex gap-1.5">
                    <S.Button
                      variant="outline"
                      size="sm"
                      data-testid={`convert-download-item-${file.id}`}
                      disabled={resultAssessment.publishBlocked}
                      title={
                        resultAssessment.publishBlocked
                          ? 'Do not publish — download disabled until issues are fixed'
                          : undefined
                      }
                      onClick={() => void handleDownloadSingle(file)}
                      className="border-0 bg-blue-500 text-sm text-white hover:bg-blue-600 focus:ring-2 focus:ring-blue-500 disabled:opacity-50 dark:bg-blue-600 dark:hover:bg-blue-700"
                      aria-label={
                        resultAssessment.publishBlocked
                          ? `Do not publish — download disabled for ${resolveDownloadXmlName(file)}`
                          : includeConversionMetadata
                            ? `Download ${resolveDownloadXmlName(file)} as ZIP with metadata`
                            : `Download ${resolveDownloadXmlName(file)} as XML`
                      }
                    >
                      <S.Download className="mr-1 h-4 w-4" aria-hidden="true" />
                      Download
                    </S.Button>
                    <S.Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleCopy(file.convertedContent)}
                      className="border-0 bg-blue-500 text-sm text-white hover:bg-blue-600 focus:ring-2 focus:ring-blue-500 dark:bg-blue-600 dark:hover:bg-blue-700"
                      aria-label={`Copy ${file.originalName} content to clipboard`}
                    >
                      <S.Copy className="mr-1 h-4 w-4" aria-hidden="true" />
                      Copy
                    </S.Button>
                    <S.Button
                      variant="ghost"
                      size="sm"
                      onClick={() => removeConvertedFile(file.id)}
                      className="hover:bg-gray-100 focus:ring-2 focus:ring-red-500 dark:hover:bg-gray-700"
                      aria-label={`Remove ${file.originalName} from results`}
                    >
                      <S.X
                        className="h-4 w-4 text-gray-600 dark:text-gray-400"
                        aria-hidden="true"
                      />
                    </S.Button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
      {convertedFiles.length > 1 ? (
        <S.Button
          type="button"
          variant="secondary"
          size="sm"
          data-testid="convert-downloads-zip"
          onClick={() => {
            void handleDownloadAll();
          }}
        >
          Download all as ZIP
        </S.Button>
      ) : null}
    </div>
  );
}

/** FileConverterSecondaryActions */
import type { FileConverterViewProps } from './FileConverterViewProps';
import * as S from './fileConverterViewScope';

/**
 * FileConverterSecondaryActions.
 * @example
 * const _ = true;
 */
export function FileConverterSecondaryActions(props: FileConverterViewProps) {
  const {
    convertedFiles,
    handleClear,
    handleDownloadAll,
    hasConverted,
    isBusy,
    lintHighlightPreset,
    setLintHighlightPreset,
  } = props;
  return (
    <div
      className="space-y-2 border-t border-gray-200 pt-3 dark:border-gray-700"
      data-testid="convert-settings-secondary-actions"
    >
      <div data-testid="lint-highlight-preset">
        <S.Label
          htmlFor="lint-highlight-preset"
          className="mb-1 block text-sm font-medium text-gray-900 dark:text-white"
        >
          Lint highlight colors
        </S.Label>
        <select
          id="lint-highlight-preset"
          data-testid="lint-highlight-preset-select"
          className="w-full rounded-md border border-gray-300 bg-white px-2 py-1.5 text-sm dark:border-gray-600 dark:bg-gray-800 dark:text-white"
          value={lintHighlightPreset}
          onChange={(event) =>
            setLintHighlightPreset(event.target.value as S.LintHighlightPreset)
          }
        >
          <option value="default">Default</option>
          <option value="colorblind">Colorblind-safe</option>
        </select>
      </div>
      <p className="text-sm font-medium text-gray-900 dark:text-white">More actions</p>
      {/* FR-052..056 / DI-008: Convert&Send + Disseminate removed */}
      <S.Button
        data-testid="download-zip-button"
        onClick={() => void handleDownloadAll()}
        disabled={isBusy || !hasConverted}
        variant="outline"
        className="w-full justify-center text-base disabled:opacity-40 disabled:cursor-not-allowed"
        aria-label={`Download all ${convertedFiles.length} converted files as ZIP`}
      >
        Download ZIP
        <span className="inline-block min-w-[1.75rem] tabular-nums">
          ({convertedFiles.length})
        </span>
      </S.Button>
      <S.Button
        data-testid="clear-queue-button"
        onClick={handleClear}
        variant="ghost"
        className="w-full justify-center text-base text-gray-700 hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-800"
        aria-label="Clear all pending files and manual input"
      >
        Clear
      </S.Button>
    </div>
  );
}

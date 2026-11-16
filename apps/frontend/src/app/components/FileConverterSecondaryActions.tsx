/* eslint-disable complexity -- FileConverter split */
/** FileConverterSecondaryActions */
import type { FileConverterViewProps } from './FileConverterViewProps';
import * as S from './fileConverterViewScope';

/**
 * FileConverterSecondaryActions.
 */
export function FileConverterSecondaryActions(props: FileConverterViewProps) {
  const {
    calmUi,
    conversionParams,
    convertDisabled,
    convertedFiles,
    handleClear,
    handleConvertAndSend,
    handleDisseminationOpenChange,
    handleDownloadAll,
    hasConverted,
    inputMode,
    isBusy,
    isConvertAndSending,
    isReadOnly,
    lintHighlightPreset,
    setLintHighlightPreset,
    setPackagingExchangeProfile,
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
      {S.isOperatorDisseminationDestinationsEnabled() &&
      inputMode !== 'validate_iwxxm' &&
      conversionParams.product !== 'IWXXM' ? (
        <S.Button
          data-testid="convert-and-send-button"
          variant="outline"
          onClick={handleConvertAndSend}
          disabled={convertDisabled}
          className="w-full justify-center text-base disabled:opacity-50 disabled:cursor-not-allowed"
          aria-busy={isConvertAndSending}
          aria-label={
            isConvertAndSending
              ? 'Converting and sending files, please wait (beta)'
              : 'Convert TAC to IWXXM XML and send to database (beta)'
          }
        >
          <S.Loader2
            className={`w-4 h-4 animate-spin ${isConvertAndSending ? '' : 'invisible'}`}
            aria-hidden="true"
          />
          {calmUi.primaryKind === 'download' ? 'Send…' : 'Convert&Send'}
          <S.BetaBadge className="ml-1 inline-flex" />
        </S.Button>
      ) : null}
      {S.isOperatorDisseminationDestinationsEnabled() ? (
        <S.Button
          type="button"
          data-testid="open-dissemination-drawer"
          onClick={() => {
            setPackagingExchangeProfile(conversionParams.exchangeProfile);
            handleDisseminationOpenChange(true);
          }}
          disabled={isBusy || isReadOnly}
          variant="outline"
          className="w-full justify-center text-base disabled:opacity-40 disabled:cursor-not-allowed"
          aria-label="Open dissemination drawer for BYOC upload or publish (beta)"
        >
          {calmUi.primaryKind === 'download' ? 'Send…' : 'Disseminate'}
          <S.BetaBadge className="ml-1 inline-flex" />
        </S.Button>
      ) : null}
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

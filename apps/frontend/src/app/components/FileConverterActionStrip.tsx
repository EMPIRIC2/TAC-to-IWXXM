/* eslint-disable complexity -- FileConverter split */
/** FileConverterActionStrip */
import type { FileConverterViewProps } from './FileConverterViewProps';
import * as S from './fileConverterViewScope';

/**
 * FileConverterActionStrip.
 */
export function FileConverterActionStrip(props: FileConverterViewProps) {
  const {
    calmUi,
    conversionParams,
    convertDisabled,
    handleConvert,
    handleDownloadSingle,
    handleNewMetar,
    inputMode,
    isBusy,
    isConverting,
    latestConverted,
    saveIndicatorLabel,
  } = props;
  return (
    <div className="mb-4" data-testid="action-button-strip">
      <div
        className="mb-2 flex h-5 items-center"
        aria-live="polite"
        data-testid="autosave-indicator"
      >
        {saveIndicatorLabel ? (
          <span className="text-sm text-gray-600 dark:text-gray-400">
            {saveIndicatorLabel}
          </span>
        ) : (
          <span className="sr-only">Autosave idle</span>
        )}
      </div>
      <div
        className="grid min-h-10 w-full grid-cols-1 gap-2 sm:grid-cols-3 sm:gap-3"
        data-testid="convert-primary-actions"
      >
        <S.Button
          type="button"
          variant="outline"
          onClick={handleNewMetar}
          disabled={isBusy}
          data-testid="new-tac-button"
          aria-label="Start a new TAC session"
          className="w-full"
        >
          New TAC
        </S.Button>
        <S.Button
          data-testid="convert-button"
          variant={calmUi.primaryKind === 'convert' ? 'default' : 'outline'}
          onClick={handleConvert}
          disabled={convertDisabled}
          className="relative w-full text-base disabled:opacity-50 disabled:cursor-not-allowed"
          aria-busy={isConverting}
          aria-label={
            isConverting
              ? inputMode === 'validate_iwxxm' || conversionParams.product === 'IWXXM'
                ? 'Validating IWXXM, please wait'
                : 'Converting files, please wait'
              : inputMode === 'validate_iwxxm'
                ? 'Validate IWXXM XML'
                : conversionParams.product === 'IWXXM'
                  ? S.IWXXM_PRODUCT_CONVERT_ARIA
                  : S.CALM_CONVERT_PRIMARY_LABEL
          }
        >
          <S.Loader2
            className={`absolute left-3 h-4 w-4 animate-spin ${isConverting ? '' : 'invisible'}`}
            aria-hidden="true"
          />
          {inputMode === 'validate_iwxxm'
            ? 'Validate'
            : conversionParams.product === 'IWXXM'
              ? S.IWXXM_PRODUCT_CONVERT_LABEL
              : S.CALM_CONVERT_PRIMARY_LABEL}
        </S.Button>
        <span
          className="min-w-0 w-full"
          data-testid={
            calmUi.primaryKind === 'download' ? 'convert-primary-cta' : undefined
          }
        >
          <S.Button
            variant={calmUi.primaryKind === 'download' ? 'default' : 'outline'}
            onClick={() => {
              if (!latestConverted) return;
              void handleDownloadSingle(latestConverted);
            }}
            disabled={isBusy || !latestConverted}
            className="w-full text-base disabled:opacity-40 disabled:cursor-not-allowed"
            aria-label={S.CALM_DOWNLOAD_PRIMARY_LABEL}
            data-testid="convert-download-iwxxm"
          >
            <S.Download className="mr-2 h-4 w-4" aria-hidden="true" />
            {S.CALM_DOWNLOAD_PRIMARY_LABEL}
          </S.Button>
        </span>
      </div>
    </div>
  );
}

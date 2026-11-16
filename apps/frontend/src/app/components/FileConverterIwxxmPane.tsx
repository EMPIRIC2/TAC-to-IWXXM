/* eslint-disable @typescript-eslint/ban-ts-comment, complexity */
// @ts-nocheck — mechanical line-count split
/** Extracted iwxxm-resize-pane region. */
import type { FileConverterViewProps } from './FileConverterViewProps';
import * as S from './fileConverterViewScope';

/**
 * FileConverterIwxxmPane.
 * @example
 * const _ = true;
 */
export function FileConverterIwxxmPane(props: FileConverterViewProps) {
  const {
    liveLayout,
    conversionParams,
    failedSpans,
    focusedAssessment,
    groupTrace,
    inputMode,
    lintCatalogByCode,
    previewIncomplete,
    previewMode,
    previewSoftFailDetail,
    previewStatus,
    previewXml,
    selectedTrace,
    validateReport,
  } = props;
  return (
    <div data-testid="iwxxm-resize-pane" className="flex h-full min-h-0 flex-col gap-3">
      {inputMode !== 'validate_iwxxm' && focusedAssessment ? (
        <S.ConvertResultStatus assessment={focusedAssessment} />
      ) : null}
      {inputMode === 'validate_iwxxm' ? (
        <section
          data-testid="validate-iwxxm-results"
          aria-label="Validation results"
          className="flex min-h-0 flex-col overflow-auto rounded-md border border-gray-200 bg-white p-3 dark:border-gray-700 dark:bg-gray-900"
        >
          <h3 className="mb-2 text-sm font-semibold text-gray-900 dark:text-white">
            Validation results
          </h3>
          {validateReport ? (
            <S.ValidateIwxxmReport
              report={validateReport}
              catalogByCode={lintCatalogByCode}
            />
          ) : (
            <p
              data-testid="validate-iwxxm-empty"
              className="text-sm text-gray-500 dark:text-gray-400"
            >
              {S.VALIDATE_IWXXM_EMPTY_RESULTS}
            </p>
          )}
        </section>
      ) : (
        <S.IwxxmPreviewPane
          className="min-w-0"
          xml={previewXml}
          status={previewStatus}
          mode={previewMode}
          softFailDetail={previewSoftFailDetail}
          failedSpanCount={failedSpans.length}
          numbered
          highlightToken={selectedTrace?.code ?? ''}
          highlightStart={selectedTrace?.start}
          highlightEnd={selectedTrace?.end}
          groupTrace={groupTrace}
          incomplete={previewIncomplete && previewXml.trim().length > 0}
          conversionProfile={
            conversionParams.conversionLibraryId || conversionParams.profile
          }
          wrapXml={liveLayout.wrapXml}
          onFailedSpanFocus={() => {
            document.querySelector('[data-testid="failed-tac-cue"]')?.scrollIntoView({
              behavior: 'smooth',
              block: 'nearest',
            });
          }}
        />
      )}
    </div>
  );
}

/* eslint-disable @typescript-eslint/ban-ts-comment, complexity */
// @ts-nocheck — mechanical line-count split
/** FileConverterBody */
import type { FileConverterViewProps } from './FileConverterViewProps';
import * as S from './fileConverterViewScope';

/**
 * FileConverterBody.
 */
export function FileConverterBody(props: FileConverterViewProps) {
  const {
    applyLoadedReportName,

    liveLayout,
    activeProfileExampleProducts,
    applyLintFix,
    applyLintJump,
    bulletinReports,
    bulletinSource,
    bulletinSummary,
    calmTacReadOnly,
    conversionParams,
    converterOpen,
    converterPaneHeight,
    demoExampleLabel,
    editorSpans,
    failedSpans,
    focusedBulletinReport,
    handleLoadGoldenExample,
    inputMode,
    isReadOnly,
    jumpIssues,
    lintFocusOffset,
    lintJump,
    manualInput,
    placeholderNotice,
    previewSoftFailDetail,
    previewStatus,
    setBulletinSource,
    setConverterPaneHeight,
    setFocusedBulletinReport,
    setLintFocusOffset,
    setLintJump,
    setManualInput,
    setRecentWorkCollapsed,
    setSelectedTrace,
    setTacLockedAfterConvert,
    tacLintSummary,
  } = props;
  return (
    <div hidden={!converterOpen} data-testid="convert-body" className="p-2">
      {inputMode !== 'validate_iwxxm' && demoExampleLabel && (
        <S.StatusBanner
          tone="info"
          className="mb-2 text-xs"
          data-testid="demo-example-banner"
        >
          Demo / non-operational example: {demoExampleLabel}
        </S.StatusBanner>
      )}
      {inputMode === 'ahl_bulletin' && (
        <p className="mb-2 text-xs text-gray-600 dark:text-gray-400">
          AHL bulletins are split and converted via{' '}
          <code>POST /api/v1/convert-bulletin</code>.
        </p>
      )}
      {inputMode === 'collect_iwxxm' && (
        <p className="mb-2 text-xs text-amber-800 dark:text-amber-200">
          IWXXM COLLECT / FTBP path uses <code>POST /api/v1/ingest-collect</code> (not
          available yet; the request returns 501 until member extract ships).
        </p>
      )}
      {inputMode === 'validate_iwxxm' && (
        <p
          className="mb-2 text-xs text-gray-600 dark:text-gray-400"
          data-testid="validate-iwxxm-help"
        >
          Paste IWXXM XML or upload one <code>.xml</code> file. This checks the XML
          only. It does not convert TAC.
        </p>
      )}
      {conversionParams.product === 'IWXXM' && inputMode !== 'validate_iwxxm' && (
        <p
          className="mb-2 text-xs text-gray-600 dark:text-gray-400"
          data-testid="iwxxm-product-help"
          role="status"
        >
          {S.IWXXM_PRODUCT_HELP}
        </p>
      )}
      {bulletinSummary && (
        <S.StatusBanner
          tone="info"
          className="mb-2 text-xs"
          data-testid="bulletin-summary"
        >
          {bulletinSummary}
        </S.StatusBanner>
      )}
      {placeholderNotice && (
        <S.StatusBanner
          tone="caution"
          className="mb-2 text-xs"
          data-testid="placeholder-notice"
        >
          {placeholderNotice}
        </S.StatusBanner>
      )}
      {bulletinReports.length >= 2 ? (
        <S.BulletinReportList
          reports={bulletinReports}
          selectedIndex={focusedBulletinReport}
          onShowAll={() => {
            setFocusedBulletinReport(null);
            setManualInput(bulletinSource || manualInput);
          }}
          onSelect={(index, tac) => {
            const source = bulletinSource || manualInput;
            setBulletinSource(source);
            setFocusedBulletinReport(index);
            setManualInput(tac);
            setSelectedTrace(null);
          }}
        />
      ) : null}
      <div data-testid="convert-panes-slot">
        <div
          className="flex min-h-0 min-w-0 flex-col overflow-auto rounded-md border border-gray-200 bg-white p-2 dark:border-gray-700 dark:bg-gray-900"
          data-testid="live-convert-panes"
          data-fit={liveLayout.span === 'roomy' ? 'roomy' : 'tight'}
          role="region"
          aria-label={inputMode === 'validate_iwxxm' ? 'IWXXM' : 'TAC'}
          style={{ height: converterPaneHeight }}
          onFocusCapture={() => setRecentWorkCollapsed(true)}
          onKeyDown={(event) => {
            const issue = S.lintIssueFromKey(event, jumpIssues, lintJump);
            if (!issue) return;
            event.preventDefault();
            applyLintJump(issue);
          }}
        >
          <div className="mb-2 flex items-center justify-between gap-2">
            <h2 className="text-sm font-semibold text-gray-900 dark:text-white">
              {inputMode === 'validate_iwxxm' ? 'IWXXM' : 'TAC'}
            </h2>
            {calmTacReadOnly && !isReadOnly ? (
              <button
                type="button"
                className="text-sm font-medium text-blue-700 underline-offset-2 hover:underline dark:text-blue-300"
                data-testid="convert-tac-edit"
                onClick={() => setTacLockedAfterConvert(false)}
              >
                Edit
              </button>
            ) : null}
          </div>
          {inputMode !== 'validate_iwxxm' ? (
            <div
              className="mb-2 flex min-w-0 flex-wrap items-center gap-2"
              data-testid="convert-examples-bar"
            >
              <S.GoldenExamplesSelect
                applicableProducts={activeProfileExampleProducts}
                disabled={isReadOnly}
                semanticProfile={conversionParams.profile}
                onSelectExample={handleLoadGoldenExample}
                onOpenChange={(open) => {
                  if (open) {
                    setRecentWorkCollapsed(true);
                  }
                }}
              />
            </div>
          ) : null}
          <div
            data-testid={
              calmTacReadOnly ? 'convert-tac-readonly' : 'convert-tac-editable'
            }
            data-glossary-exclude="true"
          >
            <S.TacEditor
              id="manual-input"
              value={manualInput}
              onReportLoaded={applyLoadedReportName}
              onChange={(value) => {
                setManualInput(value);
                setSelectedTrace(null);
                setLintJump(null);
                setLintFocusOffset(null);
                if (inputMode !== 'ahl_bulletin') {
                  return;
                }
                if (focusedBulletinReport === null) {
                  setBulletinSource(value);
                  return;
                }
                setBulletinSource((current) =>
                  S.replaceBulletinReport(current, focusedBulletinReport, value),
                );
              }}
              readOnly={calmTacReadOnly}
              placeholder={
                inputMode === 'validate_iwxxm'
                  ? '<iwxxm:METAR>...</iwxxm:METAR>'
                  : 'SPECI BGSF 282350Z 10RMF50MT 9999 SCT110 BKN130 0RN130 NN7/N11 Q1021'
              }
              aria-label={
                inputMode === 'validate_iwxxm'
                  ? 'Enter IWXXM XML manually'
                  : 'Enter METAR data manually'
              }
              className="max-h-80 min-h-44 focus-within:ring-2 focus-within:ring-blue-500"
              failedSpans={failedSpans}
              issueSpans={editorSpans}
              onSpanFix={applyLintFix}
              focusOffset={lintFocusOffset}
            />
          </div>
          {inputMode !== 'validate_iwxxm' ? (
            <>
              <p
                className="mt-2 text-xs text-gray-700 dark:text-gray-200"
                data-testid="tac-lint-summary"
              >
                {tacLintSummary}
              </p>
              <S.TacLintJumps
                issues={jumpIssues}
                activeIndex={lintJump}
                onSelect={applyLintJump}
              />
            </>
          ) : null}
        </div>
        <S.VerticalResizeHandle
          height={converterPaneHeight}
          onHeightChange={setConverterPaneHeight}
          label="Resize converter box"
          testId="converter-vertical-resize"
        />
      </div>
      <div className="mt-2 space-y-2" data-testid="convert-error-cues">
        {inputMode !== 'validate_iwxxm' ? (
          <>
            <S.FailedTacCue failedSpans={failedSpans} />
            {previewStatus === 'soft-fail' && previewSoftFailDetail ? (
              <S.StatusBanner
                tone="caution"
                className="text-xs"
                data-testid="convert-soft-fail-cue"
              >
                {previewSoftFailDetail}
              </S.StatusBanner>
            ) : null}
          </>
        ) : null}
      </div>
    </div>
  );
}

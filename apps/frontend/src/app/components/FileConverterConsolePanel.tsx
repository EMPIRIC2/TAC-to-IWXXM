/* eslint-disable @typescript-eslint/ban-ts-comment */
// @ts-nocheck — mechanical line-count split
/** Extracted convert-console-panel region. */
import type { FileConverterViewProps } from './FileConverterViewProps';
import * as S from './fileConverterViewScope';

/**
 * FileConverterConsolePanel.
 */
export function FileConverterConsolePanel(props: FileConverterViewProps) {
  const {
    consoleSchemaStatus,
    consoleSchematronStatus,
    conversionLog,
    conversionParams,
    decodeLoading,
    decodeSegments,
    inputMode,
    lintCatalogByCode,
    lintCounts,
    manualInput,
    onOpenCatalog,
    previewIncomplete,
    previewXml,
  } = props;
  return (
    <div className="space-y-3" data-testid="convert-console-panel">
      {inputMode !== 'validate_iwxxm' ? (
        <S.LiveConvertStatusStrip
          hasTac={manualInput.trim().length > 0}
          decodeReady={decodeSegments.length > 0}
          decodeLoading={decodeLoading}
          previewState={
            !previewXml.trim()
              ? 'waiting'
              : previewIncomplete
                ? 'incomplete'
                : 'current'
          }
          lintStatus={S.tacLintLayerStatus({
            hasTac: manualInput.trim().length > 0,
            loading: decodeLoading,
            errorCount: lintCounts.errorCount,
            warningCount: lintCounts.warningCount,
            issueCount: lintCounts.issueCount,
          })}
          schemaStatus={consoleSchemaStatus}
          schematronStatus={consoleSchematronStatus}
        />
      ) : null}
      {conversionLog ? (
        <S.ErrorLogPanel
          log={conversionLog}
          minLogLevel={conversionParams.logLevel as ConvertLogLevel}
          catalogByCode={lintCatalogByCode}
          onOpenCatalog={onOpenCatalog}
        />
      ) : null}
    </div>
  );
}

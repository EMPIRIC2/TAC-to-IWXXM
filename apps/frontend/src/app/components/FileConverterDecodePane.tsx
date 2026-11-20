/** Extracted decode-pane region. */
import type { FileConverterViewProps } from './FileConverterViewProps';
import * as S from './fileConverterViewScope';

/**
 * FileConverterDecodePane.
 * @example
 * const _ = true;
 */
export function FileConverterDecodePane(props: FileConverterViewProps) {
  const {
    liveLayout,
    conversionParams,
    decodeError,
    decodeLoading,
    decodeResiduals,
    decodeSegments,
    decodeSummary,
    selectedTrace,
    setSelectedTrace,
    decodeProduct,
    inputMode,
  } = props;
  if (inputMode === 'validate_iwxxm') {
    return (
      <p className="text-sm text-gray-500 dark:text-gray-400">
        Decoder is available in TAC convert mode.
      </p>
    );
  }
  return (
    <div
      className="flex h-full min-h-0 min-w-0 flex-col overflow-hidden"
      data-testid="decode-pane"
    >
      <S.DecodePanel
        segments={decodeSegments}
        residuals={decodeResiduals}
        summary={decodeSummary}
        product={decodeProduct}
        loading={decodeLoading}
        error={decodeError}
        pinned
        defaultOpen
        decodingProfile={
          S.libraryDisplayName(conversionParams.decodingLibraryId) || undefined
        }
        density={liveLayout.density}
        selectedStart={selectedTrace?.start}
        selectedEnd={selectedTrace?.end}
        onSelect={setSelectedTrace}
      />
    </div>
  );
}

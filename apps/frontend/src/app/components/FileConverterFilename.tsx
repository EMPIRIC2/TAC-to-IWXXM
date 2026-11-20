/** FileConverterFilename */
import type { FileConverterViewProps } from './FileConverterViewProps';
import * as S from './fileConverterViewScope';

/**
 * FileConverterFilename.
 * @example
 * const _ = true;
 */
export function FileConverterFilename(props: FileConverterViewProps) {
  const {
    inputMode,
    isBusy,
    isReadOnly,
    liveIwxxm,
    outputFilename,
    outputFilenameOwnedRef,
    propagateResiduals,
    setLiveIwxxm,
    setOutputFilename,
    setPropagateResiduals,
    setSoftPreview,
    softPreview,
  } = props;
  if (inputMode === 'validate_iwxxm') {
    return null;
  }
  return (
    <>
      <div data-testid="output-filename-near-convert">
        <S.Label
          htmlFor="output-filename"
          className="mb-1 block text-sm font-medium text-gray-900 dark:text-white"
        >
          Output filename (optional)
        </S.Label>
        <S.Input
          id="output-filename"
          data-testid="output-filename-input"
          value={outputFilename}
          onChange={(e) => {
            const value = e.target.value;
            outputFilenameOwnedRef.current = value.trim() !== '';
            setOutputFilename(value);
          }}
          readOnly={isReadOnly}
          placeholder="manual_input"
          className="text-sm dark:border-gray-700 dark:bg-gray-800 dark:text-white focus:ring-2 focus:ring-blue-500"
          aria-label="Output filename for manually entered METAR downloads"
        />
        <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
          Saves as{' '}
          <code data-testid="output-filename-preview">
            {S.sanitizeOutputFilename(outputFilename)}.xml
          </code>
          .
        </p>
      </div>
      <S.SoftPreviewControl
        checked={softPreview}
        onChange={setSoftPreview}
        disabled={isReadOnly || isBusy}
      />
      <S.PropagateResidualsControl
        checked={propagateResiduals}
        onChange={setPropagateResiduals}
        disabled={isReadOnly || isBusy}
      />
      <S.LiveIwxxmToggle
        checked={liveIwxxm}
        onChange={setLiveIwxxm}
        disabled={isReadOnly || isBusy}
      />
    </>
  );
}

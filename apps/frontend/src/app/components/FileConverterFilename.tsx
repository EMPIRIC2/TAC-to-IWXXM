/** FileConverterFilename — Convert optional parameters strip. */
import type { FileConverterViewProps } from './FileConverterViewProps';
import { IncludeNationalRemarksControl, INCLUDE_NATIONAL_REMARKS_HELP } from './IncludeNationalRemarksControl';
import { LiveIwxxmToggle } from './LiveIwxxmToggle';
import { PropagateResidualsControl, PROPAGATE_RESIDUALS_HELP } from './PropagateResidualsControl';
import { SoftPreviewControl } from './SoftPreviewControl';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { sanitizeOutputFilename } from '@/utils/outputFilename';

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
    includeNationalRemarks,
    setLiveIwxxm,
    setOutputFilename,
    setPropagateResiduals,
    setIncludeNationalRemarks,
    setSoftPreview,
    softPreview,
  } = props;
  if (inputMode === 'validate_iwxxm') {
    return null;
  }
  const controlsDisabled = isReadOnly || isBusy;
  return (
    <div
      data-testid="conversion-options"
      className="space-y-3 border-b border-gray-200 px-2 py-2 dark:border-gray-700"
    >
      <div data-testid="output-filename-near-convert" className="w-full min-w-0">
        <Label
          htmlFor="output-filename"
          className="mb-1 block text-sm font-medium text-gray-900 dark:text-white"
        >
          Output filename (optional)
        </Label>
        <Input
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
          className="w-full text-sm dark:border-gray-700 dark:bg-gray-800 dark:text-white focus:ring-2 focus:ring-blue-500"
          aria-label="Output filename for manually entered METAR downloads"
        />
        <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
          Saves as{' '}
          <code data-testid="output-filename-preview">
            {sanitizeOutputFilename(outputFilename)}.xml
          </code>
          .
        </p>
      </div>

      <div
        data-testid="conversion-option-toggles"
        className="flex flex-col gap-2"
        aria-label="Conversion options"
      >
        <SoftPreviewControl
          checked={softPreview}
          onChange={setSoftPreview}
          disabled={controlsDisabled}
        />
        <PropagateResidualsControl
          checked={propagateResiduals}
          onChange={setPropagateResiduals}
          disabled={controlsDisabled}
        />
        <IncludeNationalRemarksControl
          checked={includeNationalRemarks}
          onChange={setIncludeNationalRemarks}
          disabled={controlsDisabled}
        />
        <LiveIwxxmToggle
          checked={liveIwxxm}
          onChange={setLiveIwxxm}
          disabled={controlsDisabled}
        />
      </div>

      <details
        data-testid="conversion-options-about"
        className="text-xs text-gray-500 dark:text-gray-400"
      >
        <summary className="cursor-pointer select-none text-gray-600 hover:text-gray-800 dark:text-gray-300 dark:hover:text-gray-100">
          About these options
        </summary>
        <ul className="mt-2 list-disc space-y-1.5 pl-4">
          <li>
            <span className="font-medium text-gray-700 dark:text-gray-200">
              Keep leftover TAC in remarks:{' '}
            </span>
            {PROPAGATE_RESIDUALS_HELP}
          </li>
          <li>
            <span className="font-medium text-gray-700 dark:text-gray-200">
              Include national remarks in IWXXM:{' '}
            </span>
            {INCLUDE_NATIONAL_REMARKS_HELP}
          </li>
          <li>
            <span className="font-medium text-gray-700 dark:text-gray-200">
              Live IWXXM:{' '}
            </span>
            When on, the IWXXM preview rebuilds as you edit the TAC text.
          </li>
        </ul>
      </details>
    </div>
  );
}

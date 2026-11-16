/** FileConverterIntro */
import type { FileConverterViewProps } from './FileConverterViewProps';
import * as S from './fileConverterViewScope';

/**
 * FileConverterIntro.
 * @example
 * const _ = true;
 */
export function FileConverterIntro(props: FileConverterViewProps) {
  const { inputMode } = props;
  return (
    <p
      className="text-base text-gray-600 dark:text-gray-300"
      data-testid="workbench-intro"
    >
      {inputMode === 'validate_iwxxm'
        ? S.VALIDATE_IWXXM_INTRO
        : 'Enter TAC in the console below (choose product type as needed), then Convert. Upload files from the compact drop zone under the console when preferred.'}
    </p>
  );
}

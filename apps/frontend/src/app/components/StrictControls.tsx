/**
 * Strict master checkbox and optional per-step raise toggles (ADR-054).
 *
 * Plain-language operator copy only — no planning ids.
 */

/**
 * Type `StrictControlsProps`.
 * @example
 * const _ = true;
 */
export interface StrictControlsProps {
  strict: boolean;
  strictLint: boolean;
  strictConvert: boolean;
  strictValidate: boolean;
  onStrictChange: (value: boolean) => void;
  onStrictLintChange: (value: boolean) => void;
  onStrictConvertChange: (value: boolean) => void;
  onStrictValidateChange: (value: boolean) => void;
}

/**
 * Validation Options Strict control for the conversion parameters bar.
 *
 * @param props - Controlled Strict + step flags
 * @returns Strict checkbox group
 * @example
 * const _ = true;
 */
export function StrictControls(props: StrictControlsProps) {
  const {
    strict,
    strictLint,
    strictConvert,
    strictValidate,
    onStrictChange,
    onStrictLintChange,
    onStrictConvertChange,
    onStrictValidateChange,
  } = props;

  return (
    <div className="flex flex-col gap-2">
      <label className="flex cursor-pointer items-center">
        <input
          type="checkbox"
          checked={strict}
          onChange={(e) => onStrictChange(e.target.checked)}
          className="h-4 w-4 rounded text-blue-600 focus:ring-2 focus:ring-blue-500"
          data-testid="strict-validation-checkbox"
        />
        <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">Strict</span>
      </label>
      <p className="-mt-1 ml-6 text-xs text-gray-500 dark:text-gray-400">
        Off (default): only convert failures and IWXXM validation failures are
        highlighted. On: also highlight dialect warnings and informational notes, and
        run IWXXM output checks when the Validate step is on.
      </p>
      {strict ? (
        <div className="ml-6 flex flex-col gap-1" data-testid="strict-step-toggles">
          <label className="flex cursor-pointer items-center">
            <input
              type="checkbox"
              checked={strictLint}
              onChange={(e) => onStrictLintChange(e.target.checked)}
              className="h-3.5 w-3.5 rounded text-blue-600"
              data-testid="strict-lint-checkbox"
            />
            <span className="ml-2 text-xs text-gray-700 dark:text-gray-300">
              TAC lint
            </span>
          </label>
          <label className="flex cursor-pointer items-center">
            <input
              type="checkbox"
              checked={strictConvert}
              onChange={(e) => onStrictConvertChange(e.target.checked)}
              className="h-3.5 w-3.5 rounded text-blue-600"
              data-testid="strict-convert-checkbox"
            />
            <span className="ml-2 text-xs text-gray-700 dark:text-gray-300">
              Convert
            </span>
          </label>
          <label className="flex cursor-pointer items-center">
            <input
              type="checkbox"
              checked={strictValidate}
              onChange={(e) => onStrictValidateChange(e.target.checked)}
              className="h-3.5 w-3.5 rounded text-blue-600"
              data-testid="strict-validate-checkbox"
            />
            <span className="ml-2 text-xs text-gray-700 dark:text-gray-300">
              IWXXM validate
            </span>
          </label>
        </div>
      ) : null}
    </div>
  );
}

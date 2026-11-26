/**
 * Opt-in toggle for keeping national RMK content in IWXXM convert output.
 */

/** Operator-visible label (must stay free of internal doc ids). */
export const INCLUDE_NATIONAL_REMARKS_LABEL = 'Include national remarks in IWXXM';

/** Operator-visible help (tooltip / About these options — not always-visible). */
export const INCLUDE_NATIONAL_REMARKS_HELP =
  'When off, remarks after RMK are left out of the IWXXM result. National remarks are not meant for international distribution.';

/**
 * Type `IncludeNationalRemarksControlProps`.
 * @example
 * const _ = true;
 */
export interface IncludeNationalRemarksControlProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  disabled?: boolean;
}

/**
 * Toggle ``include_national_remarks`` on convert requests (default on).
 *
 * @param props.checked - Whether national remarks are kept
 * @param props.onChange - Called with the next checked state
 * @example
 * const _ = true;
 */
export function IncludeNationalRemarksControl({
  checked,
  onChange,
  disabled = false,
}: IncludeNationalRemarksControlProps) {
  return (
    <label
      className="mb-0 flex cursor-pointer items-center gap-2 text-sm text-gray-800 dark:text-gray-200"
      title={INCLUDE_NATIONAL_REMARKS_HELP}
    >
      <input
        type="checkbox"
        data-testid="include-national-remarks-toggle"
        className="h-4 w-4 rounded border-gray-300 text-rose-600 focus:ring-rose-500"
        checked={checked}
        disabled={disabled}
        onChange={(e) => onChange(e.target.checked)}
      />
      <span className="font-medium">{INCLUDE_NATIONAL_REMARKS_LABEL}</span>
    </label>
  );
}

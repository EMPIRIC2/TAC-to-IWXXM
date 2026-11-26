/**
 * Live IWXXM toggle for the F7 workbench. Convert turns this on so the
 * preview rebuilds while the operator types. It can still be switched off.
 * @example
 * const _ = true;
 */

/** Operator-visible label. */
export const LIVE_IWXXM_LABEL = 'Live IWXXM';

/** Short hint kept inline with the label (compact strip). */
export const LIVE_IWXXM_HINT = '(preview updates as you type)';

/**
 * Type `LiveIwxxmToggleProps`.
 * @example
 * const _ = true;
 */
export interface LiveIwxxmToggleProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  disabled?: boolean;
}

/**
 * Opt-in live convert/preview while editing.
 *
 * @param props.checked - Whether live IWXXM is enabled
 * @param props.onChange - Toggle handler
 * @example
 * const _ = true;
 */
export function LiveIwxxmToggle({
  checked,
  onChange,
  disabled = false,
}: LiveIwxxmToggleProps) {
  return (
    <label
      className="mb-0 flex cursor-pointer items-center gap-2 text-sm text-gray-800 dark:text-gray-200"
      data-testid="live-iwxxm-toggle-label"
      title="When on, the IWXXM preview rebuilds as you edit the TAC text."
    >
      <input
        type="checkbox"
        data-testid="live-iwxxm-toggle"
        checked={checked}
        disabled={disabled}
        onChange={(e) => onChange(e.target.checked)}
        className="h-4 w-4 rounded border-gray-300"
      />
      <span>
        <span className="font-medium">{LIVE_IWXXM_LABEL}</span>
        <span className="ml-1 text-gray-500 dark:text-gray-400">{LIVE_IWXXM_HINT}</span>
      </span>
    </label>
  );
}

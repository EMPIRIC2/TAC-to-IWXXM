/**
 * Live IWXXM toggle for the F7 workbench — default off (04 Batch 1 A / UJ-017).
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
 */
export function LiveIwxxmToggle({
  checked,
  onChange,
  disabled = false,
}: LiveIwxxmToggleProps) {
  return (
    <label
      className="inline-flex items-center gap-2 text-sm text-gray-800 dark:text-gray-200"
      data-testid="live-iwxxm-toggle-label"
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
        <span className="font-medium">Live IWXXM</span>
        <span className="ml-1 text-gray-500 dark:text-gray-400">
          (off by default — soft-preview while typing)
        </span>
      </span>
    </label>
  );
}

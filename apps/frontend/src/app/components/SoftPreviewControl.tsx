/**
 * Soft-preview checkbox for convert ``preview=true`` (UJ-016 / ADR-022).
 */

export interface SoftPreviewControlProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  disabled?: boolean;
}

/**
 * Toggle soft-preview mode on convert requests.
 *
 * @param props.checked - Whether soft-preview is enabled
 * @param props.onChange - Called with the next checked state
 */
export function SoftPreviewControl({
  checked,
  onChange,
  disabled = false,
}: SoftPreviewControlProps) {
  return (
    <label className="mb-4 flex cursor-pointer items-start gap-2 text-sm text-gray-800 dark:text-gray-200">
      <input
        type="checkbox"
        data-testid="soft-preview-toggle"
        className="mt-0.5 h-4 w-4 rounded border-gray-300 text-rose-600 focus:ring-rose-500"
        checked={checked}
        disabled={disabled}
        onChange={(e) => onChange(e.target.checked)}
      />
      <span>
        <span className="font-medium">Soft-preview</span>
        <span className="block text-xs text-gray-500 dark:text-gray-400">
          Return best-effort IWXXM and failed spans when TAC is partial (not for
          publish).
        </span>
      </span>
    </label>
  );
}

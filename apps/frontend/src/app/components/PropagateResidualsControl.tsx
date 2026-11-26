/**
 * Opt-in fold of decode leftovers into remarks / human-readable text (convert flag).
 */

/** Operator-visible label (scanned by TC-EV048 / TC-EV981-003). */
export const PROPAGATE_RESIDUALS_LABEL = 'Keep leftover TAC in remarks';

/** Operator-visible help (tooltip / About these options — not always-visible). */
export const PROPAGATE_RESIDUALS_HELP =
  'When on, leftover TAC that could not be decoded is kept in remarks or readable text for profiles that support that. The international profile has no remarks field, so leftovers stay in the diagnostic list only.';

/**
 * Type `PropagateResidualsControlProps`.
 * @example
 * const _ = true;
 */
export interface PropagateResidualsControlProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  disabled?: boolean;
}

/**
 * Toggle ``propagate_residuals_to_remarks`` on convert requests.
 *
 * @param props.checked - Whether fold is requested (explicit true)
 * @param props.onChange - Called with the next checked state
 * @example
 * const _ = true;
 */
export function PropagateResidualsControl({
  checked,
  onChange,
  disabled = false,
}: PropagateResidualsControlProps) {
  return (
    <label
      className="mb-0 flex cursor-pointer items-center gap-2 text-sm text-gray-800 dark:text-gray-200"
      title={PROPAGATE_RESIDUALS_HELP}
    >
      <input
        type="checkbox"
        data-testid="propagate-residuals-toggle"
        className="h-4 w-4 rounded border-gray-300 text-rose-600 focus:ring-rose-500"
        checked={checked}
        disabled={disabled}
        onChange={(e) => onChange(e.target.checked)}
      />
      <span className="font-medium">{PROPAGATE_RESIDUALS_LABEL}</span>
    </label>
  );
}

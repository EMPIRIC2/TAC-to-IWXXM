/**
 * Opt-in fold of decode leftovers into remarks / human-readable text (convert flag).
 */

/** Operator-visible label (scanned by TC-EV048 / TC-EV981-003). */
export const PROPAGATE_RESIDUALS_LABEL = 'Keep leftover TAC in remarks';

/** Operator-visible help under the toggle. */
export const PROPAGATE_RESIDUALS_HELP =
  'When on, undecoded TAC leftovers are kept in remarks or human-readable text for profiles that support that. International (annex3) has no remarks field in IWXXM — leftovers stay diagnostic-only.';

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
 */
export function PropagateResidualsControl({
  checked,
  onChange,
  disabled = false,
}: PropagateResidualsControlProps) {
  return (
    <label className="mb-4 flex cursor-pointer items-start gap-2 text-sm text-gray-800 dark:text-gray-200">
      <input
        type="checkbox"
        data-testid="propagate-residuals-toggle"
        className="mt-0.5 h-4 w-4 rounded border-gray-300 text-rose-600 focus:ring-rose-500"
        checked={checked}
        disabled={disabled}
        onChange={(e) => onChange(e.target.checked)}
      />
      <span>
        <span className="font-medium">{PROPAGATE_RESIDUALS_LABEL}</span>
        <span className="block text-xs text-gray-500 dark:text-gray-400">
          {PROPAGATE_RESIDUALS_HELP}
        </span>
      </span>
    </label>
  );
}

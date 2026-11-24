/**
 * Soft-preview checkbox for convert ``preview=true``.
 *
 * FR-043 / DI-007 / M1: operator soft-preview UX off by default.
 *
 * [Corpus: fr] epic #1688
 */
import { softPreviewUiConfig } from '@/utils/softPreviewUi';

/** Operator-visible label (scanned by TC-EV048-003). */
export const SOFT_PREVIEW_LABEL = 'Soft-preview';

/** Operator-visible help under the soft-preview toggle (scanned by TC-EV048-003). */
export const SOFT_PREVIEW_HELP =
  'Best-effort IWXXM when the report is incomplete. Not for publishing.';

/**
 * Type `SoftPreviewControlProps`.
 * @example
 * const _ = true;
 */
export interface SoftPreviewControlProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  disabled?: boolean;
}

/**
 * Toggle soft-preview mode on convert requests when enabled.
 */
export function SoftPreviewControl({
  checked,
  onChange,
  disabled = false,
}: SoftPreviewControlProps) {
  if (!softPreviewUiConfig.enabled) {
    return null;
  }
  return (
    <label className="mb-0 flex cursor-pointer items-start gap-2 text-sm text-gray-800 dark:text-gray-200">
      <input
        type="checkbox"
        data-testid="soft-preview-toggle"
        className="mt-0.5 h-4 w-4 rounded border-gray-300 text-rose-600 focus:ring-rose-500 disabled:cursor-not-allowed"
        checked={checked}
        disabled={disabled}
        readOnly={false}
        onChange={(e) => onChange(e.target.checked)}
      />
      <span className="min-w-0">
        <span className="font-medium">{SOFT_PREVIEW_LABEL}</span>
        <span
          className="mt-0.5 block text-xs leading-snug text-gray-500 dark:text-gray-400"
          title={SOFT_PREVIEW_HELP}
        >
          {SOFT_PREVIEW_HELP}
        </span>
      </span>
    </label>
  );
}

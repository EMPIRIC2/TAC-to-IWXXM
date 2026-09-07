/**
 * First-visit privacy notice (F22 / UJ-033 / Solution A).
 *
 * Short disclosure of IndexedDB work history + preference storage; equal-weight
 * dismiss vs open settings (no dark patterns).
 */

import { Button } from './ui/button';

export interface PrivacyNoticeProps {
  open: boolean;
  onDismiss: () => void;
  onOpenSettings: () => void;
}

/**
 * First-visit privacy notice with dismiss and open-settings actions.
 *
 * Renders nothing when `open` is false.
 */
export function PrivacyNotice({ open, onDismiss, onOpenSettings }: PrivacyNoticeProps) {
  if (!open) {
    return null;
  }

  return (
    <div
      role="region"
      aria-label="Privacy notice"
      data-testid="privacy-notice"
      className="mb-6 rounded-lg border border-gray-200 bg-white p-4 text-left shadow-sm dark:border-gray-700 dark:bg-gray-800"
    >
      <p className="text-sm text-gray-700 dark:text-gray-200">
        Guest work history may be stored in this browser (IndexedDB) when enabled in
        Privacy settings; preferences use local storage. Signing in may set Auth session
        cookies for long-term server storage. Nothing is sold or shared for advertising.
      </p>
      <div className="mt-3 flex flex-wrap gap-2">
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={onDismiss}
          aria-label="Dismiss privacy notice"
        >
          Got it
        </Button>
        <Button
          type="button"
          variant="default"
          size="sm"
          onClick={onOpenSettings}
          aria-label="Open privacy settings from notice"
        >
          Privacy settings
        </Button>
      </div>
    </div>
  );
}

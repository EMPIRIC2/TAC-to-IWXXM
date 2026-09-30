/**
 * Dismiss handler for the terms dialog.
 * @example
 * const _ = true;
 */

/**
 * Close only when the dialog is being dismissed.
 * @example
 * const _ = true;
 */
export function dismissSiteTerms(open: boolean, onClose: () => void): void {
  if (!open) {
    onClose();
  }
}

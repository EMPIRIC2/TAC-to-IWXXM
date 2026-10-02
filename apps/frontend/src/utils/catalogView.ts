/**
 * Compact or detailed rules-catalog layout for this browser tab.
 */

export const CATALOG_VIEW_STORAGE_KEY = 'tac-to-iwxxm.rules-catalog.view';

/**
 * Type `CatalogView`.
 * @example
 * const _ = true;
 */
export type CatalogView = 'detailed' | 'compact';

/**
 * Keep a stored view. Anything else is detailed.
 *
 * @param raw - Session value
 * @returns Compact or detailed
 * @example
 * const _ = true;
 */
export function parseCatalogView(raw: string | null | undefined): CatalogView {
  return raw === 'compact' ? 'compact' : 'detailed';
}

/**
 * Read the catalog view saved for this tab.
 *
 * @returns Stored view, or detailed when nothing is saved
 * @example
 * const _ = true;
 */
export function readCatalogView(): CatalogView {
  if (typeof window === 'undefined' || !window.sessionStorage) {
    return 'detailed';
  }
  try {
    return parseCatalogView(window.sessionStorage.getItem(CATALOG_VIEW_STORAGE_KEY));
  } catch {
    return 'detailed';
  }
}

/**
 * Remember the catalog view for this tab.
 *
 * @param view - Compact or detailed
 * @example
 * const _ = true;
 */
export function writeCatalogView(view: CatalogView): void {
  if (typeof window === 'undefined' || !window.sessionStorage) {
    return;
  }
  try {
    window.sessionStorage.setItem(CATALOG_VIEW_STORAGE_KEY, view);
  } catch {
    // Private mode: keep the choice on screen for this visit only.
  }
}

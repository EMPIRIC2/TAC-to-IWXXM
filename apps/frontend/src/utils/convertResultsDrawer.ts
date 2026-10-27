/**
 * Convert results drawer tab model (UJ-089 / EV-convert-declutter-drawer).
 *
 * [Corpus: product §F7] [Corpus: journeys §UJ-089]
 */

/**
 * Tab ids for the Convert results drawer.
 * @example
 * const _ = true;
 */
export type ConvertResultsTab = 'iwxxm' | 'console' | 'decoder' | 'map' | 'downloads';

/** Ordered drawer tabs shown to operators. */
export const CONVERT_RESULTS_TABS: readonly {
  id: ConvertResultsTab;
  label: string;
}[] = [
  { id: 'iwxxm', label: 'IWXXM' },
  { id: 'console', label: 'Console' },
  { id: 'decoder', label: 'Decoder' },
  { id: 'map', label: 'Map' },
  { id: 'downloads', label: 'Downloads' },
] as const;

/**
 * Tab to select when convert succeeds (auto-open).
 *
 * @returns IWXXM tab id
 * @example
 * const _ = true;
 */
export function defaultTabAfterConvert(): ConvertResultsTab {
  return 'iwxxm';
}

/**
 * Whether the results drawer should open after a successful convert.
 *
 * @param hasConverted - True when the convert queue is non-empty
 * @param wasEmpty - True when the queue was empty before this update
 * @returns Whether to force-open the drawer on IWXXM
 * @example
 * const _ = true;
 */
export function shouldAutoOpenResultsDrawer(
  hasConverted: boolean,
  wasEmpty: boolean,
): boolean {
  return hasConverted && wasEmpty;
}

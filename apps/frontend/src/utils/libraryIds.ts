/**
 * Default first-party library asset ids (EV-bridge five Libraries).
 */

import type { LibraryAssetKind } from './conversionProfilesApi';

/**
 * Build the canonical first-party library id for a kind × national line.
 *
 * @param kind - Library kind
 * @param nationalLine - Engine / national line id (e.g. ICAO_2025)
 */
export function defaultLibraryId(
  kind: LibraryAssetKind,
  nationalLine = 'ICAO_2025',
): string {
  return `LIB.${kind.toUpperCase()}.${nationalLine}`;
}

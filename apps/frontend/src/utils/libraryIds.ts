/**
 * Default first-party library asset ids (EV-bridge five Libraries).
 */

import type { LibraryAssetKind } from './conversionProfilesApi';
import { coerceIwxxmProfile } from './semanticProfile';

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

const ALIAS_TO_NATIONAL: Record<string, string> = {
  annex3: 'ICAO_2025',
  iwxxm_us: 'US_FAA_NWS',
};

/**
 * Map a legacy profile / wire id to a Conversion library asset id.
 *
 * @param profile - UI or wire profile (canonical or annex3 / iwxxm_us)
 */
export function conversionLibraryIdFromProfile(profile: string | undefined): string {
  const coerced = coerceIwxxmProfile(profile);
  const national =
    ALIAS_TO_NATIONAL[coerced] ?? coerced.toUpperCase().replace(/-/g, '_');
  return defaultLibraryId('conversion', national);
}

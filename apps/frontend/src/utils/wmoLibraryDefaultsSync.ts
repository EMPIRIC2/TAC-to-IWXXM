/**
 * Shared WMO / ICAO library defaults between Profile builder and Convert.
 */

import { libraryIdsForNationalLine } from './libraryIds';
import { DEFAULT_SEMANTIC_PROFILE } from './semanticProfile';

export const WMO_LIBRARY_DEFAULTS_SYNC_KEY = 'tac_wmo_library_defaults_sync';

/** Same-tab notify (StorageEvent only fires across tabs). */
export const WMO_LIBRARY_DEFAULTS_SYNC_EVENT = 'tac-wmo-library-defaults-sync';

export interface WmoLibraryDefaultsSync {
  profile: string;
  libraryIds: {
    conversionLibraryId: string;
    tacValidationLibraryId: string;
    iwxxmValidationLibraryId: string;
    disseminationLibraryId: string;
    decodingLibraryId: string;
  };
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function parseLibraryIds(raw: unknown): WmoLibraryDefaultsSync['libraryIds'] | null {
  if (!isRecord(raw)) {
    return null;
  }
  const keys = [
    'conversionLibraryId',
    'tacValidationLibraryId',
    'iwxxmValidationLibraryId',
    'disseminationLibraryId',
    'decodingLibraryId',
  ] as const;
  const out: Partial<WmoLibraryDefaultsSync['libraryIds']> = {};
  for (const key of keys) {
    const value = raw[key];
    if (typeof value !== 'string' || !value.trim()) {
      return null;
    }
    out[key] = value.trim();
  }
  return out as WmoLibraryDefaultsSync['libraryIds'];
}

/**
 * Canonical ICAO / WMO default profile and five library ids.
 */
export function defaultWmoLibraryDefaultsSync(): WmoLibraryDefaultsSync {
  return {
    profile: DEFAULT_SEMANTIC_PROFILE,
    libraryIds: libraryIdsForNationalLine(DEFAULT_SEMANTIC_PROFILE),
  };
}

/**
 * Read shared WMO defaults from localStorage.
 */
export function readWmoLibraryDefaultsSync(): WmoLibraryDefaultsSync | null {
  try {
    const raw = localStorage.getItem(WMO_LIBRARY_DEFAULTS_SYNC_KEY);
    if (!raw) {
      return null;
    }
    const parsed = JSON.parse(raw) as unknown;
    if (!isRecord(parsed)) {
      return null;
    }
    const profile = parsed.profile;
    const libraryIds = parseLibraryIds(parsed.libraryIds);
    if (typeof profile !== 'string' || !profile.trim() || !libraryIds) {
      return null;
    }
    return { profile: profile.trim(), libraryIds };
  } catch {
    return null;
  }
}

/**
 * Persist shared WMO defaults to localStorage.
 *
 * @param prefs - Profile id and five library ids to share with Convert.
 */
export function writeWmoLibraryDefaultsSync(prefs: WmoLibraryDefaultsSync): void {
  try {
    localStorage.setItem(WMO_LIBRARY_DEFAULTS_SYNC_KEY, JSON.stringify(prefs));
  } catch {
    // localStorage may be unavailable in private mode
  }
  if (typeof window !== 'undefined') {
    window.dispatchEvent(
      new CustomEvent(WMO_LIBRARY_DEFAULTS_SYNC_EVENT, { detail: prefs }),
    );
  }
}

/**
 * Reset shared prefs to ICAO / WMO defaults and persist them.
 */
export function resetWmoLibraryDefaultsSync(): WmoLibraryDefaultsSync {
  const defaults = defaultWmoLibraryDefaultsSync();
  writeWmoLibraryDefaultsSync(defaults);
  return defaults;
}

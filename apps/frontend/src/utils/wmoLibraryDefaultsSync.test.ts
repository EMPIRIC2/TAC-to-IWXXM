/**
 * wmoLibraryDefaultsSync util tests (TC-EVPYL-003).
 */

import { afterEach, describe, expect, it } from 'vitest';

import {
  WMO_LIBRARY_DEFAULTS_SYNC_EVENT,
  WMO_LIBRARY_DEFAULTS_SYNC_KEY,
  defaultWmoLibraryDefaultsSync,
  readWmoLibraryDefaultsSync,
  resetWmoLibraryDefaultsSync,
  writeWmoLibraryDefaultsSync,
} from './wmoLibraryDefaultsSync';

describe('wmoLibraryDefaultsSync', () => {
  afterEach(() => {
    localStorage.removeItem(WMO_LIBRARY_DEFAULTS_SYNC_KEY);
  });

  it('returns ICAO_2025 library ids from default and reset helpers', () => {
    const defaults = defaultWmoLibraryDefaultsSync();
    expect(defaults.profile).toBe('ICAO_2025');
    expect(defaults.libraryIds).toEqual({
      conversionLibraryId: 'LIB.CONVERSION.ICAO_2025',
      tacValidationLibraryId: 'LIB.TAC_VALIDATION.ICAO_2025',
      iwxxmValidationLibraryId: 'LIB.IWXXM_VALIDATION.ICAO_2025',
      disseminationLibraryId: 'LIB.DISSEMINATION.ICAO_2025',
      decodingLibraryId: 'LIB.DECODING.ICAO_2025',
    });

    const reset = resetWmoLibraryDefaultsSync();
    expect(reset).toEqual(defaults);
    expect(readWmoLibraryDefaultsSync()).toEqual(defaults);
  });

  it('round-trips prefs through localStorage', () => {
    const prefs = {
      profile: 'US_FAA_NWS',
      libraryIds: {
        conversionLibraryId: 'LIB.CONVERSION.US_FAA_NWS',
        tacValidationLibraryId: 'LIB.TAC_VALIDATION.US_FAA_NWS',
        iwxxmValidationLibraryId: 'LIB.IWXXM_VALIDATION.US_FAA_NWS',
        disseminationLibraryId: 'LIB.DISSEMINATION.US_FAA_NWS',
        decodingLibraryId: 'LIB.DECODING.US_FAA_NWS',
      },
    };
    writeWmoLibraryDefaultsSync(prefs);
    expect(readWmoLibraryDefaultsSync()).toEqual(prefs);
  });

  it('dispatches same-tab sync event on write', () => {
    const seen: unknown[] = [];
    const handler = (event: Event) => {
      seen.push((event as CustomEvent).detail);
    };
    window.addEventListener(WMO_LIBRARY_DEFAULTS_SYNC_EVENT, handler);
    const prefs = defaultWmoLibraryDefaultsSync();
    writeWmoLibraryDefaultsSync(prefs);
    window.removeEventListener(WMO_LIBRARY_DEFAULTS_SYNC_EVENT, handler);
    expect(seen).toEqual([prefs]);
  });
});

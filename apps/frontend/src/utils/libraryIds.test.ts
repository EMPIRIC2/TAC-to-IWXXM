/**
 * libraryIds helper tests.
 */

import { describe, expect, it } from 'vitest';

import { defaultLibraryId, libraryIdsForNationalLine } from './libraryIds';

describe('libraryIdsForNationalLine', () => {
  it('maps a national line to five library ids', () => {
    expect(libraryIdsForNationalLine('US_FAA_NWS')).toEqual({
      conversionLibraryId: defaultLibraryId('conversion', 'US_FAA_NWS'),
      tacValidationLibraryId: defaultLibraryId('tac_validation', 'US_FAA_NWS'),
      iwxxmValidationLibraryId: defaultLibraryId('iwxxm_validation', 'US_FAA_NWS'),
      disseminationLibraryId: defaultLibraryId('dissemination', 'US_FAA_NWS'),
      decodingLibraryId: defaultLibraryId('decoding', 'US_FAA_NWS'),
    });
  });

  it('falls back to ICAO_2025 for blank national lines', () => {
    expect(libraryIdsForNationalLine('')).toEqual(
      libraryIdsForNationalLine('ICAO_2025'),
    );
    expect(libraryIdsForNationalLine('   ')).toEqual(
      libraryIdsForNationalLine('ICAO_2025'),
    );
  });
});

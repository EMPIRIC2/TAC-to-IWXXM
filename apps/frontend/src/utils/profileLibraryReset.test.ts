/**
 * Tests for profileLibraryReset (TC-EVYCL-004 / #1251 T3.1).
 *
 * FR-019 / M1: product ship list is ICAO-only; helpers still accept line ids.
 */

import { describe, expect, it, vi } from 'vitest';
import { defaultLibraryId } from './libraryIds';
import {
  confirmLibraryResetForProfile,
  countryPresetLineForLibraries,
  isSemanticProfileLineChange,
  libraryIdsFromSessionParams,
  libraryResetForProfile,
} from './profileLibraryReset';

describe('profileLibraryReset', () => {
  it('detects national line changes', () => {
    // FR-019 / M1: dropped nationals coerce to ICAO_2025, so this is not a line change.
    expect(isSemanticProfileLineChange('ICAO_2025', 'US_FAA_NWS')).toBe(false);
    expect(isSemanticProfileLineChange('ICAO_2025', 'ICAO_2025')).toBe(false);
    expect(isSemanticProfileLineChange('US_FAA_NWS', 'us_faa_nws')).toBe(false);
    // Legacy annex3 alias stays distinct from canonical ICAO_2025 in the select.
    expect(isSemanticProfileLineChange('annex3', 'ICAO_2025')).toBe(true);
  });

  it('builds library ids for the target profile', () => {
    const { profile, libraryIds } = libraryResetForProfile('ICAO_2025');
    expect(profile).toBe('ICAO_2025');
    expect(libraryIds.conversionLibraryId).toBe(
      defaultLibraryId('conversion', 'ICAO_2025'),
    );
    expect(libraryIds.decodingLibraryId).toBe(
      defaultLibraryId('decoding', 'ICAO_2025'),
    );
    expect(libraryIds.tacValidationLibraryId).toBe(
      defaultLibraryId('tac_validation', 'ICAO_2025'),
    );
    expect(libraryIds.iwxxmValidationLibraryId).toBe(
      defaultLibraryId('iwxxm_validation', 'ICAO_2025'),
    );
  });

  it('reads camelCase and snake_case library ids from session params', () => {
    expect(
      libraryIdsFromSessionParams({
        conversionLibraryId: ' LIB.CONVERSION.ICAO_2025 ',
        tac_validation_library_id: 'LIB.TAC_VALIDATION.ICAO_2025',
        decodingLibraryId: '   ',
        iwxxmValidationLibraryId: 12,
      }),
    ).toEqual({
      conversionLibraryId: 'LIB.CONVERSION.ICAO_2025',
      tacValidationLibraryId: 'LIB.TAC_VALIDATION.ICAO_2025',
    });
  });

  it('matches a country preset only when the four libraries agree', () => {
    const icao = libraryResetForProfile('ICAO_2025').libraryIds;
    expect(countryPresetLineForLibraries(icao)).toBe('ICAO_2025');
    expect(
      countryPresetLineForLibraries({
        ...icao,
        tacValidationLibraryId: defaultLibraryId('tac_validation', 'CA_ECCC'),
      }),
    ).toBe('');
    expect(
      countryPresetLineForLibraries({
        conversionLibraryId: 'LIB.CONVERSION.AU_BOM',
        tacValidationLibraryId: 'LIB.TAC_VALIDATION.AU_BOM',
        iwxxmValidationLibraryId: 'LIB.IWXXM_VALIDATION.AU_BOM',
        decodingLibraryId: 'LIB.DECODING.AU_BOM',
      }),
    ).toBe('');
  });

  it('confirm helper uses injectable confirm', () => {
    const confirmFn = vi.fn().mockReturnValue(true);
    expect(confirmLibraryResetForProfile('ICAO_2025', confirmFn)).toBe(true);
    expect(confirmFn).toHaveBeenCalledWith(expect.stringContaining('ICAO_2025'));
    expect(confirmFn.mock.calls[0]![0]).toMatch(/reset/i);
    expect(confirmFn.mock.calls[0]![0]).not.toMatch(/ADR|Corpus|EV-|TC-/i);
  });

  it('confirm helper defaults to window.confirm', () => {
    const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(false);
    try {
      expect(confirmLibraryResetForProfile('ICAO_2025')).toBe(false);
      expect(confirmSpy).toHaveBeenCalledWith(expect.stringContaining('ICAO_2025'));
    } finally {
      confirmSpy.mockRestore();
    }
  });
});

/**
 * Tests for profileLibraryReset (TC-EVYCL-004 / #1251 T3.1).
 */

import { describe, expect, it, vi } from 'vitest';
import { defaultLibraryId } from './libraryIds';
import {
  confirmLibraryResetForProfile,
  isSemanticProfileLineChange,
  libraryResetForProfile,
} from './profileLibraryReset';

describe('profileLibraryReset', () => {
  it('detects national line changes', () => {
    expect(isSemanticProfileLineChange('ICAO_2025', 'US_FAA_NWS')).toBe(true);
    expect(isSemanticProfileLineChange('ICAO_2025', 'ICAO_2025')).toBe(false);
    expect(isSemanticProfileLineChange('US_FAA_NWS', 'us_faa_nws')).toBe(false);
  });

  it('builds library ids for the target profile', () => {
    const { profile, libraryIds } = libraryResetForProfile('US_FAA_NWS');
    expect(profile).toBe('US_FAA_NWS');
    expect(libraryIds.conversionLibraryId).toBe(
      defaultLibraryId('conversion', 'US_FAA_NWS'),
    );
    expect(libraryIds.decodingLibraryId).toBe(
      defaultLibraryId('decoding', 'US_FAA_NWS'),
    );
    expect(libraryIds.tacValidationLibraryId).toBe(
      defaultLibraryId('tac_validation', 'US_FAA_NWS'),
    );
    expect(libraryIds.iwxxmValidationLibraryId).toBe(
      defaultLibraryId('iwxxm_validation', 'US_FAA_NWS'),
    );
  });

  it('confirm helper uses injectable confirm', () => {
    const confirmFn = vi.fn().mockReturnValue(true);
    expect(confirmLibraryResetForProfile('CA_ECCC', confirmFn)).toBe(true);
    expect(confirmFn).toHaveBeenCalledWith(expect.stringContaining('CA_ECCC'));
    expect(confirmFn.mock.calls[0]![0]).toMatch(/reset/i);
    expect(confirmFn.mock.calls[0]![0]).not.toMatch(/ADR|Corpus|EV-|TC-/i);
  });
});

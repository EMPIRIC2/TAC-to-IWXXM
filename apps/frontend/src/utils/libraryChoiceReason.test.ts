import { describe, expect, it } from 'vitest';
import {
  libraryChoiceReason,
  libraryDisplayName,
  libraryLine,
} from './libraryChoiceReason';

describe('libraryChoiceReason', () => {
  it('reads a national line from a library id', () => {
    expect(libraryLine(' LIB.DECODING.ICAO_2025 ')).toBe('ICAO_2025');
    expect(libraryLine('LIB.CONVERSION.US.FAA')).toBe('US.FAA');
    expect(libraryLine('custom-asset')).toBeNull();
    expect(libraryLine('LIB.DECODING.')).toBeNull();
    expect(libraryLine('LIB.DECODING')).toBeNull();
    expect(libraryLine('  ')).toBeNull();
  });

  it('uses the country name for a known library and keeps a custom label', () => {
    expect(libraryDisplayName('LIB.DECODING.US_FAA_NWS')).toBe(
      'United States (FAA/NWS)',
    );
    expect(libraryDisplayName('LIB.TAC_VALIDATION.icao_2025')).toBe(
      'ICAO / WMO Annex 3 (2025)',
    );
    expect(libraryDisplayName('LIB.CONVERSION.CA_ECCC', 'ignored')).toBe(
      'Canada (ECCC)',
    );
    expect(libraryDisplayName('custom-asset', ' My overlay ')).toBe('My overlay');
    expect(libraryDisplayName('LIB.DECODING.NOT_A_LINE', '  ')).toBe(
      'LIB.DECODING.NOT_A_LINE',
    );
    expect(libraryDisplayName('custom-asset')).toBe('custom-asset');
  });

  it('explains the WMO baseline, a national line, and a custom library', () => {
    expect(libraryChoiceReason('')).toBe(
      'WMO baseline. Choose another line when the report is national.',
    );
    expect(libraryChoiceReason('   ')).toBe(
      'WMO baseline. Choose another line when the report is national.',
    );
    expect(libraryChoiceReason('LIB.DECODING.icao_2025')).toBe(
      'WMO baseline. Choose another line when the report is national.',
    );
    expect(libraryChoiceReason('custom-asset')).toBe(
      'Custom library for this conversion.',
    );
    expect(libraryChoiceReason('LIB.TAC_VALIDATION.')).toBe(
      'Custom library for this conversion.',
    );
    expect(libraryChoiceReason('LIB.CONVERSION.US_FAA_NWS')).toBe(
      'National line for this conversion. Reset to WMO defaults to use the baseline.',
    );
  });
});

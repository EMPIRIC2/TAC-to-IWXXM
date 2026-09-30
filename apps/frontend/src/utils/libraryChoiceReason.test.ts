import { describe, expect, it } from 'vitest';
import { libraryChoiceReason, libraryLine } from './libraryChoiceReason';

describe('libraryChoiceReason', () => {
  it('reads a national line from a library id', () => {
    expect(libraryLine(' LIB.DECODING.ICAO_2025 ')).toBe('ICAO_2025');
    expect(libraryLine('LIB.CONVERSION.US.FAA')).toBe('US.FAA');
    expect(libraryLine('custom-asset')).toBeNull();
    expect(libraryLine('LIB.DECODING.')).toBeNull();
    expect(libraryLine('LIB.DECODING')).toBeNull();
    expect(libraryLine('  ')).toBeNull();
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

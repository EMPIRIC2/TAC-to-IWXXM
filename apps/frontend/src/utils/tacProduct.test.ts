/**
 * Unit tests for F6.e TAC product auto-detect helpers.
 */
import { describe, expect, it } from 'vitest';
import { detectTacProduct, resolveConvertProduct } from './tacProduct';

describe('detectTacProduct', () => {
  it('detects SPECI before METAR default', () => {
    expect(detectTacProduct('SPECI KJFK 122045Z 18012KT 5SM 15/07 A3005=')).toBe(
      'SPECI',
    );
  });

  it('detects SPECI in a METAR+SPECI bulletin neighbor (R7 / TC-F15-005)', () => {
    const bulletin =
      'METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005=\n' +
      'SPECI KJFK 232045Z 18012KT 5SM BKN015 15/07 A3005=\n';
    // First keyword wins for whole-string detect; callers split reports for per-line identity.
    expect(detectTacProduct(bulletin)).toBe('METAR');
    expect(detectTacProduct(bulletin.split('\n')[1]!)).toBe('SPECI');
  });

  it('detects TAF', () => {
    expect(
      detectTacProduct('TAF KJFK 121730Z 1218/1324 24012KT P6SM SCT040 BKN080'),
    ).toBe('TAF');
  });

  it('defaults to METAR when no keyword', () => {
    expect(detectTacProduct('KJFK 121851Z 24008KT 10SM FEW250')).toBe('METAR');
  });
});

describe('resolveConvertProduct', () => {
  it('uses auto-detect when selection is auto', () => {
    expect(resolveConvertProduct('auto', 'SPECI KJFK 122045Z 18012KT 5SM=')).toBe(
      'SPECI',
    );
  });

  it('keeps explicit selection', () => {
    expect(resolveConvertProduct('TAF', 'METAR KJFK 121851Z 24008KT 10SM=')).toBe(
      'TAF',
    );
  });
});

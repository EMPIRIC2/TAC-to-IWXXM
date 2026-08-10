/**
 * Unit tests for F6.e TAC product auto-detect helpers.
 */
import { describe, expect, it } from 'vitest';
import {
  detectTacProduct,
  resolveConvertProduct,
  splitManualEntries,
} from './tacProduct';

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

  it('maps VOLCANIC ASH advisory phrasing to VAA', () => {
    expect(
      detectTacProduct('VOLCANIC ASH ADVISORY\nDTG: 20240923/0130Z\nVAAC: TOKYO\n'),
    ).toBe('VAA');
  });

  it('maps TROPICAL CYCLONE advisory phrasing to TCA', () => {
    expect(detectTacProduct('TROPICAL CYCLONE ADVISORY\nDTG: 20040925/1900Z\n')).toBe(
      'TCA',
    );
  });

  it('honors an explicit defaultProduct when no keyword matches', () => {
    expect(detectTacProduct('KJFK 121851Z 24008KT 10SM FEW250', 'TAF')).toBe('TAF');
  });

  it('falls back to defaultProduct when a matched token is not in TAC_PRODUCTS', () => {
    const includesSpy = vi.spyOn(Array.prototype, 'includes').mockReturnValue(false);
    try {
      expect(detectTacProduct('METAR KJFK 121851Z 24008KT 10SM FEW250', 'TAF')).toBe(
        'TAF',
      );
    } finally {
      includesSpy.mockRestore();
    }
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

describe('splitManualEntries', () => {
  it('splits METAR-style products one entry per non-empty line', () => {
    expect(splitManualEntries('METAR A\n\n METAR B ', 'METAR')).toEqual([
      'METAR A',
      'METAR B',
    ]);
  });

  it('keeps SIGMET multi-line report as a single document', () => {
    const sigmet =
      'YUDD SIGMET 2 VALID 101200/101600 YUSO-\n' +
      'YUDD SHANLON FIR/UIR OBSC TS FCST S OF N54 AND E OF W012 TOP FL390 MOV E 20KT WKN=\n';
    expect(splitManualEntries(sigmet, 'SIGMET')).toEqual([sigmet.trim()]);
  });

  it('keeps AIRMET multi-line report as a single document', () => {
    const airmet =
      'YUDD AIRMET 1 VALID 101200/101600 YUSO-\n' +
      'YUDD SHANLON FIR/UIR ISOL TS FCST N OF S50 TOP FL350 MOV E 20KT WKN=\n';
    expect(splitManualEntries(airmet, 'AIRMET')).toEqual([airmet.trim()]);
  });

  it('keeps VAA multi-line advisory as a single document', () => {
    const vaa = 'VA ADVISORY\nDTG: 20240923/0130Z\nVAAC: TOKYO\n';
    expect(splitManualEntries(vaa, 'VAA')).toEqual([vaa.trim()]);
  });

  it('keeps TCA multi-line advisory as a single document', () => {
    const tca = 'TC ADVISORY\nDTG: 20040925/1900Z\nMAX WIND: 22MPS\n';
    expect(splitManualEntries(tca, 'TCA')).toEqual([tca.trim()]);
  });

  it('detects SWXA from SWX ADVISORY', () => {
    expect(detectTacProduct('SWX ADVISORY\nDTG: 20201108/0100Z\nSWXC: DONLON\n')).toBe(
      'SWXA',
    );
  });

  it('detects VONA from VONA header', () => {
    expect(
      detectTacProduct('VONA\nDTG: 20240216/0130Z\nVOLCANO: KARYMSKY 300130\n'),
    ).toBe('VONA');
  });

  it('keeps VONA multi-line notice as a single document', () => {
    const vona = 'VONA\nDTG: 20240216/0130Z\nVOLCANO: KARYMSKY 300130\n';
    expect(splitManualEntries(vona, 'VONA')).toEqual([vona.trim()]);
  });

  it('keeps SWXA multi-line advisory as a single document', () => {
    const swxa = 'SWX ADVISORY\nDTG: 20201108/0100Z\nSWXC: DONLON\n';
    expect(splitManualEntries(swxa, 'SWXA')).toEqual([swxa.trim()]);
  });
});

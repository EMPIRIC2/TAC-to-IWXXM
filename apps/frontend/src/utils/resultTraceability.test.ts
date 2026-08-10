import { describe, expect, it } from 'vitest';
import {
  deriveTacDisplayTitle,
  parseTacHeadline,
  resolveOriginalTac,
  truncateTacSnippet,
} from './resultTraceability';

describe('resultTraceability', () => {
  it('parseTacHeadline extracts METAR station and time', () => {
    expect(
      parseTacHeadline('METAR KJFK 121251Z 18012KT 10SM FEW030 24/16 A2992'),
    ).toEqual({
      product: 'METAR',
      station: 'KJFK',
      time: '121251Z',
    });
  });

  it('defaults a product-less headline to METAR', () => {
    expect(parseTacHeadline('KJFK 121251Z 18012KT')).toEqual({
      product: 'METAR',
      station: 'KJFK',
      time: '121251Z',
    });
  });

  it('deriveTacDisplayTitle builds headline label', () => {
    const tac = 'METAR FAOR 101200Z COR 12012KT 9999 FEW020 22/14 Q1018';
    expect(deriveTacDisplayTitle(tac, 'manual_input.txt')).toBe('METAR FAOR 101200Z');
  });

  it('deriveTacDisplayTitle falls back to download name for unknown TAC', () => {
    expect(deriveTacDisplayTitle('', 'uploaded.metar')).toBe('uploaded.metar');
  });

  it('uses a compact unknown TAC as the display title', () => {
    expect(deriveTacDisplayTitle('  unusual   input  ', 'uploaded.metar')).toBe(
      'unusual input',
    );
  });

  it('truncateTacSnippet shortens long TAC', () => {
    const long = 'METAR ' + 'X'.repeat(100);
    expect(truncateTacSnippet(long, 20).endsWith('…')).toBe(true);
    expect(truncateTacSnippet(long, 20).length).toBe(20);
  });

  it('keeps snippets at or below the requested length', () => {
    expect(truncateTacSnippet('  METAR   KJFK  ', 20)).toBe('METAR KJFK');
  });

  it('resolveOriginalTac prefers API tac_input', () => {
    expect(resolveOriginalTac('METAR API', 'METAR MANUAL', 'METAR FILE')).toBe(
      'METAR API',
    );
  });

  it('resolveOriginalTac falls back to manual then file', () => {
    expect(resolveOriginalTac(undefined, 'METAR MANUAL', 'METAR FILE')).toBe(
      'METAR MANUAL',
    );
    expect(resolveOriginalTac('', '', 'METAR FILE')).toBe('METAR FILE');
    expect(resolveOriginalTac('  ', undefined, undefined)).toBe('');
    expect(resolveOriginalTac('', undefined, ' METAR FILE ')).toBe('METAR FILE');
  });
});

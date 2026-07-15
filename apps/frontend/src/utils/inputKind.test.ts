import { describe, expect, it } from 'vitest';
import {
  detectInputKind,
  kindToMode,
  looksLikeAhlBulletin,
  looksLikeCollectIwxxm,
} from './inputKind';

describe('inputKind', () => {
  it('detects AHL bulletin headers', () => {
    const text = 'SAUS31 KZNY 121200\nMETAR KJFK 121251Z 18004KT=\n';
    expect(looksLikeAhlBulletin(text)).toBe(true);
    expect(detectInputKind('bulletin.txt', text)).toBe('ahl_bulletin');
    expect(kindToMode('ahl_bulletin')).toBe('ahl_bulletin');
  });

  it('detects COLLECT IWXXM', () => {
    const xml =
      '<?xml version="1.0"?>\n<collect:MeteorologicalBulletin xmlns:collect="http://def.wmo.int/collect/1.2" xmlns:iwxxm="http://icao.int/iwxxm/3.0">';
    expect(looksLikeCollectIwxxm(xml)).toBe(true);
    expect(detectInputKind('metar-collect.xml', xml)).toBe('collect_iwxxm');
  });

  it('detects gzip by extension', () => {
    expect(detectInputKind('bulletin.tac.gz')).toBe('gzip');
    expect(kindToMode('gzip')).toBe('tac');
  });

  it('handles empty AHL text and xml unknowns', () => {
    expect(looksLikeAhlBulletin('')).toBe(false);
    expect(looksLikeAhlBulletin('   \n')).toBe(false);
    expect(detectInputKind('plain.txt', 'METAR KJFK')).toBe('tac');
    expect(detectInputKind('other.xml', '<root/>')).toBe('unknown');
    expect(detectInputKind('other.xml', '<iwxxm:METAR xmlns:iwxxm="x"/>')).toBe(
      'collect_iwxxm',
    );
    expect(kindToMode('unknown')).toBe('tac');
    expect(kindToMode('tac')).toBe('tac');
  });
});

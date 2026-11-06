/**
 * Region sketch and wind cue helpers (F7 / F9).
 */
import { describe, expect, it } from 'vitest';
import {
  regionBoxes,
  regionForStation,
  stationDisplayName,
  stationFromReport,
  windCueEmptyLabel,
  windCueFromSegments,
} from '@/utils/decodeVisuals';
import {
  publishDecodeVisuals,
  readDecodeVisuals,
  subscribeDecodeVisuals,
} from '@/utils/decodeVisualsStore';

describe('regionForStation', () => {
  it('returns a sketched region or nothing', () => {
    expect(regionForStation('kjfk')?.label).toBe('United States');
    expect(regionForStation('')).toBeNull();
    expect(regionForStation('QQQQ')).toBeNull();
    expect(regionBoxes().length).toBeGreaterThan(0);
  });
});

describe('stationDisplayName', () => {
  it('uses the catalog name when the station is known', () => {
    expect(stationDisplayName('')).toBe('');
    expect(stationDisplayName('kjfk')).toContain('Kennedy');
    expect(stationDisplayName('zzzz')).toBe('ZZZZ');
  });
});

describe('stationFromReport', () => {
  it('skips the product word and prefers a known station', () => {
    expect(stationFromReport('')).toBe('');
    expect(stationFromReport('METAR KJFK 121755Z')).toBe('KJFK');
    expect(stationFromReport('METAR ZZZZ 121755Z')).toBe('ZZZZ');
  });
});

describe('windCueFromSegments', () => {
  it('reads a numeric group, a named direction, variable wind, and skips an impossible direction', () => {
    expect(windCueFromSegments([])).toBeNull();
    expect(windCueEmptyLabel()).toContain('No wind');
    expect(
      windCueFromSegments([{ code: '18010KT', explanation: 'wind' }])?.degrees,
    ).toBe(180);
    expect(
      windCueFromSegments([{ code: '18010G20KT', explanation: '' }])?.label,
    ).toContain('180');
    expect(
      windCueFromSegments([{ code: 'VRB05KT', explanation: '' }])?.degrees,
    ).toBeNull();
    expect(
      windCueFromSegments([{ code: '180 deg', explanation: 'Mean wind direction' }])
        ?.degrees,
    ).toBe(180);
    expect(windCueFromSegments([{ code: '99910KT', explanation: '' }])).toBeNull();
    expect(
      windCueFromSegments([{ code: '999 deg', explanation: 'wind direction' }]),
    ).toBeNull();
    expect(windCueFromSegments([{ code: 'calm', explanation: 'wind' }])).toBeNull();
  });
});

describe('decodeVisualsStore', () => {
  it('publishes to subscribers and stops after unsubscribe', () => {
    const seen: string[] = [];
    const stop = subscribeDecodeVisuals(() => {
      seen.push(readDecodeVisuals().station);
    });
    publishDecodeVisuals({ station: 'KJFK', segments: [] });
    stop();
    publishDecodeVisuals({ station: 'EGLL', segments: [] });
    expect(seen).toEqual(['KJFK']);
    expect(readDecodeVisuals().station).toBe('EGLL');
    publishDecodeVisuals({ station: '', segments: [] });
  });
});

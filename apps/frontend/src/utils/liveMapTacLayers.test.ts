/**
 * TAC overlay layers + station cluster picker — success / failure / validation.
 */

import { describe, expect, it } from 'vitest';
import {
  isMultiStationCluster,
  passesTacLayers,
  stationClusterFilePicker,
  tacMatchesLayer,
} from '@/utils/liveMapTacLayers';

const METAR_RAIN =
  'METAR KJFK 231851Z 20015G25KT 3SM -RA BR BKN012 OVC025 12/11 A2998=';
const METAR_TS = 'METAR KORD 231955Z 27020G35KT 2SM TSRA BKN025CB 18/16 A2985=';
const METAR_CLEAR = 'METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005=';

describe('liveMapTacLayers success', () => {
  it('matches precip, temp, wind, thunder, and ice tokens', () => {
    expect(tacMatchesLayer(METAR_RAIN, 'precip')).toBe(true);
    expect(tacMatchesLayer(METAR_RAIN, 'temp')).toBe(true);
    expect(tacMatchesLayer(METAR_RAIN, 'wind')).toBe(true);
    expect(tacMatchesLayer(METAR_TS, 'thunder')).toBe(true);
    expect(
      tacMatchesLayer('METAR KJFK 231751Z 00000KT 1/2SM IC 15/07 A3005=', 'ice'),
    ).toBe(true);
  });

  it('keeps TAC that hits a selected overlay', () => {
    expect(passesTacLayers(METAR_RAIN, new Set(['precip']))).toBe(true);
    expect(passesTacLayers(METAR_TS, new Set(['thunder']))).toBe(true);
  });

  it('builds station cluster file picker rows', () => {
    const items = stationClusterFilePicker([
      {
        icao: 'KJFK',
        product: 'metar',
        tac: METAR_RAIN,
        observedAt: '2026-11-13T18:00:00Z',
      },
      {
        icao: 'KJFK',
        product: 'speci',
        tac: METAR_CLEAR,
        observedAt: '2026-11-13T17:00:00Z',
      },
    ]);
    expect(items).toHaveLength(2);
    expect(items[0]?.icao).toBe('KJFK');
    expect(isMultiStationCluster(2, 1)).toBe(true);
  });
});

describe('liveMapTacLayers failure', () => {
  it('rejects clear METAR when precip overlay is on', () => {
    expect(passesTacLayers(METAR_CLEAR, new Set(['precip']))).toBe(false);
  });

  it('rejects unknown overlay tokens', () => {
    expect(tacMatchesLayer(METAR_CLEAR, 'precip')).toBe(false);
    expect(tacMatchesLayer(METAR_CLEAR, 'thunder')).toBe(false);
  });

  it('does not open a picker for a single-report station', () => {
    expect(isMultiStationCluster(1, 1)).toBe(false);
  });
});

describe('liveMapTacLayers validation', () => {
  it('empty overlay set keeps every TAC', () => {
    expect(passesTacLayers(METAR_CLEAR, new Set())).toBe(true);
  });

  it('skips blank TAC rows in the cluster picker', () => {
    const items = stationClusterFilePicker([
      {
        icao: 'KJFK',
        product: 'metar',
        tac: '   ',
        observedAt: '2026-11-13T18:00:00Z',
      },
      {
        icao: 'KJFK',
        product: 'metar',
        tac: METAR_CLEAR,
        observedAt: '2026-11-13T17:00:00Z',
      },
    ]);
    expect(items).toHaveLength(1);
    expect(items[0]?.tac).toBe(METAR_CLEAR);
  });

  it('returns false for an unknown overlay id cast', () => {
    expect(
      tacMatchesLayer(METAR_RAIN, 'unknown' as Parameters<typeof tacMatchesLayer>[1]),
    ).toBe(false);
  });

  it('treats blank TAC as no tokens', () => {
    expect(tacMatchesLayer('', 'precip')).toBe(false);
    expect(tacMatchesLayer('   ', 'wind')).toBe(false);
    expect(tacMatchesLayer('---', 'precip')).toBe(false);
  });
});

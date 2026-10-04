/**
 * Live map query, wind text, and IWXXM request.
 */
import { afterEach, describe, expect, it, vi } from 'vitest';
import {
  boundsOf,
  fetchLivePlaces,
  iwxxmForReport,
  layerQuery,
  selectedLayerQuery,
  viewById,
  windFromTac,
} from './liveMap';

const bounds = { west: -80, south: 40, east: -70, north: 41 };

describe('live map helpers', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('reads map edges and falls back to observations', () => {
    expect(
      boundsOf({
        getBounds: () => ({
          getWest: () => -80,
          getSouth: () => 40,
          getEast: () => -70,
          getNorth: () => 41,
        }),
      }),
    ).toEqual(bounds);
    expect(viewById('missing').id).toBe('observations');
    expect(layerQuery('forecasts', new Set())).toBe('taf');
    expect(layerQuery('observations', new Set(['metar', 'speci']))).toBe('');
    expect(selectedLayerQuery(new Set())).toContain('metar');
    expect(selectedLayerQuery(new Set())).toContain('vona');
    expect(selectedLayerQuery(new Set(['metar']))).not.toContain('metar,');
  });

  it('reads a wind group or says it is missing', () => {
    expect(windFromTac('METAR KJFK 031200Z 18012KT')).toBe(
      'Wind from 180 degrees at 12 knots.',
    );
    expect(windFromTac('SPECI KBOS 031205Z VRB03KT')).toBe('Variable wind at 3 knots.');
    expect(windFromTac('TAF KJFK 031200Z')).toBe('No wind group in this report.');
  });

  it('keeps places with coordinates and drops the rest', async () => {
    const signal = new AbortController().signal;
    vi.stubGlobal(
      'fetch',
      vi
        .fn()
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            places: [
              {
                place_key: 'KJFK',
                product: 'metar',
                latitude: 40.6,
                longitude: -73.7,
                reports: [
                  { observed_at: '2026-10-03T12:00:00+00:00', tac: 'METAR KJFK' },
                  { tac: 'missing time' },
                  { observed_at: '2026-10-03T11:00:00+00:00' },
                  null,
                ],
              },
              { place_key: 'BAD' },
              { place_key: 'KJFK', product: 1 },
              { place_key: 'KJFK', product: 'metar', latitude: '40' },
              { place_key: 'KJFK', product: 'metar', latitude: 1, longitude: '2' },
              {
                place_key: 'KJFK',
                product: 'metar',
                latitude: 1,
                longitude: 2,
                reports: 'no',
              },
              null,
              'text',
            ],
          }),
        })
        .mockResolvedValueOnce({ ok: true, json: async () => ({ places: 'nope' }) })
        .mockResolvedValueOnce({ ok: false }),
    );
    const places = await fetchLivePlaces(bounds, 'metar,speci', signal);
    expect(places).toHaveLength(1);
    expect(places[0]?.reports).toHaveLength(1);
    await expect(fetchLivePlaces(bounds, 'metar', signal)).resolves.toEqual([]);
    await expect(fetchLivePlaces(bounds, 'metar', signal)).rejects.toThrow(
      'The live map could not be loaded.',
    );
  });

  it('returns converted XML or says it is unavailable', async () => {
    const signal = new AbortController().signal;
    vi.stubGlobal(
      'fetch',
      vi
        .fn()
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ results: [{ content: '<iwxxm/>' }] }),
        })
        .mockResolvedValueOnce({ ok: true, json: async () => ({ results: [{}] }) })
        .mockResolvedValueOnce({ ok: false }),
    );
    await expect(iwxxmForReport('METAR KJFK', 'metar', signal)).resolves.toBe(
      '<iwxxm/>',
    );
    await expect(iwxxmForReport('METAR KJFK', 'other', signal)).rejects.toThrow(
      'IWXXM is not available',
    );
    await expect(iwxxmForReport('METAR KJFK', 'taf', signal)).rejects.toThrow(
      'IWXXM is not available',
    );
  });
});

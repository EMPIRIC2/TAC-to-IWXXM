/**
 * Live map query, wind text, and IWXXM request.
 */
import { afterEach, describe, expect, it, vi } from 'vitest';
import {
  boundsOf,
  fetchLivePlaces,
  formatObservedAt,
  iwxxmForReport,
  layerQuery,
  newestObservedAt,
  observationAge,
  placeTitle,
  pinColor,
  popupWidth,
  productLabel,
  selectedLayerQuery,
  viewById,
  viewStatus,
  windFromTac,
  LIVE_MAP_EMPTY,
  LIVE_MAP_LOADING,
  LIVE_MAP_NO_TIME,
  LIVE_MAP_REFRESHING,
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
    expect(
      boundsOf({
        getBounds: () => ({
          getWest: () => -284,
          getSouth: () => -80,
          getEast: () => 284,
          getNorth: () => 80,
        }),
      }),
    ).toEqual({ west: -180, south: -80, east: 180, north: 80 });
    expect(viewById('missing').id).toBe('observations');
    expect(layerQuery('forecasts', new Set())).toBe('taf');
    expect(layerQuery('observations', new Set(['metar', 'speci']))).toBe('');
    expect(selectedLayerQuery(new Set())).toContain('metar');
    expect(selectedLayerQuery(new Set())).toContain('vona');
    expect(selectedLayerQuery(new Set(['metar']))).not.toContain('metar,');
  });

  it('names layers, times, and the current view', () => {
    expect(pinColor('taf')).toBe('#0f766e');
    expect(pinColor('airmet')).toBe('#c2410c');
    expect(pinColor('sigmet')).toBe('#c2410c');
    expect(pinColor('vaa')).toBe('#6d28d9');
    expect(pinColor('tca')).toBe('#6d28d9');
    expect(pinColor('vona')).toBe('#6d28d9');
    expect(pinColor('metar')).toBe('#1d4ed8');
    expect(productLabel('vaa')).toBe('Volcanic ash');
    expect(productLabel('other')).toBe('OTHER');
    expect(placeTitle('KJFK', 'Kennedy')).toBe('Kennedy');
    expect(placeTitle('KJFK', undefined)).toBe('KJFK');
    expect(placeTitle('sigmet-abc', undefined)).toBe('Area');
    expect(formatObservedAt('newest')).toBe('newest');
    expect(formatObservedAt('2026-10-03T21:00:00Z')).toBe('03 Oct 21:00 UTC');
    const now = Date.parse('2026-10-03T21:00:00Z');
    expect(observationAge('not-a-time', now)).toBe('');
    expect(observationAge('2026-10-03T21:00:00Z', now)).toBe('just now');
    expect(observationAge('2026-10-03T20:59:00Z', now)).toBe('1 min ago');
    expect(observationAge('2026-10-03T20:30:00Z', now)).toBe('30 min ago');
    expect(observationAge('2026-10-03T20:00:00Z', now)).toBe('1 hour ago');
    expect(observationAge('2026-10-03T16:00:00Z', now)).toBe('5 hours ago');
    expect(observationAge('2026-10-01T21:00:00Z', now)).toBe('2 days ago');
    expect(newestObservedAt([])).toBeNull();
    expect(
      newestObservedAt([
        {
          place_key: 'KJFK',
          product: 'metar',
          latitude: 1,
          longitude: 2,
          reports: [
            { observed_at: 'newest', tac: 'METAR' },
            { observed_at: '2026-10-03T12:00:00Z', tac: 'METAR' },
          ],
        },
      ]),
    ).toBe('2026-10-03T12:00:00Z');
    expect(viewStatus([], true, false)).toBe(LIVE_MAP_LOADING);
    expect(viewStatus([], false, true)).toBe(LIVE_MAP_REFRESHING);
    expect(viewStatus([], false, false)).toBe(LIVE_MAP_EMPTY);
    expect(
      viewStatus(
        [
          {
            place_key: 'KJFK',
            product: 'metar',
            latitude: 1,
            longitude: 2,
            reports: [{ observed_at: '2026-10-03T20:30:00Z', tac: 'METAR' }],
          },
        ],
        false,
        false,
        now,
      ),
    ).toBe('Newest observation in this view: 03 Oct 20:30 UTC (30 min ago).');
    expect(
      viewStatus(
        [
          {
            place_key: 'KJFK',
            product: 'metar',
            latitude: 1,
            longitude: 2,
            reports: [{ observed_at: 'newest', tac: 'METAR' }],
          },
        ],
        false,
        false,
      ),
    ).toBe(LIVE_MAP_NO_TIME);
    expect(popupWidth(400)).toBe(320);
    expect(popupWidth(200)).toBe(180);
    expect(popupWidth(250)).toBe(218);
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

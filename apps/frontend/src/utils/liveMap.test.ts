/**
 * Live map query, wind text, and IWXXM request.
 */
import { afterEach, describe, expect, it, vi } from 'vitest';
import {
  boundsOf,
  fetchLivePlaces,
  filterPlaces,
  formatObservedAt,
  iwxxmForReport,
  layerQuery,
  newestObservedAt,
  observationAge,
  placeTitle,
  pinColor,
  popupWidth,
  productLabel,
  shapePaint,
  SPACE_WEATHER_LIST_COLOR,
  spaceWeatherListColor,
  selectedLayerQuery,
  viewById,
  viewStatus,
  windFromTac,
  cardLayout,
  copyOpacity,
  placeShowingReport,
  pointNudge,
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
    expect(selectedLayerQuery(new Set())).toContain('gairmet');
    expect(selectedLayerQuery(new Set())).toContain('vona');
    expect(selectedLayerQuery(new Set(['metar']))).not.toContain('metar,');
    expect(viewById('hazards').products).toEqual(['airmet', 'gairmet', 'sigmet']);
    expect(layerQuery('hazards', new Set(['gairmet']))).toBe('airmet,sigmet');
  });

  it('names layers, times, and the current view', () => {
    expect(pinColor('metar')).toBe('#1d4ed8');
    expect(pinColor('speci')).toBe('#0369a1');
    expect(pinColor('taf')).toBe('#0f766e');
    expect(pinColor('airmet')).toBe('#c2410c');
    expect(pinColor('gairmet')).toBe('#a16207');
    expect(pinColor('sigmet')).toBe('#b91c1c');
    expect(pinColor('vaa')).toBe('#6d28d9');
    expect(pinColor('tca')).toBe('#be185d');
    expect(pinColor('vona')).toBe('#4338ca');
    expect(pinColor('metar')).not.toBe(pinColor('speci'));
    expect(pinColor('airmet')).not.toBe(pinColor('gairmet'));
    expect(pinColor('other')).toBe('#1d4ed8');
    expect(shapePaint('sigmet')).toEqual({
      color: '#ffffff',
      weight: 2,
      fillColor: '#b91c1c',
      fillOpacity: 0.45,
    });
    expect(SPACE_WEATHER_LIST_COLOR).toBe('#0e7490');
    expect(spaceWeatherListColor(1)).toBe('#0e7490');
    expect(spaceWeatherListColor(0)).toBeUndefined();
    expect(cardLayout(800)).toBe('side');
    expect(cardLayout(767)).toBe('stack');
    expect(
      placeShowingReport(
        {
          place_key: 'KJFK',
          product: 'metar',
          latitude: 1,
          longitude: 2,
          reports: [
            { observed_at: 'new', tac: 'NEW' },
            { observed_at: 'old', tac: 'OLD' },
          ],
        },
        'OLD',
      ).reports.map((report) => report.tac),
    ).toEqual(['OLD', 'NEW']);
    expect(
      placeShowingReport(
        {
          place_key: 'KJFK',
          product: 'metar',
          latitude: 1,
          longitude: 2,
          reports: [{ observed_at: 'new', tac: 'NEW' }],
        },
        'NEW',
      ).reports[0]?.tac,
    ).toBe('NEW');
    const newestFirst = {
      place_key: 'KJFK',
      product: 'metar',
      latitude: 1,
      longitude: 2,
      reports: [{ observed_at: 'new', tac: 'NEW' }],
    };
    expect(placeShowingReport(newestFirst, 'MISSING')).toBe(newestFirst);
    expect(pointNudge(0, 1)).toEqual({ latitude: 0, longitude: 0 });
    expect(pointNudge(0, 2).longitude).toBeLessThan(0);
    expect(pointNudge(1, 2).longitude).toBeGreaterThan(0);
    expect(copyOpacity(0)).toBe(1);
    expect(copyOpacity(1)).toBe(0.45);
    expect(copyOpacity(2)).toBe(0.25);
    expect(productLabel('gairmet')).toBe('G-AIRMET');
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
    expect(String(vi.mocked(fetch).mock.calls[0]?.[0])).not.toContain('country=');
    expect(String(vi.mocked(fetch).mock.calls[0]?.[0])).not.toContain('phenomenon');
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

  it('filters country, region, time, and hazard phenomenon on the loaded view', () => {
    const now = Date.parse('2026-10-06T12:00:00Z');
    const europe = { name: 'Europe', continent: 'Europe' };
    const caribbean = { name: 'Caribbean', continent: 'North America' };
    const countryOf = (placeKey: string) =>
      placeKey === 'KJFK'
        ? 'United States'
        : placeKey === 'EGLL'
          ? 'United Kingdom'
          : undefined;
    const regionOf = (latitude: number) => (latitude > 40 ? europe : caribbean);
    const base = {
      country: 'all',
      region: 'all',
      time: 'all' as const,
      phenomena: new Set<string>(),
      now,
      countryOf,
      regionOf,
    };
    const station = (
      placeKey: string,
      product: string,
      observedAt: string,
      tac: string,
      latitude = 50,
    ) => ({
      place_key: placeKey,
      product,
      latitude,
      longitude: 0,
      reports: [{ observed_at: observedAt, tac }],
    });
    const loaded = [
      station('KJFK', 'metar', '2026-10-06T11:30:00Z', 'METAR KJFK TSRA'),
      station('EGLL', 'metar', '2026-10-06T11:30:00Z', 'METAR EGLL'),
      station('KZZZ', 'metar', '2026-10-06T11:30:00Z', 'METAR KZZZ'),
      station('sigmet-1', 'sigmet', '2026-10-06T11:30:00Z', 'SIGMET FOR EMBD TS', 15),
      station('sigmet-ifr', 'sigmet', '2026-10-06T09:00:00Z', 'SIGMET FOR IFR'),
      station('airmet-turb', 'airmet', '2026-10-06T05:00:00Z', 'AIRMET TANGO FOR TURB'),
      station(
        'gairmet-ice',
        'gairmet',
        '2026-10-05T10:00:00Z',
        'G-AIRMET ZULU FOR ICE',
      ),
      station('sigmet-icing', 'sigmet', '2026-10-06T11:00:00Z', 'SIGMET FOR ICING'),
      station('sigmet-storm', 'sigmet', '2026-10-06T11:00:00Z', 'SIGMET THUNDERSTORM'),
      station('sigmet-vc', 'sigmet', '2026-10-06T11:00:00Z', 'SIGMET VCTS AND +TSRA'),
      station('sigmet-note', 'sigmet', '2026-10-06T11:00:00Z', 'SIGMET NOTICE'),
      station('sigmet-old', 'sigmet', 'newest', 'SIGMET'),
    ];
    expect(filterPlaces(loaded, base).map((place) => place.place_key)).toEqual(
      loaded.map((place) => place.place_key),
    );
    expect(
      filterPlaces(loaded, { ...base, country: 'United States' }).map(
        (place) => place.place_key,
      ),
    ).toEqual([
      'KJFK',
      'sigmet-1',
      'sigmet-ifr',
      'airmet-turb',
      'gairmet-ice',
      'sigmet-icing',
      'sigmet-storm',
      'sigmet-vc',
      'sigmet-note',
      'sigmet-old',
    ]);
    expect(
      filterPlaces(loaded, { ...base, region: 'Europe' }).map(
        (place) => place.place_key,
      ),
    ).not.toContain('sigmet-1');
    expect(
      filterPlaces(loaded, { ...base, region: 'Caribbean' }).map(
        (place) => place.place_key,
      ),
    ).toContain('sigmet-1');
    expect(
      filterPlaces(loaded, { ...base, region: 'North America' }).map(
        (place) => place.place_key,
      ),
    ).toContain('sigmet-1');
    expect(
      filterPlaces(loaded, { ...base, time: '1h' }).map((place) => place.place_key),
    ).toEqual([
      'KJFK',
      'EGLL',
      'KZZZ',
      'sigmet-1',
      'sigmet-icing',
      'sigmet-storm',
      'sigmet-vc',
      'sigmet-note',
      'sigmet-old',
    ]);
    expect(
      filterPlaces(loaded, { ...base, time: '6h' }).map((place) => place.place_key),
    ).toContain('sigmet-ifr');
    expect(
      filterPlaces(loaded, { ...base, time: '6h' }).map((place) => place.place_key),
    ).not.toContain('airmet-turb');
    expect(
      filterPlaces(loaded, { ...base, time: '24h' }).map((place) => place.place_key),
    ).toContain('airmet-turb');
    expect(
      filterPlaces(loaded, { ...base, time: '24h' }).map((place) => place.place_key),
    ).not.toContain('gairmet-ice');
    const storms = filterPlaces(loaded, { ...base, phenomena: new Set(['ts']) });
    expect(storms.map((place) => place.place_key)).toContain('KJFK');
    expect(storms.map((place) => place.place_key)).toContain('sigmet-1');
    expect(storms.map((place) => place.place_key)).toContain('sigmet-storm');
    expect(storms.map((place) => place.place_key)).toContain('sigmet-vc');
    expect(storms.map((place) => place.place_key)).not.toContain('sigmet-ifr');
    expect(
      filterPlaces(loaded, { ...base, phenomena: new Set(['ifr']) }).map(
        (place) => place.place_key,
      ),
    ).toContain('sigmet-ifr');
    expect(
      filterPlaces(loaded, { ...base, phenomena: new Set(['turb']) }).map(
        (place) => place.place_key,
      ),
    ).toContain('airmet-turb');
    expect(
      filterPlaces(loaded, { ...base, phenomena: new Set(['ice']) }).map(
        (place) => place.place_key,
      ),
    ).toEqual(expect.arrayContaining(['gairmet-ice', 'sigmet-icing']));
    expect(
      filterPlaces(loaded, { ...base, phenomena: new Set(['ice']) }).map(
        (place) => place.place_key,
      ),
    ).not.toContain('sigmet-note');
    expect(
      filterPlaces(loaded, { ...base, phenomena: new Set(['nope']) }).map(
        (place) => place.place_key,
      ),
    ).not.toContain('sigmet-1');
  });
});

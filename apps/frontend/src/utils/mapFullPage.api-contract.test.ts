/**
 * API contract the full-page map depends on: GET /api/v1/live-map via
 * fetchLivePlaces (bbox + products), public fetch (no auth headers),
 * places.reports[].tac for Send handoff, and non-OK → LIVE_MAP_ERROR.
 */
import { afterEach, describe, expect, it, vi } from 'vitest';
import {
  fetchLivePlaces,
  LIVE_MAP_ERROR,
  placeShowingReport,
  type LivePlace,
} from './liveMap';

const bounds = { west: -80, south: 40, east: -70, north: 41 };

describe('map full-page live-map API contract', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('fetchLivePlaces GETs /api/v1/live-map with bbox and products query', async () => {
    const signal = new AbortController().signal;
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ places: [] }),
    });
    vi.stubGlobal('fetch', fetchMock);

    await fetchLivePlaces(bounds, 'metar,speci,taf', signal);

    expect(fetchMock).toHaveBeenCalledTimes(1);
    const [url, init] = fetchMock.mock.calls[0] as [string, RequestInit | undefined];
    expect(url).toContain('/api/v1/live-map?');
    const parsed = new URL(url);
    expect(parsed.pathname).toBe('/api/v1/live-map');
    expect(parsed.searchParams.get('west')).toBe('-80');
    expect(parsed.searchParams.get('south')).toBe('40');
    expect(parsed.searchParams.get('east')).toBe('-70');
    expect(parsed.searchParams.get('north')).toBe('41');
    expect(parsed.searchParams.get('products')).toBe('metar,speci,taf');
    expect(init?.signal).toBe(signal);
    expect(init?.method).toBeUndefined();
  });

  it('issues a public unauthenticated fetch (no Authorization or credentials)', async () => {
    const signal = new AbortController().signal;
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ places: [] }),
    });
    vi.stubGlobal('fetch', fetchMock);

    await fetchLivePlaces(bounds, 'metar', signal);

    const [, init] = fetchMock.mock.calls[0] as [string, RequestInit | undefined];
    expect(init).toEqual({ signal });
    expect(init).not.toHaveProperty('headers');
    expect(init).not.toHaveProperty('credentials');
    const headers = init?.headers as Record<string, string> | undefined;
    expect(headers?.Authorization).toBeUndefined();
  });

  it('keeps places.reports[].tac for Send-to-converter handoff', async () => {
    const signal = new AbortController().signal;
    const tacForSend = 'METAR KJFK 031200Z 18012KT 10SM FEW250 22/12 A3012 RMK AO2';
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          places: [
            {
              place_key: 'KJFK',
              product: 'metar',
              latitude: 40.64,
              longitude: -73.78,
              reports: [
                {
                  observed_at: '2026-11-12T12:00:00+00:00',
                  tac: tacForSend,
                  iwxxm: null,
                },
                {
                  observed_at: '2026-11-12T11:00:00+00:00',
                  tac: 'METAR KJFK 031100Z 17010KT',
                },
              ],
            },
          ],
        }),
      }),
    );

    const places = await fetchLivePlaces(bounds, 'metar', signal);
    expect(places).toHaveLength(1);
    const place = places[0] as LivePlace;
    expect(place.reports[0]?.tac).toBe(tacForSend);

    const forSend = placeShowingReport(place, tacForSend);
    expect(forSend.reports[0]?.tac).toBe(tacForSend);
    expect(typeof forSend.reports[0]?.tac).toBe('string');
    expect(forSend.reports[0]?.tac.length).toBeGreaterThan(0);
  });

  it('surfaces LIVE_MAP_ERROR when the live-map response is not OK', async () => {
    const signal = new AbortController().signal;
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: false, status: 503 }));

    await expect(fetchLivePlaces(bounds, 'metar', signal)).rejects.toThrow(
      LIVE_MAP_ERROR,
    );
  });
});

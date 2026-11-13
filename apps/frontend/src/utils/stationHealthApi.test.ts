/**
 * Station health API client coverage.
 */
import { afterEach, describe, expect, it, vi } from 'vitest';

vi.mock('./apiBase', () => ({
  apiUrl: (path: string) => `https://api.example.test/api/v1${path.startsWith('/') ? path : `/${path}`}`,
}));

import {
  fetchStationHealthList,
  fetchStationHealthMetrics,
} from './stationHealthApi';

describe('stationHealthApi', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it('builds list query and returns JSON on success', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        window: '1d',
        computed_at: '2026-11-13T00:00:00Z',
        stations: [],
        summary: { station_count: 0, grade_counts: {} },
      }),
    });
    vi.stubGlobal('fetch', fetchMock);

    const payload = await fetchStationHealthList({
      window: '1d',
      product: 'metar',
      grade: 'A',
      limit: 25,
    });
    expect(payload.window).toBe('1d');
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/station-health?'),
      expect.objectContaining({ method: 'GET' }),
    );
    const url = String(fetchMock.mock.calls[0]?.[0]);
    expect(url).toContain('window=1d');
    expect(url).toContain('product=metar');
    expect(url).toContain('grade=A');
    expect(url).toContain('limit=25');
  });

  it('omits empty list filters and throws on non-OK', async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: false, status: 503 });
    vi.stubGlobal('fetch', fetchMock);
    await expect(fetchStationHealthList()).rejects.toThrow(/503/);
    expect(String(fetchMock.mock.calls[0]?.[0])).toMatch(/\/station-health$/);
  });

  it('fetches metrics and throws on non-OK', async () => {
    const okFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ metrics: [] }),
    });
    vi.stubGlobal('fetch', okFetch);
    await expect(fetchStationHealthMetrics()).resolves.toEqual({ metrics: [] });

    const badFetch = vi.fn().mockResolvedValue({ ok: false, status: 500 });
    vi.stubGlobal('fetch', badFetch);
    await expect(fetchStationHealthMetrics()).rejects.toThrow(/500/);
  });
});

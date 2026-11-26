/**
 * Station health API client coverage.
 */
import { afterEach, describe, expect, it, vi } from 'vitest';

vi.mock('./apiBase', () => ({
  apiUrl: (path: string) =>
    `https://api.example.test/api/v1${path.startsWith('/') ? path : `/${path}`}`,
}));

import {
  fetchStationHealthEvalBenchmark,
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
        window: '90d',
        computed_at: '2026-11-13T00:00:00Z',
        stations: [],
        summary: { station_count: 0, grade_counts: {} },
      }),
    });
    vi.stubGlobal('fetch', fetchMock);

    const payload = await fetchStationHealthList({
      window: '90d',
      product: 'metar',
      grade: 'A',
      region: 'IV',
      limit: 5000,
    });
    expect(payload.window).toBe('90d');
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/station-health?'),
      expect.objectContaining({ method: 'GET' }),
    );
    const url = String(fetchMock.mock.calls[0]?.[0]);
    expect(url).toContain('window=90d');
    expect(url).toContain('product=metar');
    expect(url).toContain('grade=A');
    expect(url).toContain('region=IV');
    expect(url).toContain('limit=5000');
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

  it('fetches eval-benchmark with optional icao and throws on non-OK', async () => {
    const okFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        computed_at: '2026-11-26T12:00:00Z',
        window_hours: 24,
        products: ['metar'],
        partial_decode_count: 0,
        lint_count: 0,
        top_lint_codes: [],
        convert_failure_count: 0,
        iwxxm_validation: { pass: 0, fail: 0, skip: 0 },
        failure_locations: [],
        product_breakdown: [],
        icao_filter: 'KJFK',
      }),
    });
    vi.stubGlobal('fetch', okFetch);
    const body = await fetchStationHealthEvalBenchmark({ icao: 'KJFK' });
    expect(body.icao_filter).toBe('KJFK');
    expect(String(okFetch.mock.calls[0]?.[0])).toContain('icao=KJFK');

    const bareFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        computed_at: '2026-11-26T12:00:00Z',
        window_hours: 24,
        products: [],
        partial_decode_count: 0,
        lint_count: 0,
        top_lint_codes: [],
        convert_failure_count: 0,
        iwxxm_validation: { pass: 0, fail: 0, skip: 0 },
        failure_locations: [],
        product_breakdown: [],
        icao_filter: null,
      }),
    });
    vi.stubGlobal('fetch', bareFetch);
    await fetchStationHealthEvalBenchmark();
    expect(String(bareFetch.mock.calls[0]?.[0])).toMatch(
      /\/station-health\/eval-benchmark$/,
    );
    await fetchStationHealthEvalBenchmark({ icao: '   ' });
    expect(String(bareFetch.mock.calls[1]?.[0])).toMatch(
      /\/station-health\/eval-benchmark$/,
    );

    const badFetch = vi.fn().mockResolvedValue({ ok: false, status: 400 });
    vi.stubGlobal('fetch', badFetch);
    await expect(fetchStationHealthEvalBenchmark({ icao: 'BAD' })).rejects.toThrow(
      /400/,
    );
  });
});

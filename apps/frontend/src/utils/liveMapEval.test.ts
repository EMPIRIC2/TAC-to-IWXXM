/**
 * FR-045 live-map eval fetch parser.
 */
import { afterEach, describe, expect, it, vi } from 'vitest';
import { fetchLiveMapEval } from './liveMapViews';

afterEach(() => {
  vi.unstubAllGlobals();
});

describe('fetchLiveMapEval', () => {
  it('parses a snapshot body', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          computed_at: '2026-11-24T20:00:00Z',
          window_hours: 24,
          products: ['metar'],
          partial_decode_count: 2,
          lint_count: 3,
          top_lint_codes: [{ code: 'MISSING_VIS', count: 2 }],
          convert_failure_count: 1,
          iwxxm_validation: { pass: 4, fail: 1, skip: 2 },
          failure_locations: [
            {
              place_key: 'KJFK',
              product: 'metar',
              stage: 'lint',
              code: 'MISSING_VIS',
            },
          ],
        }),
      }),
    );
    const snapshot = await fetchLiveMapEval();
    expect(snapshot.lint_count).toBe(3);
    expect(snapshot.top_lint_codes[0]?.code).toBe('MISSING_VIS');
    expect(snapshot.iwxxm_validation.pass).toBe(4);
  });

  it('throws when the response is not ok', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({ ok: false, json: async () => ({}) }),
    );
    await expect(fetchLiveMapEval()).rejects.toThrow(/evaluation could not be loaded/i);
  });
});

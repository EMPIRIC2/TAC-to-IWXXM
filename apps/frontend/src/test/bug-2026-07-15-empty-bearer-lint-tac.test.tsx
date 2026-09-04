/**
 * BUG-2026-07-15 — Empty Bearer on lint-tac/decode-tac.
 *
 * Superseded by F21 / TC-F21-auth-gone: public API omits Authorization entirely.
 * Retention: ensure stale localStorage tokens are not sent.
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { lintTac, decodeTac } from '@/utils/api';

global.fetch = vi.fn();

describe('BUG-2026-07-15 superseded by F21 (no Bearer)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    vi.stubEnv('VITE_API_BASE_URL', 'https://api.example.onrender.com');
    (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValue({
      ok: true,
      status: 200,
      json: vi.fn().mockResolvedValue({ issues: [], segments: [] }),
    });
  });

  afterEach(() => {
    vi.unstubAllEnvs();
  });

  it('lintTac does not send Authorization when access_token is present', async () => {
    localStorage.setItem('access_token', 'stale-jwt');
    await lintTac({ manualText: 'fjgfjf', product: 'METAR' });
    const init = (global.fetch as ReturnType<typeof vi.fn>).mock
      .calls[0]![1] as RequestInit;
    expect(
      (init.headers as Record<string, string> | undefined)?.Authorization,
    ).toBeUndefined();
  });

  it('decodeTac does not send Authorization when access_token is present', async () => {
    localStorage.setItem('access_token', 'stale-jwt');
    await decodeTac({ manualText: 'fjgfjf', product: 'METAR' });
    const init = (global.fetch as ReturnType<typeof vi.fn>).mock
      .calls[0]![1] as RequestInit;
    expect(
      (init.headers as Record<string, string> | undefined)?.Authorization,
    ).toBeUndefined();
  });
});

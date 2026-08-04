/**
 * BUG-2026-08-04 — Production UI called suspended Render API despite /config.json
 * pointing at https://api.tac-to-iwxxm.com (DOKS).
 *
 * Root cause: apiBase.ts read bake-time VITE_API_BASE_URL and ignored runtime-config.
 * Regression: after initRuntimeConfig(), apiUrl/getApiBaseUrl must use config.json host
 * even when VITE still points at the old onrender host.
 */
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

describe('BUG-2026-08-04 frontend baked onrender API host', () => {
  beforeEach(() => {
    vi.resetModules();
    vi.unstubAllEnvs();
    // Stale bake-time host (matches live App-BkEPMp_C.js after DOKS cutover).
    vi.stubEnv('VITE_API_BASE_URL', 'https://metar-to-iwxxm-api.onrender.com');
    vi.stubEnv('VITE_APP_URL', 'https://app.tac-to-iwxxm.com');
    vi.stubEnv('MODE', 'production');
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: vi.fn().mockResolvedValue({
        environment: 'prod',
        api: {
          baseUrl: 'https://api.tac-to-iwxxm.com',
          frontendUrl: 'https://app.tac-to-iwxxm.com',
          corsOrigins: ['https://app.tac-to-iwxxm.com'],
        },
        supabase: {
          url: 'https://ktvxijislbtgqapllmuk.supabase.co',
          publishableKey: 'sb_publishable_test_key',
        },
      }),
    });
  });

  afterEach(() => {
    vi.unstubAllEnvs();
    vi.restoreAllMocks();
  });

  it('uses /config.json API host for apiBase helpers after initRuntimeConfig', async () => {
    const runtime = await import('../utils/runtime-config');
    await runtime.initRuntimeConfig();

    const apiBase = await import('../utils/apiBase');

    expect(apiBase.getApiBaseUrl()).toBe('https://api.tac-to-iwxxm.com');
    expect(apiBase.apiUrl('/lint-issue-catalog')).toBe(
      'https://api.tac-to-iwxxm.com/api/v1/lint-issue-catalog',
    );
    expect(apiBase.requireApiBaseUrl()).toBe('https://api.tac-to-iwxxm.com');
    // Must not keep calling the suspended Render hostname.
    expect(apiBase.getApiBaseUrl()).not.toContain('onrender.com');
  });

  it('exposes supabase publishableKey from /config.json via runtime-config', async () => {
    const runtime = await import('../utils/runtime-config');
    await runtime.initRuntimeConfig();

    expect(runtime.getSupabasePublishableKey()).toBe('sb_publishable_test_key');
  });
});

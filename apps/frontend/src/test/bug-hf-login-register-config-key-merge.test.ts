/**
 * HF-login-register-broken regression.
 *
 * Prod DOKS ConfigMap `/config.json` shipped `supabase.url` without
 * `publishableKey`. Empty apikey → Supabase 401 "No API key found".
 * runtime-config must merge bake-time Vite publishable key.
 *
 * [Corpus: api] [Corpus: env] [Corpus: product F21/F31]
 */
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

describe('HF login/register — config.json missing publishableKey', () => {
  beforeEach(() => {
    vi.resetModules();
    vi.unstubAllEnvs();
    vi.stubEnv('VITE_API_BASE_URL', 'https://api.tac-to-iwxxm.com');
    vi.stubEnv('VITE_APP_URL', 'https://app.tac-to-iwxxm.com');
    vi.stubEnv('VITE_SUPABASE_URL', 'https://ktvxijislbtgqapllmuk.supabase.co');
    vi.stubEnv(
      'VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY',
      'sb_publishable_baked_from_vite',
    );
    global.fetch = vi.fn();
  });

  afterEach(() => {
    vi.unstubAllEnvs();
    vi.restoreAllMocks();
  });

  it('merges Vite key when prod config.json omits publishableKey', async () => {
    (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: true,
      json: vi.fn().mockResolvedValueOnce({
        environment: 'prod',
        api: {
          baseUrl: 'https://api.tac-to-iwxxm.com',
          frontendUrl: 'https://app.tac-to-iwxxm.com',
        },
        supabase: {
          url: 'https://ktvxijislbtgqapllmuk.supabase.co',
        },
      }),
    });

    const runtime = await import('../utils/runtime-config');
    await runtime.initRuntimeConfig();

    expect(runtime.getSupabasePublishableKey()).toBe('sb_publishable_baked_from_vite');
    expect(runtime.getSupabaseUrl()).toBe('https://ktvxijislbtgqapllmuk.supabase.co');
  });
});

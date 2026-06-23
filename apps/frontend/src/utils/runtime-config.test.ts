import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

describe('runtime-config', () => {
  beforeEach(() => {
    vi.resetModules();
    vi.unstubAllEnvs();
    vi.stubEnv('VITE_API_BASE_URL', 'http://localhost:18001/');
    vi.stubEnv('VITE_APP_URL', 'http://localhost:18000');
    vi.stubEnv('VITE_SUPABASE_URL', 'https://demo.supabase.co');
    vi.stubEnv('VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY', 'publishable-key');
    global.fetch = vi.fn();
  });

  afterEach(() => {
    vi.unstubAllEnvs();
    vi.restoreAllMocks();
  });

  it('loads config.json when fetch succeeds', async () => {
    (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: true,
      json: vi.fn().mockResolvedValueOnce({
        environment: 'local',
        api: {
          baseUrl: 'http://api.test',
          frontendUrl: 'http://frontend.test',
          corsOrigins: ['http://frontend.test'],
        },
        supabase: {
          url: 'https://project.supabase.co',
          publishableKey: 'sb_publishable_test',
        },
      }),
    });

    const runtime = await import('./runtime-config');
    const config = await runtime.initRuntimeConfig();

    expect(config.api.baseUrl).toBe('http://api.test');
    expect(runtime.getApiBaseUrl()).toBe('http://api.test');
    expect(runtime.getSupabaseUrl()).toBe('https://project.supabase.co');
    expect(runtime.getSupabasePublishableKey()).toBe('sb_publishable_test');
  });

  it('falls back to Vite env when config.json is unavailable', async () => {
    (global.fetch as ReturnType<typeof vi.fn>).mockRejectedValueOnce(
      new Error('network'),
    );

    const runtime = await import('./runtime-config');
    const config = await runtime.initRuntimeConfig();

    expect(config.api.baseUrl).toBe('http://localhost:18001/');
    expect(runtime.getApiBaseUrl()).toBe('http://localhost:18001');
    expect(runtime.getSupabasePublishableKey()).toBe('publishable-key');
  });

  it('returns cached config from getRuntimeConfig without init', async () => {
    const runtime = await import('./runtime-config');
    const config = runtime.getRuntimeConfig();

    expect(config.supabase.url).toBe('https://demo.supabase.co');
    expect(runtime.getSupabasePublishableKey()).toBe('publishable-key');
  });
});

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

  it('merges Vite publishableKey when config.json omits Auth key (HF login)', async () => {
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

    const runtime = await import('./runtime-config');
    await runtime.initRuntimeConfig();

    expect(runtime.getSupabaseUrl()).toBe('https://ktvxijislbtgqapllmuk.supabase.co');
    expect(runtime.getSupabasePublishableKey()).toBe('publishable-key');
  });

  it('merges Vite supabase.url when config.json leaves url empty', async () => {
    (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: true,
      json: vi.fn().mockResolvedValueOnce({
        environment: 'prod',
        api: { baseUrl: 'https://api.test', frontendUrl: 'https://app.test' },
        supabase: { url: '   ', publishableKey: '' },
      }),
    });

    const runtime = await import('./runtime-config');
    await runtime.initRuntimeConfig();

    expect(runtime.getSupabaseUrl()).toBe('https://demo.supabase.co');
    expect(runtime.getSupabasePublishableKey()).toBe('publishable-key');
  });

  it('leaves Auth bootstrap empty when config and Vite both omit url', async () => {
    vi.stubEnv('VITE_SUPABASE_URL', '');
    vi.stubEnv('VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY', '');
    (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: true,
      json: vi.fn().mockResolvedValueOnce({
        environment: 'prod',
        api: { baseUrl: 'https://api.test', frontendUrl: 'https://app.test' },
        supabase: { url: '', publishableKey: '' },
      }),
    });

    const runtime = await import('./runtime-config');
    await runtime.initRuntimeConfig();

    expect(runtime.getSupabaseUrl()).toBe('');
    expect(runtime.getSupabasePublishableKey()).toBe('');
  });

  it('merges Vite Auth bootstrap when config.json omits supabase object', async () => {
    (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: true,
      json: vi.fn().mockResolvedValueOnce({
        environment: 'prod',
        api: { baseUrl: 'https://api.test', frontendUrl: 'https://app.test' },
      }),
    });

    const runtime = await import('./runtime-config');
    await runtime.initRuntimeConfig();

    expect(runtime.getSupabaseUrl()).toBe('https://demo.supabase.co');
    expect(runtime.getSupabasePublishableKey()).toBe('publishable-key');
  });

  it('does not override config.json publishableKey with Vite env', async () => {
    (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: true,
      json: vi.fn().mockResolvedValueOnce({
        environment: 'prod',
        api: { baseUrl: 'https://api.test', frontendUrl: 'https://app.test' },
        supabase: {
          url: 'https://project.supabase.co',
          publishableKey: 'sb_publishable_from_config',
        },
      }),
    });

    const runtime = await import('./runtime-config');
    await runtime.initRuntimeConfig();

    expect(runtime.getSupabasePublishableKey()).toBe('sb_publishable_from_config');
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

  it('does not expose isAuthDisabled (F21 — public by default)', async () => {
    const runtime = await import('./runtime-config');
    expect('isAuthDisabled' in runtime).toBe(false);
  });

  it('reuses cached config on subsequent initRuntimeConfig calls', async () => {
    (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: true,
      json: vi.fn().mockResolvedValueOnce({
        environment: 'local',
        api: { baseUrl: 'http://api.test', frontendUrl: 'http://frontend.test' },
        supabase: { url: 'https://project.supabase.co' },
      }),
    });

    const runtime = await import('./runtime-config');
    const first = await runtime.initRuntimeConfig();
    const second = await runtime.initRuntimeConfig();

    expect(second).toBe(first);
    expect(global.fetch).toHaveBeenCalledTimes(1);
  });

  it('falls back when config.json responds with non-OK status', async () => {
    (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: false,
      status: 404,
    });

    const runtime = await import('./runtime-config');
    const config = await runtime.initRuntimeConfig();

    expect(config.api.baseUrl).toBe('http://localhost:18001/');
  });

  it('defaults environment mode when Vite MODE is unset', async () => {
    vi.unstubAllEnvs();
    vi.stubEnv('VITE_API_BASE_URL', 'http://localhost:18001');
    vi.stubEnv('VITE_APP_URL', 'http://localhost:18000');
    (global.fetch as ReturnType<typeof vi.fn>).mockRejectedValueOnce(
      new Error('network'),
    );

    const runtime = await import('./runtime-config');
    const config = await runtime.initRuntimeConfig();

    expect(config.environment).toBe('test');
  });

  it('falls back to localhost URLs when Vite env URLs are empty', async () => {
    vi.unstubAllEnvs();
    vi.stubEnv('VITE_API_BASE_URL', '');
    vi.stubEnv('VITE_APP_URL', '');
    (global.fetch as ReturnType<typeof vi.fn>).mockRejectedValueOnce(
      new Error('network'),
    );

    const runtime = await import('./runtime-config');
    const config = await runtime.initRuntimeConfig();

    expect(config.api.baseUrl).toBe('http://localhost:18001');
    expect(config.api.frontendUrl).toBe('http://localhost:18000');
  });

  it('uses development when MODE is unset in Vite env fallback', async () => {
    vi.unstubAllEnvs();
    vi.stubEnv('MODE', '');
    vi.stubEnv('VITE_API_BASE_URL', 'http://localhost:18001');
    vi.stubEnv('VITE_APP_URL', 'http://localhost:18000');

    const runtime = await import('./runtime-config');
    expect(runtime.getRuntimeConfig().environment).toBe('development');
  });

  it('omits sentryDsn when Vite DSN is blank and publishableKey when unset', async () => {
    vi.unstubAllEnvs();
    vi.stubEnv('VITE_API_BASE_URL', 'http://localhost:18001');
    vi.stubEnv('VITE_APP_URL', 'http://localhost:18000');
    vi.stubEnv('VITE_SUPABASE_URL', 'https://demo.supabase.co');
    vi.stubEnv('VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY', '');
    vi.stubEnv('VITE_SENTRY_DSN', '   ');
    (global.fetch as ReturnType<typeof vi.fn>).mockRejectedValueOnce(
      new Error('network'),
    );

    const runtime = await import('./runtime-config');
    const config = await runtime.initRuntimeConfig();

    expect(config.sentryDsn).toBeUndefined();
    expect(runtime.getSupabasePublishableKey()).toBe('');
  });
});

import { beforeEach, describe, expect, it, vi } from 'vitest';

const initMock = vi.fn();

vi.mock('@sentry/react', () => ({
  init: (...args: unknown[]) => initMock(...args),
}));

describe('initSentry', () => {
  beforeEach(() => {
    initMock.mockReset();
    vi.resetModules();
    vi.stubEnv('VITE_SENTRY_DSN', '');
  });

  it('is a no-op when DSN unset', async () => {
    const { initRuntimeConfig } = await import('./runtime-config');
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: false, status: 404 }));
    await initRuntimeConfig();
    const { initSentry } = await import('./sentry');
    expect(initSentry()).toBe(false);
    expect(initMock).not.toHaveBeenCalled();
  });

  it('initializes when VITE_SENTRY_DSN is set', async () => {
    vi.stubEnv('VITE_SENTRY_DSN', 'https://public@example.ingest.sentry.io/1');
    const { initRuntimeConfig } = await import('./runtime-config');
    // Force Vite fallback path
    const mod = await import('./runtime-config');
    // re-init via fresh module state: call configFromVite by failing fetch
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: false, status: 404 }));
    // Clear cached config by re-importing after resetModules
    await initRuntimeConfig();
    const { initSentry } = await import('./sentry');
    expect(initSentry()).toBe(true);
    expect(initMock).toHaveBeenCalledWith(
      expect.objectContaining({
        dsn: 'https://public@example.ingest.sentry.io/1',
        tracesSampleRate: 0,
      }),
    );
    void mod;
  });
});

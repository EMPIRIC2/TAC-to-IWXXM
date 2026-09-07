/**
 * EV-080 — requireApiBaseUrl nullish env / runtime branches.
 */
import { afterEach, describe, expect, it, vi } from 'vitest';

const runtimeMocks = vi.hoisted(() => ({
  getApiBaseUrl: vi.fn(() => 'https://api.example.test'),
  getRuntimeConfig: vi.fn(() => ({
    api: { baseUrl: 'https://api.example.test' as string | undefined },
  })),
}));

vi.mock('./runtime-config', () => ({
  getApiBaseUrl: () => runtimeMocks.getApiBaseUrl(),
  getRuntimeConfig: () => runtimeMocks.getRuntimeConfig(),
}));

import { requireApiBaseUrl } from './apiBase';

describe('requireApiBaseUrl (EV-080)', () => {
  afterEach(() => {
    vi.unstubAllEnvs();
    runtimeMocks.getApiBaseUrl.mockReset();
    runtimeMocks.getRuntimeConfig.mockReset();
    runtimeMocks.getApiBaseUrl.mockReturnValue('https://api.example.test');
    runtimeMocks.getRuntimeConfig.mockReturnValue({
      api: { baseUrl: 'https://api.example.test' },
    });
  });

  it('allows production when vite URL is set even if runtime is empty', () => {
    vi.stubEnv('MODE', 'production');
    vi.stubEnv('VITE_API_BASE_URL', 'https://vite.example');
    runtimeMocks.getRuntimeConfig.mockReturnValue({ api: { baseUrl: undefined } });
    runtimeMocks.getApiBaseUrl.mockReturnValue('https://vite.example');
    expect(requireApiBaseUrl()).toBe('https://vite.example');
  });

  it('allows production when runtime URL is set and vite is empty', () => {
    vi.stubEnv('MODE', 'production');
    vi.stubEnv('VITE_API_BASE_URL', '');
    runtimeMocks.getRuntimeConfig.mockReturnValue({
      api: { baseUrl: 'https://runtime.example' },
    });
    runtimeMocks.getApiBaseUrl.mockReturnValue('https://runtime.example');
    expect(requireApiBaseUrl()).toBe('https://runtime.example');
  });

  it('rejects production when both vite and runtime are empty-ish', () => {
    vi.stubEnv('MODE', 'production');
    vi.stubEnv('VITE_API_BASE_URL', '');
    runtimeMocks.getRuntimeConfig.mockReturnValue({ api: { baseUrl: '' } });
    runtimeMocks.getApiBaseUrl.mockReturnValue('http://localhost:18001');
    expect(() => requireApiBaseUrl()).toThrow(/API base URL must be set/i);
  });

  it('allows production when vite env key is undefined (nullish coalesce)', () => {
    vi.stubEnv('MODE', 'production');
    vi.stubEnv('VITE_API_BASE_URL', undefined as unknown as string);
    runtimeMocks.getRuntimeConfig.mockReturnValue({
      api: { baseUrl: 'https://runtime.example' },
    });
    runtimeMocks.getApiBaseUrl.mockReturnValue('https://runtime.example');
    expect(requireApiBaseUrl()).toBe('https://runtime.example');
  });
});

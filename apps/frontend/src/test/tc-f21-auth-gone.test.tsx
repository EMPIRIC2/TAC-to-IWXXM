/**
 * TC-F21-auth-gone (frontend slice) — S023 / EV-017 / T4.1
 *
 * Public app: no login chrome, no JWT bootstrap on convert/lint/decode,
 * Auth route components absent from the FE surface.
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { convertMetarToIwxxm, decodeTac, lintTac } from '@/utils/api';

global.fetch = vi.fn();

vi.mock('@/utils/localWorkSessionStore', () => ({
  listLocalWorkSessions: vi
    .fn()
    .mockResolvedValue({ items: [], total: 0, page: 1, limit: 20 }),
  migrateGuestSessionStorageToIndexedDb: vi
    .fn()
    .mockResolvedValue({ migrated: false, sessionId: null }),
}));

vi.mock('@/utils/guestConverterState', () => ({
  readGuestConverterState: vi.fn(() => null),
  clearGuestConverterState: vi.fn(),
}));

vi.mock('sonner', () => ({
  toast: { error: vi.fn(), success: vi.fn(), info: vi.fn() },
  Toaster: () => null,
}));

vi.mock('@/app/components/FileConverter', () => ({
  FileConverter: () => <div data-testid="file-converter" />,
}));

vi.mock('@/app/components/MyMetarsPage', () => ({
  MyMetarsPage: () => <div data-testid="my-metars" />,
}));

vi.mock('@/app/components/ThemeProvider', () => ({
  ThemeProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

vi.mock('@/app/components/ui/sonner', () => ({
  Toaster: () => <div data-testid="toaster" />,
}));

import App from '@/app/App';

function authHeaderFromFetchCall(): string | undefined {
  const call = (global.fetch as ReturnType<typeof vi.fn>).mock.calls[0];
  const init = call?.[1] as RequestInit | undefined;
  const headers = init?.headers as Record<string, string> | undefined;
  return headers?.Authorization;
}

describe('TC-F21-auth-gone (frontend)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    vi.stubEnv('VITE_API_BASE_URL', 'https://api.example.onrender.com');
    (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValue({
      ok: true,
      status: 200,
      statusText: 'OK',
      json: vi.fn().mockResolvedValue({
        results: [],
        errors: [],
        total_processed: 0,
        successful: 0,
        failed: 0,
        issues: [],
        segments: [],
      }),
    });
  });

  afterEach(() => {
    vi.unstubAllEnvs();
  });

  it('boots directly to converter with no login/register chrome', () => {
    render(<App />);

    expect(screen.getByTestId('file-converter')).toBeInTheDocument();
    expect(screen.queryByTestId('login-view')).not.toBeInTheDocument();
    expect(screen.queryByText(/sign in/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/log in/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/create account/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/register/i)).not.toBeInTheDocument();
  });

  it('App.tsx does not import Auth route components', () => {
    const appSource = readFileSync(resolve(__dirname, '../app/App.tsx'), 'utf8');
    expect(appSource).not.toMatch(/from ['"]\.\/components\/auth\//);
    expect(appSource).not.toMatch(/authService/);
    expect(appSource).not.toMatch(/isLoggedIn|getAccessToken|logout/);
  });

  it('convertMetarToIwxxm omits Authorization even when a token is in storage', async () => {
    localStorage.setItem('access_token', 'stale-jwt');
    await convertMetarToIwxxm({
      manualText: 'METAR KJFK 121851Z 09014KT 10SM FEW250',
    });
    expect(authHeaderFromFetchCall()).toBeUndefined();
  });

  it('lintTac omits Authorization even when a token is in storage', async () => {
    localStorage.setItem('access_token', 'stale-jwt');
    await lintTac({ manualText: 'METAR KJFK 121851Z 09014KT 10SM FEW250' });
    expect(authHeaderFromFetchCall()).toBeUndefined();
  });

  it('decodeTac omits Authorization even when a token is in storage', async () => {
    localStorage.setItem('access_token', 'stale-jwt');
    await decodeTac({
      manualText: 'METAR KJFK 121851Z 09014KT 10SM FEW250',
      product: 'METAR',
    });
    expect(authHeaderFromFetchCall()).toBeUndefined();
  });
});

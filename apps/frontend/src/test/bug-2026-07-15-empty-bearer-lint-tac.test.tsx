/**
 * BUG-2026-07-15 — Empty Bearer on lint-tac/decode-tac (auth hydrate + storage key).
 *
 * Production HAR: Authorization: Bearer (no JWT) → Missing authorization credentials.
 *
 * Report: docs/bug-reports/BUG-2026-07-15-empty-bearer-lint-tac.md
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { lintTac, decodeTac } from '@/utils/api';

const authServiceMocks = vi.hoisted(() => ({
  isLoggedIn: vi.fn(),
  logout: vi.fn(),
  getAccessToken: vi.fn(),
}));

vi.mock('@/utils/authService', () => ({
  isLoggedIn: authServiceMocks.isLoggedIn,
  logout: authServiceMocks.logout,
  getAccessToken: authServiceMocks.getAccessToken,
}));

vi.mock('@/utils/workSessionApi', () => ({
  listWorkSessions: vi.fn().mockResolvedValue({ items: [] }),
  createWorkSession: vi.fn(),
}));

vi.mock('@/utils/guestConverterState', () => ({
  readGuestConverterState: vi.fn(() => null),
  clearGuestConverterState: vi.fn(),
}));

vi.mock('@/utils/runtime-config', () => ({
  isAuthDisabled: () => false,
}));

vi.mock('sonner', () => ({
  toast: { error: vi.fn(), success: vi.fn() },
  Toaster: () => null,
}));

vi.mock('@/app/components/FileConverter', () => ({
  FileConverter: ({ accessToken }: { accessToken?: string }) => (
    <div
      data-testid="file-converter"
      data-access-token={accessToken === undefined ? '__undefined__' : accessToken}
    />
  ),
}));

vi.mock('@/app/components/auth/Login', () => ({
  Login: () => <div data-testid="login-view" />,
}));

vi.mock('@/app/components/auth/Register', () => ({
  Register: () => null,
}));

vi.mock('@/app/components/auth/EmailVerification', () => ({
  EmailVerification: () => null,
}));

vi.mock('@/app/components/auth/AuthCallback', () => ({
  AuthCallback: () => null,
}));

vi.mock('@/app/components/auth/PasswordReset', () => ({
  PasswordReset: () => null,
}));

vi.mock('@/app/components/MyMetarsPage', () => ({
  MyMetarsPage: () => null,
}));

vi.mock('@/app/components/ThemeProvider', () => ({
  ThemeProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

describe('BUG-2026-07-15 empty Bearer lint-tac / decode-tac', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
    global.fetch = vi.fn();
    authServiceMocks.isLoggedIn.mockReturnValue(false);
    authServiceMocks.getAccessToken.mockReturnValue(null);
  });

  afterEach(() => {
    localStorage.clear();
  });

  function mockOkJson(data: unknown) {
    (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: true,
      status: 200,
      statusText: 'OK',
      json: vi.fn().mockResolvedValueOnce(data),
    });
  }

  function mockErrJson(data: unknown, status = 401) {
    (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: false,
      status,
      statusText: 'Unauthorized',
      json: vi.fn().mockResolvedValueOnce(data),
    });
  }

  it('lintTac sends Bearer from authService localStorage key access_token', async () => {
    localStorage.setItem('access_token', 'real-jwt-from-login');
    localStorage.removeItem('supabase_access_token');
    mockOkJson({ ok: true, issues: [], fixes: [], product: 'METAR' });

    await lintTac({ manualText: 'fjgfjf', product: 'METAR' });

    const [, init] = (global.fetch as ReturnType<typeof vi.fn>).mock.calls[0] as [
      string,
      RequestInit,
    ];
    const headers = init.headers as Record<string, string>;
    expect(headers.Authorization).toBe('Bearer real-jwt-from-login');
  });

  it('decodeTac sends Bearer from authService localStorage key access_token', async () => {
    localStorage.setItem('access_token', 'real-jwt-from-login');
    localStorage.removeItem('supabase_access_token');
    mockOkJson({ product: 'METAR', segments: [], residuals: [] });

    await decodeTac({ manualText: 'fjgfjf', product: 'METAR' });

    const [, init] = (global.fetch as ReturnType<typeof vi.fn>).mock.calls[0] as [
      string,
      RequestInit,
    ];
    const headers = init.headers as Record<string, string>;
    expect(headers.Authorization).toBe('Bearer real-jwt-from-login');
  });

  it('lintTac surfaces FastAPI string detail on 401 (not only HTTP 401)', async () => {
    mockErrJson({ detail: 'Missing authorization credentials' }, 401);

    await expect(
      lintTac({ manualText: 'fjgfjf', product: 'METAR', accessToken: '' }),
    ).rejects.toThrow('Missing authorization credentials');
  });

  it('App reload hydrates FileConverter accessToken from getAccessToken when logged in', async () => {
    authServiceMocks.isLoggedIn.mockReturnValue(true);
    authServiceMocks.getAccessToken.mockReturnValue('hydrated-jwt');

    const { default: App } = await import('@/app/App');
    render(<App />);

    const el = await screen.findByTestId('file-converter');
    expect(el.getAttribute('data-access-token')).toBe('hydrated-jwt');
  });
});

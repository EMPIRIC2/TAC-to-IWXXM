/**
 * TC-F21-auth-gone (frontend slice) — F21 Amended / EV-031 / F31
 *
 * Public convert remains JWT-free. Optional Auth login UX may exist for
 * long-term storage; App boots to the converter without forcing login.
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen } from '@testing-library/react';
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

vi.mock('@/utils/authService', () => ({
  getAccessToken: vi.fn(() => null),
  isLoggedIn: vi.fn(() => false),
  logout: vi.fn(),
}));

vi.mock('sonner', () => ({
  toast: { error: vi.fn(), success: vi.fn(), info: vi.fn() },
  Toaster: () => null,
}));

vi.mock('@/app/components/FileConverter', () => ({
  FileConverter: ({
    isGuest,
    onRequestLogin,
  }: {
    isGuest?: boolean;
    onRequestLogin?: () => void;
  }) => (
    <div data-testid="file-converter">
      {isGuest ? (
        <button type="button" data-testid="sign-in-button" onClick={onRequestLogin}>
          Sign in
        </button>
      ) : null}
    </div>
  ),
}));

vi.mock('@/app/components/MyMetarsPage', () => ({
  MyMetarsPage: () => <div data-testid="my-metars" />,
}));

vi.mock('@/app/components/auth/Login', () => ({
  Login: ({ onContinueAsGuest }: { onContinueAsGuest?: () => void }) => (
    <div data-testid="login-view">
      <button type="button" onClick={onContinueAsGuest}>
        Continue without signing in
      </button>
    </div>
  ),
}));

vi.mock('@/app/components/auth/Register', () => ({
  Register: () => <div data-testid="register-view" />,
}));

vi.mock('@/app/components/auth/EmailVerification', () => ({
  EmailVerification: () => <div data-testid="verify-view" />,
}));

vi.mock('@/app/components/auth/AuthCallback', () => ({
  AuthCallback: () => <div data-testid="callback-view" />,
}));

vi.mock('@/app/components/auth/PasswordReset', () => ({
  PasswordReset: () => <div data-testid="reset-view" />,
}));

vi.mock('@/app/components/ThemeProvider', () => ({
  ThemeProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

vi.mock('@/app/components/ui/sonner', () => ({
  Toaster: () => <div data-testid="toaster" />,
}));

import App from '@/app/App';
import userEvent from '@testing-library/user-event';

function authHeaderFromFetchCall(): string | undefined {
  const call = (global.fetch as ReturnType<typeof vi.fn>).mock.calls[0];
  const init = call?.[1] as RequestInit | undefined;
  const headers = init?.headers as Record<string, string> | undefined;
  return headers?.Authorization;
}

describe('TC-F21-auth-gone (frontend, F31 amended)', () => {
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

  it('boots directly to converter with optional Sign in (no forced login gate)', () => {
    render(<App />);

    expect(screen.getByTestId('file-converter')).toBeInTheDocument();
    expect(screen.queryByTestId('login-view')).not.toBeInTheDocument();
    expect(screen.getByTestId('sign-in-button')).toBeInTheDocument();
  });

  it('opens optional login UX from Sign in and returns via continue-as-guest', async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.click(screen.getByTestId('sign-in-button'));
    expect(screen.getByTestId('login-view')).toBeInTheDocument();
    expect(screen.queryByTestId('file-converter')).not.toBeInTheDocument();

    await user.click(
      screen.getByRole('button', { name: /continue without signing in/i }),
    );
    expect(screen.getByTestId('file-converter')).toBeInTheDocument();
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

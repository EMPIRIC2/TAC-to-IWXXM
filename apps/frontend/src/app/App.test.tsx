import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

const workSessionMocks = vi.hoisted(() => ({
  listLocalWorkSessions: vi.fn(),
  migrateGuestSessionStorageToIndexedDb: vi.fn(),
}));

vi.mock('@/utils/localWorkSessionStore', () => ({
  listLocalWorkSessions: workSessionMocks.listLocalWorkSessions,
  migrateGuestSessionStorageToIndexedDb:
    workSessionMocks.migrateGuestSessionStorageToIndexedDb,
}));

vi.mock('@/utils/guestConverterState', () => ({
  readGuestConverterState: vi.fn(() => null),
  clearGuestConverterState: vi.fn(),
}));

const toastMocks = vi.hoisted(() => ({
  error: vi.fn(),
  success: vi.fn(),
  info: vi.fn(),
}));

vi.mock('sonner', () => ({
  toast: toastMocks,
}));

vi.mock('./components/FileConverter', () => ({
  FileConverter: ({
    onOpenHistory,
    onRequestLogin,
    isGuest,
  }: {
    onOpenHistory?: () => void;
    onRequestLogin?: () => void;
    isGuest?: boolean;
  }) => (
    <div data-testid="file-converter">
      <button
        type="button"
        data-testid="open-history"
        onClick={() => onOpenHistory?.()}
      >
        History
      </button>
      {isGuest ? (
        <button type="button" data-testid="sign-in-button" onClick={onRequestLogin}>
          Sign in
        </button>
      ) : null}
    </div>
  ),
}));

vi.mock('./components/auth/Login', () => ({
  Login: ({ onContinueAsGuest }: { onContinueAsGuest?: () => void }) => (
    <div data-testid="login-view">
      <button type="button" onClick={onContinueAsGuest}>
        Continue without signing in
      </button>
    </div>
  ),
}));

vi.mock('./components/auth/Register', () => ({
  Register: () => <div data-testid="register-view" />,
}));

vi.mock('./components/auth/EmailVerification', () => ({
  EmailVerification: () => <div data-testid="verify-view" />,
}));

vi.mock('./components/auth/AuthCallback', () => ({
  AuthCallback: () => <div data-testid="callback-view" />,
}));

vi.mock('./components/auth/PasswordReset', () => ({
  PasswordReset: () => <div data-testid="reset-view" />,
}));

vi.mock('@/utils/authService', () => ({
  getAccessToken: vi.fn(() => null),
  isLoggedIn: vi.fn(() => false),
  logout: vi.fn(),
}));

vi.mock('@/utils/autoUploadLocalDrafts', () => ({
  autoUploadEligibleLocalDrafts: vi.fn().mockResolvedValue({ uploaded: 0, errors: [] }),
}));

vi.mock('@/utils/workSessionApi', () => ({
  listWorkSessions: vi
    .fn()
    .mockResolvedValue({ items: [], total: 0, page: 1, limit: 20 }),
}));

vi.mock('./components/MyMetarsPage', () => ({
  MyMetarsPage: ({
    onBack,
    onOpenSession,
  }: {
    onBack: () => void;
    onOpenSession: (session: { id: string }) => void;
  }) => (
    <div data-testid="history-view">
      <button type="button" data-testid="back-converter" onClick={onBack}>
        Back
      </button>
      <button
        type="button"
        data-testid="open-session"
        onClick={() =>
          onOpenSession({
            id: 'sess-1',
          })
        }
      >
        Open
      </button>
    </div>
  ),
}));

vi.mock('./components/QualityMetricsPage', () => ({
  QualityMetricsPage: () => <div data-testid="quality-metrics-page" />,
}));

vi.mock('./components/ThemeProvider', () => ({
  ThemeProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

vi.mock('./components/ui/sonner', () => ({
  Toaster: () => <div data-testid="toaster" />,
}));

import App from './App';

describe('App Component (F31 optional Auth)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    workSessionMocks.listLocalWorkSessions.mockResolvedValue({
      items: [],
      total: 0,
      page: 1,
      limit: 20,
    });
    workSessionMocks.migrateGuestSessionStorageToIndexedDb.mockResolvedValue({
      migrated: false,
      sessionId: null,
    });
    vi.unstubAllEnvs();
    vi.stubEnv('VITE_API_BASE_URL', 'https://api.example.onrender.com');
  });

  it('boots to converter as guest with optional Sign in', () => {
    render(<App />);
    expect(screen.getByTestId('file-converter')).toBeInTheDocument();
    expect(screen.queryByTestId('login-view')).not.toBeInTheDocument();
    expect(screen.getByTestId('sign-in-button')).toBeInTheDocument();
  });

  it('opens login UX from Sign in without blocking convert return path', async () => {
    const user = userEvent.setup();
    render(<App />);
    await user.click(screen.getByTestId('sign-in-button'));
    expect(screen.getByTestId('login-view')).toBeInTheDocument();
    await user.click(
      screen.getByRole('button', { name: /continue without signing in/i }),
    );
    expect(screen.getByTestId('file-converter')).toBeInTheDocument();
  });

  it('shows toaster and reports missing API base env in production', () => {
    const consoleErrorSpy = vi
      .spyOn(console, 'error')
      .mockImplementation(() => undefined);
    vi.unstubAllEnvs();
    vi.stubEnv('MODE', 'production');
    vi.stubEnv('VITE_API_BASE_URL', '');

    render(<App />);

    expect(screen.getByTestId('toaster')).toBeInTheDocument();
    expect(consoleErrorSpy).toHaveBeenCalledTimes(1);
    expect(toastMocks.error).toHaveBeenCalledTimes(1);
    consoleErrorSpy.mockRestore();
  });

  it('opens history view and returns to converter', async () => {
    const user = userEvent.setup();
    render(<App />);
    await user.click(screen.getByTestId('open-history'));
    expect(screen.getByTestId('history-view')).toBeInTheDocument();
    await user.click(screen.getByTestId('back-converter'));
    expect(screen.getByTestId('file-converter')).toBeInTheDocument();
  });

  it('reaches Quality metrics via primary shell nav (TC-EV054-001)', async () => {
    const user = userEvent.setup();
    render(<App />);

    expect(screen.getByTestId('app-shell-nav')).toBeInTheDocument();
    expect(screen.getByTestId('shell-nav-converter')).toHaveAttribute(
      'aria-selected',
      'true',
    );

    await user.click(screen.getByTestId('shell-nav-quality'));
    expect(screen.getByTestId('quality-metrics-page')).toBeInTheDocument();
    expect(screen.queryByTestId('file-converter')).not.toBeInTheDocument();
    expect(screen.getByTestId('shell-nav-quality')).toHaveAttribute(
      'aria-selected',
      'true',
    );

    await user.click(screen.getByTestId('shell-nav-history'));
    expect(screen.getByTestId('history-view')).toBeInTheDocument();
    expect(screen.queryByTestId('quality-metrics-page')).not.toBeInTheDocument();
  });

  it('resumes an active draft from IndexedDB on load', async () => {
    workSessionMocks.listLocalWorkSessions.mockResolvedValue({
      items: [
        {
          id: 'active-1',
          status: 'wip',
          deleted_at: null,
          title: 'Draft',
        },
      ],
      total: 1,
      page: 1,
      limit: 20,
    });

    render(<App />);

    await waitFor(() => {
      expect(workSessionMocks.listLocalWorkSessions).toHaveBeenCalled();
    });
    expect(screen.getByTestId('file-converter')).toBeInTheDocument();
  });

  it('runs one-time guest sessionStorage migrate on init (E17-14)', async () => {
    render(<App />);
    await waitFor(() => {
      expect(workSessionMocks.migrateGuestSessionStorageToIndexedDb).toHaveBeenCalled();
    });
  });

  it('logs work session init failures without crashing', async () => {
    const consoleErrorSpy = vi
      .spyOn(console, 'error')
      .mockImplementation(() => undefined);
    workSessionMocks.listLocalWorkSessions.mockRejectedValueOnce(new Error('idb down'));
    render(<App />);
    await waitFor(() => {
      expect(consoleErrorSpy).toHaveBeenCalled();
    });
    expect(screen.getByTestId('file-converter')).toBeInTheDocument();
    consoleErrorSpy.mockRestore();
  });
});

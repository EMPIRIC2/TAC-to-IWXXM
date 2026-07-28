/* eslint-disable @typescript-eslint/no-explicit-any */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

const authServiceMocks = vi.hoisted(() => ({
  isLoggedIn: vi.fn(),
  logout: vi.fn(),
  getAccessToken: vi.fn(),
}));

const toastMocks = vi.hoisted(() => ({
  error: vi.fn(),
}));

const workSessionMocks = vi.hoisted(() => ({
  listLocalWorkSessions: vi.fn(),
  migrateGuestSessionStorageToIndexedDb: vi.fn(),
}));

// Setup all mocks FIRST before any imports
vi.mock('/utils/supabase/client', () => {
  return {
    supabase: {
      auth: {
        onAuthStateChange: vi
          .fn()
          .mockReturnValue({ data: { subscription: { unsubscribe: vi.fn() } } }),
        getSession: vi.fn(() =>
          Promise.resolve({ data: { session: null }, error: null }),
        ),
        signOut: vi.fn(() => Promise.resolve({ error: null })),
      },
    },
  };
});

vi.mock('@/utils/authService', () => ({
  isLoggedIn: authServiceMocks.isLoggedIn,
  logout: authServiceMocks.logout,
  getAccessToken: authServiceMocks.getAccessToken,
}));

vi.mock('@/utils/localWorkSessionStore', () => ({
  listLocalWorkSessions: workSessionMocks.listLocalWorkSessions,
  migrateGuestSessionStorageToIndexedDb:
    workSessionMocks.migrateGuestSessionStorageToIndexedDb,
}));

vi.mock('sonner', async (importOriginal) => {
  const mod = await importOriginal<typeof import('sonner')>();
  return {
    ...mod,
    toast: {
      ...mod.toast,
      error: toastMocks.error,
    },
  };
});

vi.mock('./components/FileConverter', () => ({
  FileConverter: ({
    onLogout,
    userEmail,
    onSwitchToAdmin,
    onOpenHistory,
    onNewMetar,
    onSessionUpdated,
  }: any) => (
    <div data-testid="file-converter">
      <div>{userEmail}</div>
      <button onClick={onLogout} data-testid="logout-btn">
        Logout
      </button>
      {onSwitchToAdmin && (
        <button onClick={onSwitchToAdmin} data-testid="admin-btn">
          Admin
        </button>
      )}
      {onOpenHistory && (
        <button onClick={onOpenHistory} data-testid="open-history">
          History
        </button>
      )}
      {onNewMetar && (
        <button onClick={onNewMetar} data-testid="new-metar">
          New METAR
        </button>
      )}
      {onSessionUpdated && (
        <button
          onClick={() =>
            onSessionUpdated({
              id: 'sess-updated',
              user_id: 'user-1',
              product: 'metar',
              status: 'wip',
              title: 'Updated',
              manual_tac: '',
              pending_files: [],
              converted_results: [],
              errors: [],
              issues: [],
              conversion_params: {},
              kv_upload_key: null,
              deleted_at: null,
              created_at: '2026-06-24T00:00:00Z',
              updated_at: '2026-06-24T00:00:01Z',
            })
          }
          data-testid="session-updated"
        >
          Session Updated
        </button>
      )}
    </div>
  ),
}));

vi.mock('./components/MyMetarsPage', () => ({
  MyMetarsPage: ({ onBack, onOpenSession }: any) => (
    <div data-testid="history-view">
      <button onClick={onBack} data-testid="history-back">
        Back
      </button>
      <button
        onClick={() =>
          onOpenSession({
            id: 'sess-history',
            user_id: 'user-1',
            product: 'metar',
            status: 'draft',
            title: 'From history',
            manual_tac: 'METAR',
            pending_files: [],
            converted_results: [],
            errors: [],
            issues: [],
            conversion_params: {},
            kv_upload_key: null,
            deleted_at: null,
            created_at: '2026-06-24T00:00:00Z',
            updated_at: '2026-06-24T00:00:00Z',
          })
        }
        data-testid="open-history-session"
      >
        Open session
      </button>
    </div>
  ),
}));

vi.mock('./components/auth/Login', () => ({
  Login: ({
    onLogin,
    onSwitchToRegister,
    onForgotPassword,
    onContinueAsGuest,
  }: any) => (
    <div data-testid="login-view">
      <button
        onClick={() => onLogin('test@example.com', false, 'token', false)}
        data-testid="do-login"
      >
        Login
      </button>
      <button
        onClick={() => onLogin('admin@example.com', false, 'token', true)}
        data-testid="do-admin-login"
      >
        Admin Login
      </button>
      <button
        onClick={() => onLogin('pending@example.com', true, 'token', false)}
        data-testid="do-login-requires-verify"
      >
        Login Needs Verify
      </button>
      <button onClick={onSwitchToRegister} data-testid="switch-register">
        Register
      </button>
      <button onClick={onForgotPassword} data-testid="forgot-password">
        Reset
      </button>
      {onContinueAsGuest && (
        <button onClick={onContinueAsGuest} data-testid="continue-guest">
          Continue as guest
        </button>
      )}
    </div>
  ),
}));

vi.mock('./components/auth/Register', () => ({
  Register: ({ onRegister, onSwitchToLogin }: any) => (
    <div data-testid="register-view">
      <button onClick={() => onRegister('new@example.com')} data-testid="do-register">
        Register
      </button>
      <button onClick={onSwitchToLogin} data-testid="switch-login">
        Login
      </button>
    </div>
  ),
}));

vi.mock('./components/auth/PasswordReset', () => ({
  PasswordReset: ({ onBackToLogin }: any) => (
    <div data-testid="reset-view">
      <button onClick={onBackToLogin} data-testid="back-to-login">
        Back to Login
      </button>
    </div>
  ),
}));

vi.mock('./components/auth/EmailVerification', () => ({
  EmailVerification: ({ email, onVerified, onBackToLogin }: any) => (
    <div data-testid="verify-view">
      <div>{email}</div>
      <button
        onClick={() => onVerified('token', false)}
        data-testid="verify-email-user"
      >
        Verify User
      </button>
      <button
        onClick={() => onVerified('token', true)}
        data-testid="verify-email-admin"
      >
        Verify Admin
      </button>
      <button onClick={onBackToLogin} data-testid="verify-back">
        Back
      </button>
    </div>
  ),
}));

vi.mock('./components/auth/AuthCallback', () => ({
  AuthCallback: ({ onLogin }: any) => (
    <div data-testid="callback-view">
      <button
        onClick={() => onLogin('callback@example.com', false, 'token', false)}
        data-testid="callback-login"
      >
        Callback Login
      </button>
      <button
        onClick={() => onLogin('callback-admin@example.com', false, 'token', true)}
        data-testid="callback-login-admin"
      >
        Callback Admin Login
      </button>
    </div>
  ),
}));

vi.mock('./components/admin/AdminDashboard', () => ({
  AdminDashboard: ({ onLogout, userEmail, onSwitchToConverter }: any) => (
    <div data-testid="admin-dashboard">
      <div>{userEmail}</div>
      <button onClick={onLogout} data-testid="admin-logout">
        Admin Logout
      </button>
      <button onClick={onSwitchToConverter} data-testid="switch-converter">
        Converter
      </button>
    </div>
  ),
}));

vi.mock('./components/ui/sonner', () => ({
  Toaster: () => <div data-testid="toaster" />,
}));

// Now import App and mocked dependencies
import App from './App';

describe('App Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    authServiceMocks.isLoggedIn.mockReturnValue(false);
    authServiceMocks.getAccessToken.mockReturnValue(null);
    authServiceMocks.logout.mockResolvedValue(undefined);
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

  describe('Rendering and Initial State', () => {
    it('renders login view by default when not logged in', () => {
      const { container } = render(<App />);
      expect(container).toBeTruthy();
      expect(screen.getByTestId('login-view')).toBeInTheDocument();
      expect(authServiceMocks.isLoggedIn).toHaveBeenCalledTimes(1);
    });

    it('renders converter by default when already logged in', () => {
      authServiceMocks.isLoggedIn.mockReturnValue(true);
      render(<App />);

      expect(screen.getByTestId('file-converter')).toBeInTheDocument();
      expect(screen.queryByTestId('login-view')).not.toBeInTheDocument();
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

    it('reports missing API base env when value is whitespace in production', () => {
      const consoleErrorSpy = vi
        .spyOn(console, 'error')
        .mockImplementation(() => undefined);
      vi.stubEnv('MODE', 'production');
      vi.stubEnv('VITE_API_BASE_URL', '   ');

      render(<App />);

      expect(consoleErrorSpy).toHaveBeenCalledTimes(1);
      expect(toastMocks.error).toHaveBeenCalledTimes(1);

      consoleErrorSpy.mockRestore();
    });

    it('reports missing env once per mount in production', () => {
      const consoleErrorSpy = vi
        .spyOn(console, 'error')
        .mockImplementation(() => undefined);
      vi.stubEnv('MODE', 'production');
      vi.stubEnv('VITE_API_BASE_URL', '');

      const first = render(<App />);
      first.unmount();
      render(<App />);

      expect(consoleErrorSpy).toHaveBeenCalledTimes(2);
      expect(toastMocks.error).toHaveBeenCalledTimes(2);

      consoleErrorSpy.mockRestore();
    });
  });

  describe('Callback Edge Paths', () => {
    it('routes callback login to converter view', async () => {
      const user = userEvent.setup();
      window.history.pushState({}, '', '/auth/callback');

      render(<App />);
      expect(await screen.findByTestId('callback-view')).toBeInTheDocument();

      await user.click(screen.getByTestId('callback-login'));
      expect(await screen.findByTestId('file-converter')).toBeInTheDocument();

      window.history.pushState({}, '', '/');
    });

    it('routes callback admin login to converter (admin dashboard removed)', async () => {
      const user = userEvent.setup();
      window.history.pushState({}, '', '/auth/callback');

      render(<App />);
      expect(await screen.findByTestId('callback-view')).toBeInTheDocument();

      await user.click(screen.getByTestId('callback-login-admin'));
      expect(await screen.findByTestId('file-converter')).toBeInTheDocument();
      expect(screen.queryByTestId('admin-dashboard')).not.toBeInTheDocument();

      window.history.pushState({}, '', '/');
    });
  });

  describe('Auth State Transitions', () => {
    it('switches login to register and back to login', async () => {
      const user = userEvent.setup();
      render(<App />);

      await user.click(screen.getByTestId('switch-register'));
      expect(screen.getByTestId('register-view')).toBeInTheDocument();

      await user.click(screen.getByTestId('switch-login'));
      expect(screen.getByTestId('login-view')).toBeInTheDocument();
    });

    it('switches login to password reset and back to login', async () => {
      const user = userEvent.setup();
      render(<App />);

      await user.click(screen.getByTestId('forgot-password'));
      expect(screen.getByTestId('reset-view')).toBeInTheDocument();

      await user.click(screen.getByTestId('back-to-login'));
      expect(screen.getByTestId('login-view')).toBeInTheDocument();
    });

    it('routes to verify view after register flow', async () => {
      const user = userEvent.setup();
      render(<App />);

      await user.click(screen.getByTestId('switch-register'));
      await user.click(screen.getByTestId('do-register'));

      expect(screen.getByTestId('verify-view')).toBeInTheDocument();
      expect(screen.getByText('new@example.com')).toBeInTheDocument();
    });

    it('routes verify flow to converter for non-admin user', async () => {
      const user = userEvent.setup();
      render(<App />);

      await user.click(screen.getByTestId('switch-register'));
      await user.click(screen.getByTestId('do-register'));
      await user.click(screen.getByTestId('verify-email-user'));

      expect(screen.getByTestId('file-converter')).toBeInTheDocument();
      expect(screen.queryByTestId('admin-dashboard')).not.toBeInTheDocument();
    });

    it('routes verify flow to converter even for former admin flag', async () => {
      const user = userEvent.setup();
      render(<App />);

      await user.click(screen.getByTestId('switch-register'));
      await user.click(screen.getByTestId('do-register'));
      await user.click(screen.getByTestId('verify-email-admin'));

      expect(screen.getByTestId('file-converter')).toBeInTheDocument();
      expect(screen.queryByTestId('admin-dashboard')).not.toBeInTheDocument();
    });

    it('returns from verify view to login', async () => {
      const user = userEvent.setup();
      render(<App />);

      await user.click(screen.getByTestId('switch-register'));
      await user.click(screen.getByTestId('do-register'));
      await user.click(screen.getByTestId('verify-back'));

      expect(screen.getByTestId('login-view')).toBeInTheDocument();
      expect(screen.queryByTestId('verify-view')).not.toBeInTheDocument();
    });

    it('keeps regular login users on converter view', async () => {
      const user = userEvent.setup();
      render(<App />);

      await user.click(screen.getByTestId('do-login'));

      expect(screen.getByTestId('file-converter')).toBeInTheDocument();
      expect(screen.queryByTestId('admin-btn')).not.toBeInTheDocument();
    });

    it('routes former admin-flag login to converter (no admin dashboard)', async () => {
      const user = userEvent.setup();
      render(<App />);

      await user.click(screen.getByTestId('do-admin-login'));
      expect(screen.getByTestId('file-converter')).toBeInTheDocument();
      expect(screen.queryByTestId('admin-dashboard')).not.toBeInTheDocument();
      expect(screen.queryByTestId('admin-btn')).not.toBeInTheDocument();
    });

    it('does not expose switch-back-to-admin after login', async () => {
      const user = userEvent.setup();
      render(<App />);

      await user.click(screen.getByTestId('do-admin-login'));
      expect(screen.getByTestId('file-converter')).toBeInTheDocument();
      expect(screen.queryByTestId('admin-btn')).not.toBeInTheDocument();
    });

    it('routes login to verify when login response requires verification', async () => {
      const user = userEvent.setup();
      render(<App />);

      await user.click(screen.getByTestId('do-login-requires-verify'));

      expect(screen.getByTestId('verify-view')).toBeInTheDocument();
      expect(screen.getByText('pending@example.com')).toBeInTheDocument();
    });
  });

  describe('Logout Behavior', () => {
    it('logs out from converter and returns to login', async () => {
      const user = userEvent.setup();
      render(<App />);

      await user.click(screen.getByTestId('do-login'));
      await user.click(screen.getByTestId('logout-btn'));

      expect(authServiceMocks.logout).toHaveBeenCalledTimes(1);
      expect(screen.getByTestId('login-view')).toBeInTheDocument();
    });

    it('logs out after former admin-flag login and returns to login', async () => {
      const user = userEvent.setup();
      render(<App />);

      await user.click(screen.getByTestId('do-admin-login'));
      await user.click(screen.getByTestId('logout-btn'));

      expect(authServiceMocks.logout).toHaveBeenCalledTimes(1);
      expect(screen.getByTestId('login-view')).toBeInTheDocument();
      expect(screen.queryByTestId('admin-dashboard')).not.toBeInTheDocument();
    });

    it('resets to login even when logout service throws', async () => {
      const user = userEvent.setup();
      const consoleErrorSpy = vi
        .spyOn(console, 'error')
        .mockImplementation(() => undefined);
      authServiceMocks.logout.mockRejectedValueOnce(new Error('logout failed'));

      render(<App />);
      await user.click(screen.getByTestId('do-login'));
      await user.click(screen.getByTestId('logout-btn'));

      expect(authServiceMocks.logout).toHaveBeenCalledTimes(1);
      expect(screen.getByTestId('login-view')).toBeInTheDocument();

      consoleErrorSpy.mockRestore();
    });
  });

  describe('F5 work history navigation', () => {
    it('opens history view and returns to converter with selected session', async () => {
      const user = userEvent.setup();
      render(<App />);

      await user.click(screen.getByTestId('do-login'));
      await user.click(screen.getByTestId('open-history'));
      expect(screen.getByTestId('history-view')).toBeInTheDocument();

      await user.click(screen.getByTestId('open-history-session'));
      expect(screen.getByTestId('file-converter')).toBeInTheDocument();

      await user.click(screen.getByTestId('new-metar'));
      await user.click(screen.getByTestId('session-updated'));
      await user.click(screen.getByTestId('open-history'));
      await user.click(screen.getByTestId('history-back'));
      expect(screen.getByTestId('file-converter')).toBeInTheDocument();
    });

    it('resumes an active draft from IndexedDB on load', async () => {
      workSessionMocks.listLocalWorkSessions.mockResolvedValue({
        items: [
          {
            id: 'sess-resume',
            user_id: 'local',
            product: 'metar',
            status: 'draft',
            title: 'Resume me',
            manual_tac: 'METAR',
            pending_files: [],
            converted_results: [],
            errors: [],
            issues: [],
            conversion_params: {},
            kv_upload_key: null,
            deleted_at: null,
            created_at: '2026-06-24T00:00:00Z',
            updated_at: '2026-06-24T00:00:00Z',
          },
        ],
        total: 1,
        page: 1,
        limit: 20,
      });

      const user = userEvent.setup();
      render(<App />);
      await user.click(screen.getByTestId('do-login'));

      await vi.waitFor(() => {
        expect(workSessionMocks.listLocalWorkSessions).toHaveBeenCalled();
        expect(
          workSessionMocks.migrateGuestSessionStorageToIndexedDb,
        ).toHaveBeenCalled();
      });
    });

    it('runs one-time guest sessionStorage migrate on init (E17-14)', async () => {
      workSessionMocks.migrateGuestSessionStorageToIndexedDb.mockResolvedValue({
        migrated: true,
        sessionId: 'migrated-1',
      });

      const user = userEvent.setup();
      render(<App />);
      await user.click(screen.getByTestId('do-login'));

      await vi.waitFor(() => {
        expect(
          workSessionMocks.migrateGuestSessionStorageToIndexedDb,
        ).toHaveBeenCalled();
      });
    });

    it('allows guest converter without authentication', async () => {
      const user = userEvent.setup();
      render(<App />);

      await user.click(screen.getByTestId('continue-guest'));
      expect(screen.getByTestId('file-converter')).toBeInTheDocument();
      expect(screen.getByText('Guest')).toBeInTheDocument();

      await user.click(screen.getByTestId('logout-btn'));
      expect(screen.getByTestId('login-view')).toBeInTheDocument();
    });

    it('logs work session init failures without crashing', async () => {
      const consoleErrorSpy = vi
        .spyOn(console, 'error')
        .mockImplementation(() => undefined);
      workSessionMocks.listLocalWorkSessions.mockRejectedValue(
        new Error('init failed'),
      );

      render(<App />);

      await waitFor(() => {
        expect(workSessionMocks.listLocalWorkSessions).toHaveBeenCalled();
        expect(consoleErrorSpy).toHaveBeenCalled();
      });
      expect(consoleErrorSpy.mock.calls[0]?.[0]).toBe(
        '[App] work session init failed:',
      );

      consoleErrorSpy.mockRestore();
    });
  });
});

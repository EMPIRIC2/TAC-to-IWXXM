import { useState, useEffect, useLayoutEffect, useRef, useCallback } from 'react';
import { FileConverter } from './components/FileConverter';
import { MyMetarsPage } from './components/MyMetarsPage';
import { Login } from './components/auth/Login';
import { Register } from './components/auth/Register';
import { EmailVerification } from './components/auth/EmailVerification';
import { AuthCallback } from './components/auth/AuthCallback';
import { PasswordReset } from './components/auth/PasswordReset';
import { Toaster } from './components/ui/sonner';
import { toast } from 'sonner';
import { ThemeProvider } from './components/ThemeProvider';
import { getAccessToken, isLoggedIn, logout } from '@/utils/authService';
import { autoUploadEligibleLocalDrafts } from '@/utils/autoUploadLocalDrafts';

import { requireApiBaseUrl } from '@/utils/apiBase';
import type { WorkSession } from '@metar/shared';
import {
  listLocalWorkSessions,
  migrateGuestSessionStorageToIndexedDb,
} from '@/utils/localWorkSessionStore';
import { listWorkSessions } from '@/utils/workSessionApi';

/**
 * Validate required environment variables on app load.
 * F31 — public convert + optional Auth; API base still required.
 */
function validateApiEnv() {
  try {
    requireApiBaseUrl();
    return true;
  } catch {
    const errorMsg =
      '❌ Missing VITE_API_BASE_URL environment variable. Please check .env.local file.';
    console.error(errorMsg);
    toast.error(errorMsg);
    return false;
  }
}

type AppView =
  | 'converter'
  | 'history'
  | 'login'
  | 'register'
  | 'verify'
  | 'callback'
  | 'reset';

/**
 * Operator shell — boots to the public converter (guest). Optional Supabase Auth
 * login is available for long-term server sessions (F31 / F21 Amended).
 */
function App() {
  const initiallyLoggedIn = isLoggedIn();
  const [currentView, setCurrentView] = useState<AppView>('converter');
  const [userEmail, setUserEmail] = useState('');
  const [isAuthenticated, setIsAuthenticated] = useState(initiallyLoggedIn);
  const [accessToken, setAccessToken] = useState(() =>
    initiallyLoggedIn ? getAccessToken() || '' : '',
  );
  const [activeWorkSessionId, setActiveWorkSessionId] = useState<string | null>(null);
  const [loadedWorkSession, setLoadedWorkSession] = useState<WorkSession | null>(null);
  const sessionInitRef = useRef<string | null>(null);

  useEffect(() => {
    validateApiEnv();
  }, []);

  const initializeWorkSessions = useCallback(async (token?: string | null) => {
    if (sessionInitRef.current === 'done') {
      return;
    }
    sessionInitRef.current = 'done';

    try {
      await migrateGuestSessionStorageToIndexedDb();
      if (token) {
        const response = await listWorkSessions(token, { limit: 20 });
        const activeSession =
          response.items.find(
            (session) => session.status !== 'finished' && session.deleted_at == null,
          ) ?? null;
        if (activeSession) {
          setActiveWorkSessionId(activeSession.id);
          setLoadedWorkSession(activeSession);
        }
        return;
      }

      const response = await listLocalWorkSessions({ limit: 20 });
      const activeSession =
        response.items.find(
          (session) => session.status !== 'finished' && session.deleted_at == null,
        ) ?? null;

      if (activeSession) {
        setActiveWorkSessionId(activeSession.id);
        setLoadedWorkSession(activeSession);
      }
    } catch (error) {
      console.error('[App] work session init failed:', error);
      sessionInitRef.current = null;
    }
  }, []);

  /* eslint-disable react-hooks/set-state-in-effect -- F7.h resume IndexedDB on load */
  useEffect(() => {
    const token = initiallyLoggedIn ? getAccessToken() : null;
    void initializeWorkSessions(token);
  }, [initializeWorkSessions, initiallyLoggedIn]);
  /* eslint-enable react-hooks/set-state-in-effect */

  useLayoutEffect(() => {
    if (window.location.pathname.includes('/auth/callback')) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setCurrentView('callback');
    }
  }, []);

  const runPostLoginHydration = useCallback(
    async (token: string) => {
      try {
        const result = await autoUploadEligibleLocalDrafts(token);
        if (result.uploaded > 0) {
          toast.success(
            `Uploaded ${result.uploaded} local draft${result.uploaded === 1 ? '' : 's'} to your account`,
          );
        }
        if (result.errors.length > 0) {
          toast.error(
            `Could not upload ${result.errors.length} local draft${result.errors.length === 1 ? '' : 's'}`,
          );
        }
      } catch (error) {
        console.error('[App] auto-upload on login failed:', error);
        toast.error('Failed to upload local drafts after sign-in');
      }
      sessionInitRef.current = null;
      setActiveWorkSessionId(null);
      setLoadedWorkSession(null);
      await initializeWorkSessions(token);
    },
    [initializeWorkSessions],
  );

  const handleLogin = (
    email: string,
    needsVerification: boolean,
    token?: string,
    _adminStatus?: boolean,
  ) => {
    setUserEmail(email);
    const jwt = token || getAccessToken() || '';
    setAccessToken(jwt);

    if (needsVerification) {
      setCurrentView('verify');
    } else {
      setIsAuthenticated(true);
      setCurrentView('converter');
      if (jwt) {
        void runPostLoginHydration(jwt);
      }
    }
  };

  const handleRegister = (email: string) => {
    setUserEmail(email);
    setCurrentView('verify');
  };

  const handleVerified = (token?: string, _adminStatus?: boolean) => {
    const jwt = token || getAccessToken() || '';
    setIsAuthenticated(true);
    setAccessToken(jwt);
    setCurrentView('converter');
    if (jwt) {
      void runPostLoginHydration(jwt);
    }
  };

  const handleLogout = async () => {
    try {
      await logout();
    } catch (error) {
      console.error('Logout error:', error);
    }

    setIsAuthenticated(false);
    setUserEmail('');
    setAccessToken('');
    setActiveWorkSessionId(null);
    setLoadedWorkSession(null);
    sessionInitRef.current = null;
    setCurrentView('converter');
    void initializeWorkSessions(null);
  };

  const handleSwitchToConverter = () => {
    setCurrentView('converter');
  };

  const handleOpenHistory = () => {
    setCurrentView('history');
  };

  const handleRequestLogin = () => {
    setCurrentView('login');
  };

  const handleContinueAsGuest = () => {
    setCurrentView('converter');
  };

  const handleLoadWorkSession = (session: WorkSession) => {
    setActiveWorkSessionId(session.id);
    setLoadedWorkSession(session);
    setCurrentView('converter');
  };

  const handleNewMetar = () => {
    setActiveWorkSessionId(null);
    setLoadedWorkSession(null);
  };

  const handleSessionUpdated = (session: WorkSession) => {
    setLoadedWorkSession(session);
    setActiveWorkSessionId(session.id);
  };

  const isGuest = !isAuthenticated;

  return (
    <ThemeProvider>
      {currentView === 'login' && (
        <Login
          onLogin={handleLogin}
          onSwitchToRegister={() => setCurrentView('register')}
          onForgotPassword={() => setCurrentView('reset')}
          onContinueAsGuest={handleContinueAsGuest}
        />
      )}

      {currentView === 'register' && (
        <Register
          onRegister={handleRegister}
          onSwitchToLogin={() => setCurrentView('login')}
        />
      )}

      {currentView === 'reset' && (
        <PasswordReset onBackToLogin={() => setCurrentView('login')} />
      )}

      {currentView === 'verify' && (
        <EmailVerification
          email={userEmail}
          onVerified={handleVerified}
          onBackToLogin={() => setCurrentView('login')}
        />
      )}

      {currentView === 'converter' && (
        <FileConverter
          onLogout={handleLogout}
          userEmail={isGuest ? 'Guest' : userEmail || 'Operator'}
          accessToken={isAuthenticated ? accessToken : undefined}
          isGuest={isGuest}
          onRequestLogin={handleRequestLogin}
          onOpenHistory={handleOpenHistory}
          onLoadWorkSession={handleLoadWorkSession}
          onNewMetar={handleNewMetar}
          onSessionUpdated={handleSessionUpdated}
          onActiveSessionIdChange={setActiveWorkSessionId}
          activeWorkSessionId={activeWorkSessionId}
          loadedWorkSession={loadedWorkSession}
        />
      )}

      {currentView === 'history' && (
        <MyMetarsPage
          accessToken={isAuthenticated ? accessToken : undefined}
          userEmail={isAuthenticated ? userEmail || 'Operator' : 'Local history'}
          onBack={handleSwitchToConverter}
          onOpenSession={handleLoadWorkSession}
        />
      )}

      {currentView === 'callback' && (
        <AuthCallback
          onLogin={handleLogin}
          onRegister={handleRegister}
          onVerified={handleVerified}
        />
      )}

      <Toaster />
    </ThemeProvider>
  );
}

export default App;

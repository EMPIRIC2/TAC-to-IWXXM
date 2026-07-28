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

import { requireApiBaseUrl } from '@/utils/apiBase';
import { isAuthDisabled } from '@/utils/runtime-config';
import type { WorkSession } from '@metar/shared';
import {
  listLocalWorkSessions,
  migrateGuestSessionStorageToIndexedDb,
} from '@/utils/localWorkSessionStore';

// Validate required environment variables on app load
function validateAuthEnv() {
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

type AuthView =
  | 'login'
  | 'register'
  | 'verify'
  | 'converter'
  | 'history'
  | 'callback'
  | 'reset';

function App() {
  const disableAuth = isAuthDisabled();
  const initialLoggedIn = disableAuth || isLoggedIn();
  const [currentView, setCurrentView] = useState<AuthView>(() =>
    initialLoggedIn ? 'converter' : 'login',
  );
  const [userEmail, setUserEmail] = useState('');
  const [isAuthenticated, setIsAuthenticated] = useState(initialLoggedIn);
  const [accessToken, setAccessToken] = useState(() =>
    disableAuth ? 'dev-bypass-token' : getAccessToken() || '',
  );
  const [activeWorkSessionId, setActiveWorkSessionId] = useState<string | null>(null);
  const [loadedWorkSession, setLoadedWorkSession] = useState<WorkSession | null>(null);
  const sessionInitRef = useRef<string | null>(null);

  // Validate environment on mount
  useEffect(() => {
    validateAuthEnv();
  }, []);

  const initializeWorkSessions = useCallback(async () => {
    if (sessionInitRef.current === 'done') {
      return;
    }
    sessionInitRef.current = 'done';

    try {
      await migrateGuestSessionStorageToIndexedDb();
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
    void initializeWorkSessions();
  }, [initializeWorkSessions]);
  /* eslint-enable react-hooks/set-state-in-effect */

  // Handle auth callback route
  useLayoutEffect(() => {
    if (window.location.pathname.includes('/auth/callback')) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setCurrentView('callback');
    }
  }, []);

  const handleLogin = (
    email: string,
    needsVerification: boolean,
    token?: string,
    _adminStatus?: boolean,
  ) => {
    console.log(`🔐 handleLogin called with:`, {
      email,
      needsVerification,
      hasToken: !!token,
    });
    setUserEmail(email);
    setAccessToken(token || 'auth-service-token');

    if (needsVerification) {
      setCurrentView('verify');
    } else {
      setIsAuthenticated(true);
      sessionInitRef.current = null;
      setCurrentView('converter');
      void initializeWorkSessions();
    }
  };

  const handleRegister = (email: string) => {
    setUserEmail(email);
    setCurrentView('verify');
  };

  const handleVerified = (token?: string, _adminStatus?: boolean) => {
    setIsAuthenticated(true);
    setAccessToken(token || '');
    sessionInitRef.current = null;
    setCurrentView('converter');
    void initializeWorkSessions();
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
    setCurrentView('login');
  };

  const handleSwitchToConverter = () => {
    setCurrentView('converter');
  };

  const handleOpenHistory = () => {
    setCurrentView('history');
  };

  const handleContinueAsGuest = () => {
    setCurrentView('converter');
  };

  const handleRequestLogin = () => {
    setCurrentView('login');
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

  const isGuestConverter =
    currentView === 'converter' && !isAuthenticated && !disableAuth;

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

      {currentView === 'converter' &&
        (isAuthenticated || isGuestConverter || disableAuth) && (
          <FileConverter
            onLogout={isGuestConverter ? handleRequestLogin : handleLogout}
            userEmail={isGuestConverter ? 'Guest' : userEmail}
            accessToken={isAuthenticated ? accessToken : undefined}
            isGuest={isGuestConverter}
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
          userEmail={isAuthenticated ? userEmail || 'Local history' : 'Local history'}
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

import { useState, useEffect, useLayoutEffect, useRef, useCallback } from 'react';
import { FileConverter } from './components/FileConverter';
import { MyMetarsPage } from './components/MyMetarsPage';
import { Login } from './components/auth/Login';
import { Register } from './components/auth/Register';
import { EmailVerification } from './components/auth/EmailVerification';
import { AuthCallback } from './components/auth/AuthCallback';
import { AdminDashboard } from './components/admin/AdminDashboard';
import { PasswordReset } from './components/auth/PasswordReset';
import { Toaster } from './components/ui/sonner';
import { toast } from 'sonner';
import { ThemeProvider } from './components/ThemeProvider';
import { isLoggedIn, logout } from '@/utils/authService';

import { requireApiBaseUrl } from '@/utils/apiBase';
import { isAuthDisabled } from '@/utils/runtime-config';
import type { WorkSession } from '@metar/shared';
import { createWorkSession, listWorkSessions } from '@/utils/workSessionApi';
import {
  buildWorkSessionPayload,
  hasConverterContent,
} from '@/utils/workSessionPayload';
import {
  clearGuestConverterState,
  readGuestConverterState,
} from '@/utils/guestConverterState';

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
  | 'admin'
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
    disableAuth ? 'dev-bypass-token' : '',
  );
  const [isAdmin, setIsAdmin] = useState(false);
  const [activeWorkSessionId, setActiveWorkSessionId] = useState<string | null>(null);
  const [loadedWorkSession, setLoadedWorkSession] = useState<WorkSession | null>(null);
  const sessionInitRef = useRef<string | null>(null);

  // Validate environment on mount
  useEffect(() => {
    validateAuthEnv();
  }, []);

  const initializeWorkSessions = useCallback(async (token: string) => {
    if (sessionInitRef.current === token) {
      return;
    }
    sessionInitRef.current = token;

    try {
      const guestSnapshot = readGuestConverterState();
      let activeSession: WorkSession | null = null;

      if (guestSnapshot && hasConverterContent(guestSnapshot)) {
        activeSession = await createWorkSession(
          token,
          buildWorkSessionPayload(guestSnapshot, { status: 'draft' }),
        );
        clearGuestConverterState();
      } else {
        const response = await listWorkSessions(token, { limit: 20 });
        activeSession =
          response.items.find(
            (session) => session.status !== 'finished' && session.deleted_at == null,
          ) ?? null;
      }

      if (activeSession) {
        setActiveWorkSessionId(activeSession.id);
        setLoadedWorkSession(activeSession);
      }
    } catch (error) {
      console.error('[App] work session init failed:', error);
    }
  }, []);

  /* eslint-disable react-hooks/set-state-in-effect -- F5 resume/create work sessions after login or page reload */
  useEffect(() => {
    if (!accessToken || disableAuth) {
      return;
    }
    void initializeWorkSessions(accessToken);
  }, [accessToken, disableAuth, initializeWorkSessions]);
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
    adminStatus?: boolean,
  ) => {
    console.log(`🔐 handleLogin called with:`, {
      email,
      needsVerification,
      adminStatus,
      hasToken: !!token,
    });
    setUserEmail(email);
    setAccessToken(token || 'auth-service-token');
    setIsAdmin(adminStatus || false);

    if (needsVerification) {
      setCurrentView('verify');
    } else {
      setIsAuthenticated(true);
      sessionInitRef.current = null;
      console.log(`DEBUG: Routing to ${adminStatus ? 'admin' : 'converter'} view`);
      setCurrentView(adminStatus ? 'admin' : 'converter');
      if (token) {
        void initializeWorkSessions(token);
      }
    }
  };

  const handleRegister = (email: string) => {
    setUserEmail(email);
    setCurrentView('verify');
  };

  const handleVerified = (token?: string, adminStatus?: boolean) => {
    setIsAuthenticated(true);
    setAccessToken(token || '');
    setIsAdmin(adminStatus || false);
    sessionInitRef.current = null;
    setCurrentView(adminStatus ? 'admin' : 'converter');
    if (token) {
      void initializeWorkSessions(token);
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
    setIsAdmin(false);
    setActiveWorkSessionId(null);
    setLoadedWorkSession(null);
    sessionInitRef.current = null;
    setCurrentView('login');
  };

  const handleSwitchToAdmin = () => {
    setCurrentView('admin');
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
            onSwitchToAdmin={isAdmin ? handleSwitchToAdmin : undefined}
            onOpenHistory={isAuthenticated ? handleOpenHistory : undefined}
            onLoadWorkSession={isAuthenticated ? handleLoadWorkSession : undefined}
            onNewMetar={handleNewMetar}
            onSessionUpdated={handleSessionUpdated}
            onActiveSessionIdChange={setActiveWorkSessionId}
            activeWorkSessionId={activeWorkSessionId}
            loadedWorkSession={loadedWorkSession}
          />
        )}

      {currentView === 'history' && isAuthenticated && (
        <MyMetarsPage
          accessToken={accessToken}
          userEmail={userEmail}
          onBack={handleSwitchToConverter}
          onOpenSession={handleLoadWorkSession}
        />
      )}

      {currentView === 'admin' && isAuthenticated && isAdmin && (
        <AdminDashboard
          onLogout={handleLogout}
          userEmail={userEmail}
          accessToken={accessToken}
          onSwitchToConverter={handleSwitchToConverter}
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

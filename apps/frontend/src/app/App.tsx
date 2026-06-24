import { useState, useEffect, useLayoutEffect } from 'react';
import { FileConverter } from './components/FileConverter';
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

  // Validate environment on mount
  useEffect(() => {
    validateAuthEnv();
  }, []);

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
      // Route admins to admin view, others to converter
      console.log(`DEBUG: Routing to ${adminStatus ? 'admin' : 'converter'} view`);
      setCurrentView(adminStatus ? 'admin' : 'converter');
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
    setCurrentView(adminStatus ? 'admin' : 'converter');
  };

  const handleLogout = async () => {
    // Logout through auth service
    try {
      await logout();
    } catch (error) {
      console.error('Logout error:', error);
    }

    setIsAuthenticated(false);
    setUserEmail('');
    setAccessToken('');
    setIsAdmin(false);
    setCurrentView('login');
  };

  const handleSwitchToAdmin = () => {
    setCurrentView('admin');
  };

  const handleSwitchToConverter = () => {
    setCurrentView('converter');
  };

  return (
    <ThemeProvider>
      {currentView === 'login' && (
        <Login
          onLogin={handleLogin}
          onSwitchToRegister={() => setCurrentView('register')}
          onForgotPassword={() => setCurrentView('reset')}
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

      {currentView === 'converter' && isAuthenticated && (
        <FileConverter
          onLogout={handleLogout}
          userEmail={userEmail}
          accessToken={accessToken}
          onSwitchToAdmin={isAdmin ? handleSwitchToAdmin : undefined}
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

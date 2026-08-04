import { useState, useEffect, useRef, useCallback } from 'react';
import { FileConverter } from './components/FileConverter';
import { MyMetarsPage } from './components/MyMetarsPage';
import { Toaster } from './components/ui/sonner';
import { toast } from 'sonner';
import { ThemeProvider } from './components/ThemeProvider';

import { requireApiBaseUrl } from '@/utils/apiBase';
import type { WorkSession } from '@metar/shared';
import {
  listLocalWorkSessions,
  migrateGuestSessionStorageToIndexedDb,
} from '@/utils/localWorkSessionStore';

/** Validate required environment variables on app load (F21 — no Auth env). */
function validateApiEnv() {
  try {
    requireApiBaseUrl();
    return true;
  } catch {
    const errorMsg =
      '❌ Missing API base URL (/config.json or VITE_API_BASE_URL). Check runtime config.';
    console.error(errorMsg);
    toast.error(errorMsg);
    return false;
  }
}

type AppView = 'converter' | 'history';

function App() {
  const [currentView, setCurrentView] = useState<AppView>('converter');
  const [activeWorkSessionId, setActiveWorkSessionId] = useState<string | null>(null);
  const [loadedWorkSession, setLoadedWorkSession] = useState<WorkSession | null>(null);
  const sessionInitRef = useRef<string | null>(null);

  useEffect(() => {
    validateApiEnv();
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

  const handleSwitchToConverter = () => {
    setCurrentView('converter');
  };

  const handleOpenHistory = () => {
    setCurrentView('history');
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

  return (
    <ThemeProvider>
      {currentView === 'converter' && (
        <FileConverter
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
          userEmail="Local history"
          onBack={handleSwitchToConverter}
          onOpenSession={handleLoadWorkSession}
        />
      )}

      <Toaster />
    </ThemeProvider>
  );
}

export default App;

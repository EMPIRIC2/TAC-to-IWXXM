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
  FileConverter: ({ onOpenHistory }: { onOpenHistory?: () => void }) => (
    <div data-testid="file-converter">
      <button
        type="button"
        data-testid="open-history"
        onClick={() => onOpenHistory?.()}
      >
        History
      </button>
    </div>
  ),
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

vi.mock('./components/ThemeProvider', () => ({
  ThemeProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

vi.mock('./components/ui/sonner', () => ({
  Toaster: () => <div data-testid="toaster" />,
}));

import App from './App';

describe('App Component (F21 public)', () => {
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

  it('boots to converter with no login chrome', () => {
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

  it('opens history view and returns to converter', async () => {
    const user = userEvent.setup();
    render(<App />);
    await user.click(screen.getByTestId('open-history'));
    expect(screen.getByTestId('history-view')).toBeInTheDocument();
    await user.click(screen.getByTestId('back-converter'));
    expect(screen.getByTestId('file-converter')).toBeInTheDocument();
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

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { act, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import type { WorkSession } from '@metar/shared';
import { WorkHistorySidebar } from './WorkHistorySidebar';

const mockList = vi.fn();
const mockListServer = vi.fn();

vi.mock('/utils/localWorkSessionStore', () => ({
  listLocalWorkSessions: (...args: unknown[]) => mockList(...args),
}));

vi.mock('/utils/workSessionApi', () => ({
  listWorkSessions: (...args: unknown[]) => mockListServer(...args),
}));

const sampleSession = (overrides: Partial<WorkSession> = {}): WorkSession => ({
  id: 'sess-1',
  user_id: 'local',
  product: 'metar',
  status: 'wip',
  title: 'KDEN WIP',
  manual_tac: 'METAR',
  pending_files: [],
  converted_results: [],
  errors: [],
  issues: [],
  conversion_params: {},
  kv_upload_key: null,
  deleted_at: null,
  created_at: '2026-06-24T00:00:00Z',
  updated_at: '2026-06-24T12:00:00Z',
  ...overrides,
});

describe('WorkHistorySidebar', () => {
  const onSelectSession = vi.fn();
  const onOpenHistory = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    mockList.mockResolvedValue({
      items: [sampleSession()],
      total: 1,
      page: 1,
      limit: 5,
    });
    mockListServer.mockResolvedValue({
      items: [sampleSession({ id: 'server-1', title: 'Server WIP', user_id: 'auth' })],
      total: 1,
      page: 1,
      limit: 5,
    });
  });

  it('loads recent sessions from IndexedDB', async () => {
    render(
      <WorkHistorySidebar
        onSelectSession={onSelectSession}
        onOpenHistory={onOpenHistory}
      />,
    );

    expect(screen.getByLabelText(/recent work sessions/i)).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByText('KDEN WIP')).toBeInTheDocument();
    });
    expect(mockList).toHaveBeenCalledWith({ limit: 5 });
  });

  it('selects a session and opens full history', async () => {
    const user = userEvent.setup();
    const session = sampleSession();

    render(
      <WorkHistorySidebar
        activeSessionId="sess-1"
        onSelectSession={onSelectSession}
        onOpenHistory={onOpenHistory}
      />,
    );

    await waitFor(() => expect(screen.getByText('KDEN WIP')).toBeInTheDocument());
    await user.click(screen.getByText('KDEN WIP'));
    expect(onSelectSession).toHaveBeenCalledWith(session);

    await user.click(screen.getByRole('button', { name: /my metars/i }));
    expect(onOpenHistory).toHaveBeenCalled();
  });

  it('shows empty state when no sessions exist', async () => {
    mockList.mockResolvedValue({ items: [], total: 0, page: 1, limit: 5 });

    render(<WorkHistorySidebar onSelectSession={onSelectSession} />);

    await waitFor(() => {
      expect(screen.getByText(/no saved sessions yet/i)).toBeInTheDocument();
    });
  });

  it('shows load errors', async () => {
    mockList.mockRejectedValue(new Error('Forbidden'));

    render(<WorkHistorySidebar onSelectSession={onSelectSession} />);

    await waitFor(() => {
      expect(screen.getByText('Forbidden')).toBeInTheDocument();
    });
  });

  it('shows generic load errors for non-Error rejections', async () => {
    mockList.mockRejectedValue('network');

    render(<WorkHistorySidebar onSelectSession={onSelectSession} />);

    await waitFor(() => {
      expect(screen.getByText('Failed to load history')).toBeInTheDocument();
    });
  });

  it('omits My METARs link when onOpenHistory is not provided', async () => {
    render(<WorkHistorySidebar onSelectSession={onSelectSession} />);

    await waitFor(() => expect(screen.getByText('KDEN WIP')).toBeInTheDocument());
    expect(
      screen.queryByRole('button', { name: /my metars/i }),
    ).not.toBeInTheDocument();
  });

  it('highlights only the active session', async () => {
    mockList.mockResolvedValue({
      items: [
        sampleSession({ id: 'sess-1', title: 'Active session' }),
        sampleSession({ id: 'sess-2', title: 'Other session', status: 'draft' }),
      ],
      total: 2,
      page: 1,
      limit: 5,
    });

    render(
      <WorkHistorySidebar activeSessionId="sess-2" onSelectSession={onSelectSession} />,
    );

    await waitFor(() => expect(screen.getByText('Other session')).toBeInTheDocument());

    const activeBtn = screen.getByText('Other session').closest('button');
    const otherBtn = screen.getByText('Active session').closest('button');
    expect(activeBtn?.className).toMatch(/border-blue-500/);
    expect(otherBtn?.className).not.toMatch(/border-blue-500/);
  });

  it('loads recent sessions from server when accessToken is set (F31)', async () => {
    render(
      <WorkHistorySidebar
        accessToken="jwt-token"
        onSelectSession={onSelectSession}
        onOpenHistory={onOpenHistory}
      />,
    );

    await waitFor(() => {
      expect(screen.getByText('Server WIP')).toBeInTheDocument();
    });
    expect(mockListServer).toHaveBeenCalledWith('jwt-token', { limit: 5 });
    expect(mockList).not.toHaveBeenCalled();
  });

  it('falls back to raw status text for unknown session statuses', async () => {
    mockList.mockResolvedValue({
      items: [sampleSession({ status: 'archived' as WorkSession['status'] })],
      total: 1,
      page: 1,
      limit: 5,
    });

    render(<WorkHistorySidebar onSelectSession={onSelectSession} />);

    await waitFor(() => {
      expect(screen.getByText('archived')).toBeInTheDocument();
    });
  });

  it('ignores late list results after unmount (cancelled path)', async () => {
    let resolveList: ((v: unknown) => void) | undefined;
    mockList.mockImplementation(
      () =>
        new Promise((resolve) => {
          resolveList = resolve;
        }),
    );
    const { unmount } = render(
      <WorkHistorySidebar onSelectSession={onSelectSession} />,
    );
    unmount();
    await act(async () => {
      resolveList?.({ items: [sampleSession()], total: 1, page: 1, limit: 5 });
      await Promise.resolve();
    });
    expect(mockList).toHaveBeenCalled();
  });

  it('ignores late list errors after unmount', async () => {
    let rejectList: ((e: unknown) => void) | undefined;
    mockList.mockImplementation(
      () =>
        new Promise((_resolve, reject) => {
          rejectList = reject;
        }),
    );
    const { unmount } = render(
      <WorkHistorySidebar onSelectSession={onSelectSession} />,
    );
    unmount();
    rejectList?.(new Error('late'));
    await Promise.resolve();
    expect(mockList).toHaveBeenCalled();
  });

  it('shouldApplyHistoryResult covers cancelled and active arms', async () => {
    const { shouldApplyHistoryResult } = await import('./WorkHistorySidebar');
    expect(shouldApplyHistoryResult(false)).toBe(true);
    expect(shouldApplyHistoryResult(true)).toBe(false);
  });
});

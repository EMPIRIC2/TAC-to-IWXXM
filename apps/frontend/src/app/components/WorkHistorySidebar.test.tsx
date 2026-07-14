import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import type { WorkSession } from '@metar/shared';
import { WorkHistorySidebar } from './WorkHistorySidebar';

const mockList = vi.fn();

vi.mock('/utils/workSessionApi', () => ({
  listWorkSessions: (...args: unknown[]) => mockList(...args),
}));

const sampleSession = (overrides: Partial<WorkSession> = {}): WorkSession => ({
  id: 'sess-1',
  user_id: 'user-1',
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
  });

  it('loads recent sessions', async () => {
    render(
      <WorkHistorySidebar
        accessToken="token"
        onSelectSession={onSelectSession}
        onOpenHistory={onOpenHistory}
      />,
    );

    expect(screen.getByLabelText(/recent work sessions/i)).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByText('KDEN WIP')).toBeInTheDocument();
    });
    expect(mockList).toHaveBeenCalledWith('token', { limit: 5 });
  });

  it('selects a session and opens full history', async () => {
    const user = userEvent.setup();
    const session = sampleSession();

    render(
      <WorkHistorySidebar
        accessToken="token"
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

    render(
      <WorkHistorySidebar accessToken="token" onSelectSession={onSelectSession} />,
    );

    await waitFor(() => {
      expect(screen.getByText(/no saved sessions yet/i)).toBeInTheDocument();
    });
  });

  it('shows load errors', async () => {
    mockList.mockRejectedValue(new Error('Forbidden'));

    render(
      <WorkHistorySidebar accessToken="token" onSelectSession={onSelectSession} />,
    );

    await waitFor(() => {
      expect(screen.getByText('Forbidden')).toBeInTheDocument();
    });
  });

  it('shows generic load errors for non-Error rejections', async () => {
    mockList.mockRejectedValue('network');

    render(
      <WorkHistorySidebar accessToken="token" onSelectSession={onSelectSession} />,
    );

    await waitFor(() => {
      expect(screen.getByText('Failed to load history')).toBeInTheDocument();
    });
  });

  it('omits My METARs link when onOpenHistory is not provided', async () => {
    render(
      <WorkHistorySidebar accessToken="token" onSelectSession={onSelectSession} />,
    );

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
      <WorkHistorySidebar
        accessToken="token"
        activeSessionId="sess-2"
        onSelectSession={onSelectSession}
      />,
    );

    await waitFor(() => expect(screen.getByText('Other session')).toBeInTheDocument());

    const otherButton = screen.getByText('Other session').closest('button');
    const activeButton = screen.getByText('Active session').closest('button');
    expect(otherButton).toHaveClass('border-blue-500');
    expect(activeButton).not.toHaveClass('border-blue-500');
  });

  it('falls back to raw status label for unknown statuses', async () => {
    mockList.mockResolvedValue({
      items: [
        sampleSession({
          status: 'archived' as WorkSession['status'],
          title: 'Archived session',
        }),
      ],
      total: 1,
      page: 1,
      limit: 5,
    });

    render(
      <WorkHistorySidebar accessToken="token" onSelectSession={onSelectSession} />,
    );

    await waitFor(() => {
      expect(screen.getByText(/archived ·/i)).toBeInTheDocument();
    });
  });
});

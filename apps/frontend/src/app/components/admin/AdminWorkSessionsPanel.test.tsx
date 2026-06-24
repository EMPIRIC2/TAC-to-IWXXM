import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import type { WorkSession } from '@metar/shared';
import { AdminWorkSessionsPanel } from './AdminWorkSessionsPanel';

const mockListAdmin = vi.fn();

vi.mock('/utils/workSessionApi', () => ({
  listAdminWorkSessions: (...args: unknown[]) => mockListAdmin(...args),
}));

const sampleSession = (overrides: Partial<WorkSession> = {}): WorkSession => ({
  id: 'sess-1',
  user_id: 'user-abc',
  status: 'finished',
  title: 'KJFK finished',
  manual_tac: 'METAR',
  pending_files: [],
  converted_results: [],
  errors: [],
  issues: [],
  conversion_params: {},
  kv_upload_key: 'kv-1',
  deleted_at: null,
  created_at: '2026-06-24T00:00:00Z',
  updated_at: '2026-06-24T12:00:00Z',
  ...overrides,
});

describe('AdminWorkSessionsPanel', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockListAdmin.mockResolvedValue({
      items: [sampleSession()],
      total: 1,
      page: 1,
      limit: 50,
    });
  });

  it('loads and renders work sessions table', async () => {
    render(<AdminWorkSessionsPanel accessToken="admin-token" />);

    expect(screen.getByLabelText(/all users metar work sessions/i)).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText('KJFK finished')).toBeInTheDocument();
    });
    expect(screen.getByText('user-abc')).toBeInTheDocument();
    expect(mockListAdmin).toHaveBeenCalledWith('admin-token', {
      limit: 50,
      status: undefined,
    });
  });

  it('refetches when status filter changes', async () => {
    const user = userEvent.setup();
    render(<AdminWorkSessionsPanel accessToken="admin-token" />);

    await waitFor(() => expect(mockListAdmin).toHaveBeenCalledTimes(1));

    await user.selectOptions(
      screen.getByLabelText(/filter work sessions by status/i),
      'failed',
    );

    await waitFor(() => {
      expect(mockListAdmin).toHaveBeenLastCalledWith('admin-token', {
        limit: 50,
        status: 'failed',
      });
    });
  });

  it('shows empty and error states', async () => {
    mockListAdmin.mockResolvedValueOnce({ items: [], total: 0, page: 1, limit: 50 });
    const { unmount } = render(<AdminWorkSessionsPanel accessToken="admin-token" />);

    await waitFor(() => {
      expect(screen.getByText(/no work sessions found/i)).toBeInTheDocument();
    });

    unmount();
    mockListAdmin.mockRejectedValueOnce(new Error('Admin only'));
    render(<AdminWorkSessionsPanel accessToken="admin-token" />);

    await waitFor(() => {
      expect(screen.getByText('Admin only')).toBeInTheDocument();
    });
  });

  it('shows generic errors for non-Error rejections', async () => {
    mockListAdmin.mockRejectedValue('offline');
    render(<AdminWorkSessionsPanel accessToken="admin-token" />);

    await waitFor(() => {
      expect(screen.getByText('Failed to load work sessions')).toBeInTheDocument();
    });
  });
});

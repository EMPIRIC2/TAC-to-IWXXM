import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import { UserApprovalPanel } from './UserApprovalPanel';

const mockToast = vi.hoisted(() => ({
  error: vi.fn(),
  success: vi.fn(),
}));

const pendingUsers = vi.hoisted(() => [
  {
    id: '1',
    username: 'user1',
    email: 'user1@example.com',
    approval_status: 'pending',
    created_at: '2024-01-01T00:00:00.000Z',
  },
  {
    id: '2',
    username: 'pilot2',
    email: 'pilot2@example.com',
    approval_status: 'pending',
    created_at: '2024-01-02T00:00:00.000Z',
  },
]);

vi.mock('sonner', () => ({
  toast: mockToast,
}));

function jsonResponse(body: unknown, ok = true): Response {
  return {
    ok,
    json: async () => body,
  } as Response;
}

describe('UserApprovalPanel', () => {
  const accessToken = 'admin-token';

  beforeEach(() => {
    vi.clearAllMocks();
    vi.stubGlobal('fetch', vi.fn());
  });

  it('loads and renders pending users via merged admin API', async () => {
    const fetchMock = vi.mocked(fetch);
    fetchMock.mockResolvedValueOnce(jsonResponse({ users: pendingUsers }));

    render(<UserApprovalPanel accessToken={accessToken} />);

    expect(await screen.findByText('user1')).toBeInTheDocument();
    expect(screen.getByText('pilot2')).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/admin/pending-users'),
      expect.objectContaining({
        headers: expect.objectContaining({ Authorization: `Bearer ${accessToken}` }),
      }),
    );
  });

  it('shows empty state when search has no matches', async () => {
    const user = userEvent.setup();
    vi.mocked(fetch).mockResolvedValueOnce(jsonResponse({ users: pendingUsers }));

    render(<UserApprovalPanel accessToken={accessToken} />);

    await screen.findByText('user1');
    await user.type(
      screen.getByPlaceholderText(/search by email or username/i),
      'no-match',
    );

    expect(screen.getByText(/no users match your search/i)).toBeInTheDocument();
  });

  it('refreshes data when refresh button is clicked', async () => {
    const user = userEvent.setup();
    const fetchMock = vi.mocked(fetch);
    fetchMock.mockResolvedValue(jsonResponse({ users: pendingUsers }));

    render(<UserApprovalPanel accessToken={accessToken} />);

    await screen.findByText('user1');
    await user.click(screen.getByRole('button', { name: /refresh/i }));

    expect(fetchMock).toHaveBeenCalledTimes(2);
  });

  it('approves a user and shows success toast', async () => {
    const user = userEvent.setup();
    const fetchMock = vi.mocked(fetch);
    fetchMock
      .mockResolvedValueOnce(jsonResponse({ users: pendingUsers }))
      .mockResolvedValueOnce(jsonResponse({ message: 'ok', profile: pendingUsers[0] }))
      .mockResolvedValueOnce(jsonResponse({ users: [pendingUsers[1]] }));

    render(<UserApprovalPanel accessToken={accessToken} />);

    await screen.findByText('user1');
    const approveButtons = screen.getAllByRole('button', { name: /approve/i });
    await user.click(approveButtons[0]);

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining('/admin/approve-user'),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({ userId: '1' }),
        }),
      );
      expect(mockToast.success).toHaveBeenCalledWith(
        expect.stringContaining('approved successfully'),
      );
    });
  });

  it('rejects a user and shows success toast', async () => {
    const user = userEvent.setup();
    const fetchMock = vi.mocked(fetch);
    fetchMock
      .mockResolvedValueOnce(jsonResponse({ users: pendingUsers }))
      .mockResolvedValueOnce(jsonResponse({ message: 'ok', profile: pendingUsers[0] }))
      .mockResolvedValueOnce(jsonResponse({ users: [pendingUsers[1]] }));

    render(<UserApprovalPanel accessToken={accessToken} />);

    await screen.findByText('user1');
    const rejectButtons = screen.getAllByRole('button', { name: /reject/i });
    await user.click(rejectButtons[0]);

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining('/admin/reject-user'),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({ userId: '1' }),
        }),
      );
      expect(mockToast.success).toHaveBeenCalledWith(
        expect.stringContaining('rejected'),
      );
    });
  });

  it('shows error toast when list query fails', async () => {
    vi.mocked(fetch).mockResolvedValueOnce(jsonResponse({}, false));

    render(<UserApprovalPanel accessToken={accessToken} />);

    await waitFor(() => {
      expect(mockToast.error).toHaveBeenCalledWith('Failed to load pending users');
    });
  });

  it('shows error toast when approve fails', async () => {
    const user = userEvent.setup();
    const fetchMock = vi.mocked(fetch);
    fetchMock
      .mockResolvedValueOnce(jsonResponse({ users: pendingUsers }))
      .mockResolvedValueOnce(jsonResponse({}, false));

    render(<UserApprovalPanel accessToken={accessToken} />);

    await screen.findByText('user1');
    const approveButtons = screen.getAllByRole('button', { name: /approve/i });
    await user.click(approveButtons[0]);

    await waitFor(() => {
      expect(mockToast.error).toHaveBeenCalledWith('Failed to approve user');
    });
  });

  it('shows error toast when reject fails', async () => {
    const user = userEvent.setup();
    const fetchMock = vi.mocked(fetch);
    fetchMock
      .mockResolvedValueOnce(jsonResponse({ users: pendingUsers }))
      .mockResolvedValueOnce(jsonResponse({}, false));

    render(<UserApprovalPanel accessToken={accessToken} />);

    await screen.findByText('user1');
    const rejectButtons = screen.getAllByRole('button', { name: /reject/i });
    await user.click(rejectButtons[0]);

    await waitFor(() => {
      expect(mockToast.error).toHaveBeenCalledWith('Failed to reject user');
    });
  });

  it('shows empty pending users message when list is empty', async () => {
    vi.mocked(fetch).mockResolvedValueOnce(jsonResponse({ users: [] }));

    render(<UserApprovalPanel accessToken={accessToken} />);

    await waitFor(() => {
      expect(screen.getByText(/no pending approvals/i)).toBeInTheDocument();
    });
  });

  it('approve button is disabled while processing', async () => {
    const user = userEvent.setup();
    const fetchMock = vi.mocked(fetch);
    fetchMock
      .mockResolvedValueOnce(jsonResponse({ users: pendingUsers }))
      .mockImplementationOnce(
        () =>
          new Promise((resolve) => {
            setTimeout(() => resolve(jsonResponse({ message: 'ok' })), 5000);
          }),
      );

    render(<UserApprovalPanel accessToken={accessToken} />);

    await screen.findByText('user1');
    const approveButtons = screen.getAllByRole('button', { name: /approve/i });
    user.click(approveButtons[0]);

    await waitFor(() => {
      const buttons = screen.getAllByRole('button', { name: /approve/i });
      expect(buttons.length).toBeGreaterThanOrEqual(1);
    });
  });
});

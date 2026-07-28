import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import type { WorkSession } from '@metar/shared';
import { MyMetarsPage } from './MyMetarsPage';

const mockList = vi.fn();
const mockDelete = vi.fn();
const mockRestore = vi.fn();

vi.mock('/utils/localWorkSessionStore', () => ({
  listMyMetars: (...args: unknown[]) => mockList(...args),
  deleteLocalWorkSession: (...args: unknown[]) => mockDelete(...args),
  restoreLocalWorkSession: (...args: unknown[]) => mockRestore(...args),
}));

const sampleSession = (overrides: Partial<WorkSession> = {}): WorkSession => ({
  id: 'sess-1',
  user_id: 'local',
  product: 'metar',
  status: 'draft',
  title: 'KJFK draft',
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

describe('MyMetarsPage', () => {
  const onBack = vi.fn();
  const onOpenSession = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    mockList.mockResolvedValue({
      items: [sampleSession()],
      total: 1,
      page: 1,
      limit: 50,
    });
    mockDelete.mockResolvedValue(sampleSession({ deleted_at: '2026-06-24T13:00:00Z' }));
    mockRestore.mockResolvedValue(sampleSession());
  });

  it('loads and displays work sessions from IndexedDB', async () => {
    render(
      <MyMetarsPage
        userEmail="Local history"
        onBack={onBack}
        onOpenSession={onOpenSession}
      />,
    );

    expect(screen.getByText('My METARs')).toBeInTheDocument();
    expect(screen.getByText('Local history')).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText('KJFK draft')).toBeInTheDocument();
    });
    expect(mockList).toHaveBeenCalledWith({
      status: undefined,
      include_deleted: false,
      limit: 50,
    });
  });

  it('opens a session when row is clicked', async () => {
    const user = userEvent.setup();
    const session = sampleSession();
    mockList.mockResolvedValue({ items: [session], total: 1, page: 1, limit: 50 });

    render(<MyMetarsPage onBack={onBack} onOpenSession={onOpenSession} />);

    await waitFor(() => {
      expect(screen.getByText('KJFK draft')).toBeInTheDocument();
    });
    await user.click(screen.getByText('KJFK draft'));
    expect(onOpenSession).toHaveBeenCalledWith(session);
  });

  it('refetches when status filter changes', async () => {
    const user = userEvent.setup();
    render(<MyMetarsPage onBack={onBack} onOpenSession={onOpenSession} />);

    await waitFor(() => expect(mockList).toHaveBeenCalledTimes(1));

    await user.selectOptions(screen.getByDisplayValue('All'), 'wip');
    await waitFor(() => {
      expect(mockList).toHaveBeenLastCalledWith({
        status: 'wip',
        include_deleted: false,
        limit: 50,
      });
    });
  });

  it('includes deleted sessions when trash filter is enabled', async () => {
    const user = userEvent.setup();
    render(<MyMetarsPage onBack={onBack} onOpenSession={onOpenSession} />);

    await waitFor(() => expect(mockList).toHaveBeenCalledTimes(1));
    await user.click(screen.getByLabelText(/show trash/i));

    await waitFor(() => {
      expect(mockList).toHaveBeenLastCalledWith({
        status: undefined,
        include_deleted: true,
        limit: 50,
      });
    });
  });

  it('soft-deletes and restores sessions', async () => {
    const user = userEvent.setup();
    mockList
      .mockResolvedValueOnce({
        items: [sampleSession()],
        total: 1,
        page: 1,
        limit: 50,
      })
      .mockResolvedValueOnce({
        items: [sampleSession({ deleted_at: '2026-06-24T13:00:00Z' })],
        total: 1,
        page: 1,
        limit: 50,
      })
      .mockResolvedValueOnce({
        items: [sampleSession()],
        total: 1,
        page: 1,
        limit: 50,
      });

    render(<MyMetarsPage onBack={onBack} onOpenSession={onOpenSession} />);

    await waitFor(() => expect(screen.getByText('KJFK draft')).toBeInTheDocument());
    await user.click(screen.getByRole('button', { name: '' }));
    expect(mockDelete).toHaveBeenCalledWith('sess-1');

    await waitFor(() => expect(mockRestore).toHaveBeenCalled);
    await user.click(screen.getByRole('button', { name: '' }));
    expect(mockRestore).toHaveBeenCalledWith('sess-1');
  });

  it('shows API errors', async () => {
    mockList.mockRejectedValue(new Error('Network down'));

    render(<MyMetarsPage onBack={onBack} onOpenSession={onOpenSession} />);

    await waitFor(() => {
      expect(screen.getByText('Network down')).toBeInTheDocument();
    });
  });

  it('shows generic API errors for non-Error rejections', async () => {
    mockList.mockRejectedValue('offline');

    render(<MyMetarsPage onBack={onBack} onOpenSession={onOpenSession} />);

    await waitFor(() => {
      expect(screen.getByText('Failed to load sessions')).toBeInTheDocument();
    });
  });

  it('navigates back to converter', async () => {
    const user = userEvent.setup();
    render(<MyMetarsPage onBack={onBack} onOpenSession={onOpenSession} />);

    await user.click(screen.getByRole('button', { name: /back to converter/i }));
    expect(onBack).toHaveBeenCalled();
  });
});

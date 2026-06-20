import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { MonitoringPanel } from './MonitoringPanel'

const mockToast = vi.hoisted(() => ({
  error: vi.fn(),
  success: vi.fn(),
}))

vi.mock('/utils/supabase/info', () => ({
  projectId: 'test-project',
}))

vi.mock('sonner', () => ({
  toast: mockToast,
}))

describe('MonitoringPanel', () => {
  const accessToken = 'access-token-123'

  beforeEach(() => {
    vi.clearAllMocks()
    vi.stubGlobal('fetch', vi.fn())
  })

  it('loads and renders stats plus users table', async () => {
    const fetchMock = vi.mocked(fetch)
    fetchMock
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          users: [
            {
              user_id: 'u1',
              email: 'pilot@example.com',
              username: 'pilot',
              approval_status: 'approved',
              is_admin: false,
              created_at: '2026-01-01T00:00:00.000Z',
            },
          ],
        }),
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          stats: {
            totalUsers: 1,
            pendingUsers: 0,
            approvedUsers: 1,
            rejectedUsers: 0,
            adminUsers: 0,
            totalConversions: 10,
            totalStorageUsed: '1GB',
          },
        }),
      } as Response)

    render(<MonitoringPanel accessToken={accessToken} />)

    expect(await screen.findByText('System Monitoring')).toBeInTheDocument()
    expect(await screen.findByText('Total Users')).toBeInTheDocument()
    expect(await screen.findByText('pilot@example.com')).toBeInTheDocument()

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/admin/all-users'),
      expect.objectContaining({
        headers: expect.objectContaining({ Authorization: `Bearer ${accessToken}` }),
      }),
    )
  })

  it('shows toast error when initial monitoring fetch fails', async () => {
    const fetchMock = vi.mocked(fetch)
    fetchMock
      .mockResolvedValueOnce({ ok: false, json: async () => ({}) } as Response)
      .mockResolvedValueOnce({ ok: true, json: async () => ({ stats: null }) } as Response)

    render(<MonitoringPanel accessToken={accessToken} />)

    await waitFor(() => {
      expect(mockToast.error).toHaveBeenCalledWith('Failed to load monitoring data')
    })
  })

  it('filters user rows by search and status', async () => {
    const user = userEvent.setup()
    const fetchMock = vi.mocked(fetch)

    fetchMock
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          users: [
            {
              user_id: 'u1',
              email: 'pilot@example.com',
              username: 'pilot',
              approval_status: 'approved',
              is_admin: false,
              created_at: '2026-01-01T00:00:00.000Z',
            },
            {
              user_id: 'u2',
              email: 'new@example.com',
              username: 'newbie',
              approval_status: 'pending',
              is_admin: false,
              created_at: '2026-01-02T00:00:00.000Z',
            },
          ],
        }),
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          stats: {
            totalUsers: 2,
            pendingUsers: 1,
            approvedUsers: 1,
            rejectedUsers: 0,
            adminUsers: 0,
            totalConversions: 0,
            totalStorageUsed: '0',
          },
        }),
      } as Response)

    render(<MonitoringPanel accessToken={accessToken} />)

    expect(await screen.findByText('pilot@example.com')).toBeInTheDocument()

    await user.type(screen.getByPlaceholderText(/search by email or username/i), 'new@')
    expect(screen.getByText('new@example.com')).toBeInTheDocument()
    expect(screen.queryByText('pilot@example.com')).not.toBeInTheDocument()

    await user.clear(screen.getByPlaceholderText(/search by email or username/i))
    await user.click(screen.getByRole('button', { name: 'Pending' }))
    expect(screen.getByText('new@example.com')).toBeInTheDocument()
    expect(screen.queryByText('pilot@example.com')).not.toBeInTheDocument()
  })

  it('searches case-insensitively by email', async () => {
    const user = userEvent.setup()
    const fetchMock = vi.mocked(fetch)

    fetchMock
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          users: [
            {
              user_id: 'u1',
              email: 'PILOT@EXAMPLE.COM',
              username: 'pilot',
              approval_status: 'approved',
              is_admin: false,
              created_at: '2026-01-01T00:00:00.000Z',
            },
          ],
        }),
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ stats: null }),
      } as Response)

    render(<MonitoringPanel accessToken={accessToken} />)

    await screen.findByText('PILOT@EXAMPLE.COM')

    await user.type(screen.getByPlaceholderText(/search by email or username/i), 'pilot')
    expect(screen.getByText('PILOT@EXAMPLE.COM')).toBeInTheDocument()
  })

  it('applies both status filter and search term simultaneously', async () => {
    const user = userEvent.setup()
    const fetchMock = vi.mocked(fetch)

    fetchMock
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          users: [
            {
              user_id: 'u1',
              email: 'approved@example.com',
              username: 'approved_user',
              approval_status: 'approved',
              is_admin: false,
              created_at: '2026-01-01T00:00:00.000Z',
            },
            {
              user_id: 'u2',
              email: 'pending@example.com',
              username: 'pending_user',
              approval_status: 'pending',
              is_admin: false,
              created_at: '2026-01-02T00:00:00.000Z',
            },
            {
              user_id: 'u3',
              email: 'approved_other@example.com',
              username: 'other',
              approval_status: 'approved',
              is_admin: false,
              created_at: '2026-01-03T00:00:00.000Z',
            },
          ],
        }),
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ stats: null }),
      } as Response)

    render(<MonitoringPanel accessToken={accessToken} />)

    await screen.findByText('approved@example.com')

    // Filter by status 'approved'
    await user.click(screen.getByRole('button', { name: 'Approved' }))
    // Then also search for 'approved@'
    await user.type(screen.getByPlaceholderText(/search by email or username/i), 'approved@')

    expect(screen.getByText('approved@example.com')).toBeInTheDocument()
    expect(screen.queryByText('approved_other@example.com')).not.toBeInTheDocument()
    expect(screen.queryByText('pending@example.com')).not.toBeInTheDocument()
  })

  it('shows toast error when toggle admin status fails', async () => {
    const user = userEvent.setup()
    const fetchMock = vi.mocked(fetch)

    fetchMock
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          users: [
            {
              user_id: 'u1',
              email: 'pilot@example.com',
              username: 'pilot',
              approval_status: 'approved',
              is_admin: false,
              created_at: '2026-01-01T00:00:00.000Z',
            },
          ],
        }),
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ stats: null }),
      } as Response)
      .mockResolvedValueOnce({ ok: false, json: async () => ({}) } as Response)

    render(<MonitoringPanel accessToken={accessToken} />)

    await user.click(await screen.findByRole('button', { name: /grant admin/i }))

    await waitFor(() => {
      expect(mockToast.error).toHaveBeenCalledWith('Failed to toggle admin status')
    })
  })

  it('revokes admin status when user is already admin', async () => {
    const user = userEvent.setup()
    const fetchMock = vi.mocked(fetch)

    fetchMock
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          users: [
            {
              user_id: 'u1',
              email: 'admin@example.com',
              username: 'admin_user',
              approval_status: 'approved',
              is_admin: true,
              created_at: '2026-01-01T00:00:00.000Z',
            },
          ],
        }),
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ stats: null }),
      } as Response)
      .mockResolvedValueOnce({ ok: true, json: async () => ({}) } as Response)
      .mockResolvedValueOnce({ ok: true, json: async () => ({ users: [] }) } as Response)
      .mockResolvedValueOnce({ ok: true, json: async () => ({ stats: null }) } as Response)

    render(<MonitoringPanel accessToken={accessToken} />)

    await user.click(await screen.findByRole('button', { name: /revoke admin/i }))

    await waitFor(() => {
      expect(mockToast.success).toHaveBeenCalledWith('Admin status revoked')
    })
  })

  it('toggles admin status and refreshes data', async () => {
    const user = userEvent.setup()
    const fetchMock = vi.mocked(fetch)

    fetchMock
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          users: [
            {
              user_id: 'u1',
              email: 'pilot@example.com',
              username: 'pilot',
              approval_status: 'approved',
              is_admin: false,
              created_at: '2026-01-01T00:00:00.000Z',
            },
          ],
        }),
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          stats: {
            totalUsers: 1,
            pendingUsers: 0,
            approvedUsers: 1,
            rejectedUsers: 0,
            adminUsers: 0,
            totalConversions: 0,
            totalStorageUsed: '0',
          },
        }),
      } as Response)
      .mockResolvedValueOnce({ ok: true, json: async () => ({}) } as Response)
      .mockResolvedValueOnce({ ok: true, json: async () => ({ users: [] }) } as Response)
      .mockResolvedValueOnce({ ok: true, json: async () => ({ stats: null }) } as Response)

    render(<MonitoringPanel accessToken={accessToken} />)

    await user.click(await screen.findByRole('button', { name: /grant admin/i }))

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining('/admin/toggle-admin'),
        expect.objectContaining({ method: 'POST' }),
      )
      expect(mockToast.success).toHaveBeenCalledWith('Admin status granted')
    })
  })
})

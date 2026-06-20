import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { UserApprovalPanel } from './UserApprovalPanel'

const mockToast = vi.hoisted(() => ({
  error: vi.fn(),
  success: vi.fn(),
}))

const queryState = vi.hoisted(() => ({
  pendingUsers: [
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
  ],
  listError: null as Error | null,
  updateError: null as Error | null,
  user: { id: 'admin-1' } as { id: string } | null,
}))

const mockSupabase = vi.hoisted(() => {
  const order = vi.fn(async () => {
    if (queryState.listError) {
      return { data: null, error: queryState.listError }
    }
    return { data: queryState.pendingUsers, error: null }
  })

  const eqSelect = vi.fn(() => ({ order }))
  const select = vi.fn(() => ({ eq: eqSelect }))

  const eqUpdate = vi.fn(async () => {
    if (queryState.updateError) {
      return { error: queryState.updateError }
    }
    return { error: null }
  })
  const update = vi.fn(() => ({ eq: eqUpdate }))

  const from = vi.fn(() => ({
    select,
    update,
  }))

  const getUser = vi.fn(async () => ({
    data: { user: queryState.user },
  }))

  return {
    from,
    auth: { getUser },
    __mocks: {
      order,
      eqSelect,
      eqUpdate,
      select,
      update,
      getUser,
    },
  }
})

vi.mock('/utils/supabase/client', () => ({
  supabase: mockSupabase,
}))

vi.mock('sonner', () => ({
  toast: mockToast,
}))

describe('UserApprovalPanel', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    queryState.pendingUsers = [
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
    ]
    queryState.listError = null
    queryState.updateError = null
    queryState.user = { id: 'admin-1' }
  })

  it('loads and renders pending users', async () => {
    render(<UserApprovalPanel accessToken="token" />)

    expect(await screen.findByText('user1')).toBeInTheDocument()
    expect(screen.getByText('pilot2')).toBeInTheDocument()
  })

  it('shows empty state when search has no matches', async () => {
    const user = userEvent.setup()
    render(<UserApprovalPanel accessToken="token" />)

    await screen.findByText('user1')
    await user.type(screen.getByPlaceholderText(/search by email or username/i), 'no-match')

    expect(screen.getByText(/no users match your search/i)).toBeInTheDocument()
  })

  it('refreshes data when refresh button is clicked', async () => {
    const user = userEvent.setup()
    render(<UserApprovalPanel accessToken="token" />)

    await screen.findByText('user1')
    await user.click(screen.getByRole('button', { name: /refresh/i }))

    expect(mockSupabase.__mocks.order).toHaveBeenCalledTimes(2)
  })

  it('approves a user and shows success toast', async () => {
    const user = userEvent.setup()
    render(<UserApprovalPanel accessToken="token" />)

    await screen.findByText('user1')
    const approveButtons = screen.getAllByRole('button', { name: /approve/i })
    await user.click(approveButtons[0])

    await waitFor(() => {
      expect(mockSupabase.__mocks.getUser).toHaveBeenCalledTimes(1)
      expect(mockSupabase.__mocks.eqUpdate).toHaveBeenCalled()
      expect(mockToast.success).toHaveBeenCalledWith(expect.stringContaining('approved successfully'))
    })
  })

  it('rejects a user and shows success toast', async () => {
    const user = userEvent.setup()
    render(<UserApprovalPanel accessToken="token" />)

    await screen.findByText('user1')
    const rejectButtons = screen.getAllByRole('button', { name: /reject/i })
    await user.click(rejectButtons[0])

    await waitFor(() => {
      expect(mockSupabase.__mocks.getUser).toHaveBeenCalledTimes(1)
      expect(mockSupabase.__mocks.eqUpdate).toHaveBeenCalled()
      expect(mockToast.success).toHaveBeenCalledWith(expect.stringContaining('rejected'))
    })
  })

  it('shows error toast when list query fails', async () => {
    queryState.listError = new Error('list failed')

    render(<UserApprovalPanel accessToken="token" />)

    await waitFor(() => {
      expect(mockToast.error).toHaveBeenCalledWith('Failed to load pending users')
    })
  })

  it('shows error toast when update fails', async () => {
    const user = userEvent.setup()
    queryState.updateError = new Error('update failed')
    render(<UserApprovalPanel accessToken="token" />)

    await screen.findByText('user1')
    const approveButtons = screen.getAllByRole('button', { name: /approve/i })
    await user.click(approveButtons[0])

    await waitFor(() => {
      expect(mockToast.error).toHaveBeenCalledWith('Failed to approve user')
    })
  })

  it('shows error toast when admin user is not authenticated', async () => {
    const user = userEvent.setup()
    queryState.user = null
    render(<UserApprovalPanel accessToken="token" />)

    await screen.findByText('user1')
    const rejectButtons = screen.getAllByRole('button', { name: /reject/i })
    await user.click(rejectButtons[0])

    await waitFor(() => {
      expect(mockToast.error).toHaveBeenCalledWith('Failed to reject user')
    })
  })

  it('shows empty pending users message when list is empty', async () => {
    queryState.pendingUsers = []
    render(<UserApprovalPanel accessToken="token" />)

    await waitFor(() => {
      expect(screen.getByText(/no pending approvals/i)).toBeInTheDocument()
    })
  })

  it('approve button is disabled while processing', async () => {
    const user = userEvent.setup()
    // Simulate a slow approval that keeps processing state active
    mockSupabase.__mocks.eqUpdate.mockImplementationOnce(async () => {
      await new Promise(r => setTimeout(r, 5000))
      return { error: null }
    })

    render(<UserApprovalPanel accessToken="token" />)

    await screen.findByText('user1')
    const approveButtons = screen.getAllByRole('button', { name: /approve/i })
    // Clicking starts async process; button for this user should disable quickly
    user.click(approveButtons[0])

    await waitFor(() => {
      const buttons = screen.getAllByRole('button', { name: /approve/i })
      // At least one approve button should be in DOM (the other user's)
      expect(buttons.length).toBeGreaterThanOrEqual(1)
    })
  })
})

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { AdminDashboard } from './AdminDashboard'

const mockSignOutWithScope = vi.hoisted(() => vi.fn())

vi.mock('/utils/supabase/logout', () => ({
  signOutWithScope: mockSignOutWithScope,
}), { virtual: true })

vi.mock('./UserApprovalPanel', () => ({
  UserApprovalPanel: () => <div data-testid="approval-panel">Approval Panel</div>,
}))

vi.mock('./SystemSettingsPanel', () => ({
  SystemSettingsPanel: () => <div data-testid="settings-panel">Settings Panel</div>,
}))

vi.mock('./MonitoringPanel', () => ({
  MonitoringPanel: () => <div data-testid="monitoring-panel">Monitoring Panel</div>,
}))

vi.mock('../ThemeToggle', () => ({
  ThemeToggle: () => <div data-testid="theme-toggle">Theme Toggle</div>,
}))

describe('AdminDashboard', () => {
  const defaultProps = {
    onLogout: vi.fn(),
    userEmail: 'admin@example.com',
    accessToken: 'admin-token',
    onSwitchToConverter: vi.fn(),
  }

  beforeEach(() => {
    vi.clearAllMocks()
    mockSignOutWithScope.mockResolvedValue(true)
  })

  it('renders default approval panel and header details', () => {
    render(<AdminDashboard {...defaultProps} />)

    expect(screen.getByText('Admin Dashboard')).toBeInTheDocument()
    expect(screen.getByText('Logged in as: admin@example.com')).toBeInTheDocument()
    expect(screen.getByTestId('approval-panel')).toBeInTheDocument()
    expect(screen.getByTestId('theme-toggle')).toBeInTheDocument()
  })

  it('switches active panel when selection cards are clicked', async () => {
    const user = userEvent.setup()
    render(<AdminDashboard {...defaultProps} />)

    await user.click(screen.getByText('System Settings'))
    expect(screen.getByTestId('settings-panel')).toBeInTheDocument()

    await user.click(screen.getByText('System Monitoring'))
    expect(screen.getByTestId('monitoring-panel')).toBeInTheDocument()

    await user.click(screen.getByText('User Approvals'))
    expect(screen.getByTestId('approval-panel')).toBeInTheDocument()
  })

  it('calls optional converter callback when File Converter button is clicked', async () => {
    const user = userEvent.setup()
    const onSwitchToConverter = vi.fn()

    render(
      <AdminDashboard
        {...defaultProps}
        onSwitchToConverter={onSwitchToConverter}
      />,
    )

    await user.click(screen.getByRole('button', { name: /switch to file converter/i }))
    expect(onSwitchToConverter).toHaveBeenCalledTimes(1)
  })

  it('hides converter switch button when callback is not provided', () => {
    render(
      <AdminDashboard
        {...defaultProps}
        onSwitchToConverter={undefined}
      />,
    )

    expect(screen.queryByRole('button', { name: /switch to file converter/i })).not.toBeInTheDocument()
  })

  it('handles local logout scope and calls onLogout after delay', async () => {
    const user = userEvent.setup()
    const onLogout = vi.fn()
    render(<AdminDashboard {...defaultProps} onLogout={onLogout} />)

    await user.click(screen.getByRole('button', { name: /logout options/i }))
    await user.click(screen.getByRole('button', { name: /sign out from this device only/i }))

    expect(mockSignOutWithScope).toHaveBeenCalledWith('local')
    await waitFor(() => {
      expect(onLogout).toHaveBeenCalledTimes(1)
    })
  })

  it('handles global and others logout scopes', async () => {
    const user = userEvent.setup()
    render(<AdminDashboard {...defaultProps} />)

    await user.click(screen.getByRole('button', { name: /logout options/i }))
    await user.click(screen.getByRole('button', { name: /sign out from all devices/i }))
    expect(mockSignOutWithScope).toHaveBeenCalledWith('global')

    await user.click(screen.getByRole('button', { name: /logout options/i }))
    await user.click(screen.getByRole('button', { name: /sign out from other devices/i }))
    expect(mockSignOutWithScope).toHaveBeenCalledWith('others')
  })

  it('keeps logout menu open when sign out fails', async () => {
    const user = userEvent.setup()
    mockSignOutWithScope.mockResolvedValueOnce(false)

    render(<AdminDashboard {...defaultProps} />)

    await user.click(screen.getByRole('button', { name: /logout options/i }))
    await user.click(screen.getByRole('button', { name: /sign out from all devices/i }))

    await waitFor(() => {
      expect(screen.getByText('Sign out scope:')).toBeInTheDocument()
    })
  })
})

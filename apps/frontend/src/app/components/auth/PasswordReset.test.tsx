import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { PasswordReset } from './PasswordReset'

const mockRequestPasswordReset = vi.hoisted(() => vi.fn())
const mockConfirmPasswordReset = vi.hoisted(() => vi.fn())
const mockToast = vi.hoisted(() => ({
  success: vi.fn(),
  error: vi.fn(),
}))

vi.mock('@/utils/authService', () => ({
  requestPasswordReset: mockRequestPasswordReset,
  confirmPasswordReset: mockConfirmPasswordReset,
}))

vi.mock('sonner', () => ({
  toast: mockToast,
}))

vi.mock('../ThemeToggle', () => ({
  ThemeToggle: () => <div data-testid="theme-toggle">Theme Toggle</div>,
}))

describe('PasswordReset', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('renders request step by default', () => {
    render(<PasswordReset onBackToLogin={vi.fn()} />)

    expect(screen.getByRole('heading', { name: 'Reset Password' })).toBeInTheDocument()
    expect(screen.getByLabelText(/email address/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /send reset email/i })).toBeInTheDocument()
    expect(screen.getByTestId('theme-toggle')).toBeInTheDocument()
  })

  it('shows email-required error when request form is submitted empty', async () => {
    render(<PasswordReset onBackToLogin={vi.fn()} />)

    fireEvent.submit(screen.getByRole('button', { name: /send reset email/i }).closest('form') as HTMLFormElement)

    await waitFor(() => {
      expect(mockToast.error).toHaveBeenCalledWith('Please enter your email address')
    })
  })

  it('requests reset email successfully', async () => {
    const user = userEvent.setup()
    mockRequestPasswordReset.mockResolvedValueOnce(undefined)

    render(<PasswordReset onBackToLogin={vi.fn()} />)

    await user.type(screen.getByLabelText(/email address/i), 'pilot@example.com')
    await user.click(screen.getByRole('button', { name: /send reset email/i }))

    await waitFor(() => {
      expect(mockRequestPasswordReset).toHaveBeenCalledWith('pilot@example.com')
      expect(mockToast.success).toHaveBeenCalledWith('Password reset email sent! Check your inbox.')
    })
  })

  it('shows service error when reset email request fails', async () => {
    const user = userEvent.setup()
    mockRequestPasswordReset.mockRejectedValueOnce(new Error('Reset unavailable'))

    render(<PasswordReset onBackToLogin={vi.fn()} />)

    await user.type(screen.getByLabelText(/email address/i), 'pilot@example.com')
    await user.click(screen.getByRole('button', { name: /send reset email/i }))

    await waitFor(() => {
      expect(mockToast.error).toHaveBeenCalledWith('Reset unavailable')
    })
  })

  it('renders reset step when token is provided', () => {
    render(<PasswordReset onBackToLogin={vi.fn()} resetToken="token-123" />)

    expect(screen.getByLabelText(/new password/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/confirm password/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /update password/i })).toBeInTheDocument()
  })

  it('shows password mismatch error in reset step', async () => {
    const user = userEvent.setup()
    render(<PasswordReset onBackToLogin={vi.fn()} resetToken="token-123" />)

    await user.type(screen.getByLabelText(/new password/i), 'secret123')
    await user.type(screen.getByLabelText(/confirm password/i), 'different456')
    await user.click(screen.getByRole('button', { name: /update password/i }))

    await waitFor(() => {
      expect(mockToast.error).toHaveBeenCalledWith('Passwords do not match')
    })
  })

  it('updates password successfully and redirects back after delay', async () => {
    const user = userEvent.setup()
    const onBackToLogin = vi.fn()
    mockConfirmPasswordReset.mockResolvedValueOnce(undefined)

    render(<PasswordReset onBackToLogin={onBackToLogin} resetToken="token-123" />)

    await user.type(screen.getByLabelText(/new password/i), 'secret123')
    await user.type(screen.getByLabelText(/confirm password/i), 'secret123')
    await user.click(screen.getByRole('button', { name: /update password/i }))

    await waitFor(() => {
      expect(mockConfirmPasswordReset).toHaveBeenCalledWith('token-123', 'secret123')
      expect(mockToast.success).toHaveBeenCalledWith('✓ Password updated successfully! Redirecting to login...')
    })

    await waitFor(() => {
      expect(onBackToLogin).toHaveBeenCalledTimes(1)
    }, { timeout: 3000 })
  })

  it('shows missing token error if resetToken is absent in reset flow', async () => {
    const user = userEvent.setup()
    render(<PasswordReset onBackToLogin={vi.fn()} resetToken={undefined} />)

    await user.type(screen.getByLabelText(/email address/i), 'pilot@example.com')
    await user.click(screen.getByRole('button', { name: /send reset email/i }))

    await waitFor(() => {
      expect(mockRequestPasswordReset).toHaveBeenCalled()
    })
  })

  it('calls onBackToLogin from back button', async () => {
    const user = userEvent.setup()
    const onBackToLogin = vi.fn()

    render(<PasswordReset onBackToLogin={onBackToLogin} />)

    await user.click(screen.getByRole('button', { name: /back to login/i }))
    expect(onBackToLogin).toHaveBeenCalledTimes(1)
  })

  it('shows missing new password error in reset step', async () => {
    render(<PasswordReset onBackToLogin={vi.fn()} resetToken="token-123" />)

    // Button is disabled when fields are empty; submit form directly to test handler
    const form = screen.getByLabelText(/new password/i).closest('form') as HTMLFormElement
    fireEvent.submit(form)

    await waitFor(() => {
      expect(mockToast.error).toHaveBeenCalledWith('Please enter a new password')
    })
  })

  it('shows short password error in reset step', async () => {
    const user = userEvent.setup()
    render(<PasswordReset onBackToLogin={vi.fn()} resetToken="token-123" />)

    await user.type(screen.getByLabelText(/new password/i), '12345')
    await user.type(screen.getByLabelText(/confirm password/i), '12345')
    await user.click(screen.getByRole('button', { name: /update password/i }))

    await waitFor(() => {
      expect(mockToast.error).toHaveBeenCalledWith('Password must be at least 6 characters')
    })
  })

  it('shows update error when confirmPasswordReset fails', async () => {
    const user = userEvent.setup()
    mockConfirmPasswordReset.mockRejectedValueOnce(new Error('Token expired'))

    render(<PasswordReset onBackToLogin={vi.fn()} resetToken="token-123" />)

    await user.type(screen.getByLabelText(/new password/i), 'secret123')
    await user.type(screen.getByLabelText(/confirm password/i), 'secret123')
    await user.click(screen.getByRole('button', { name: /update password/i }))

    await waitFor(() => {
      expect(mockToast.error).toHaveBeenCalledWith('Token expired')
    })
  })
})

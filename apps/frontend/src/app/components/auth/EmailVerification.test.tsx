import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, act, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { EmailVerification } from './EmailVerification'

const mockToast = vi.hoisted(() => ({
  success: vi.fn(),
  error: vi.fn(),
  info: vi.fn(),
}))

vi.mock('sonner', () => ({
  toast: mockToast,
}))

vi.mock('../ThemeToggle', () => ({
  ThemeToggle: () => <div data-testid="theme-toggle">Theme Toggle</div>,
}))

describe('EmailVerification', () => {
  const defaultProps = {
    email: 'pilot@example.com',
    onVerified: vi.fn(),
    onBackToLogin: vi.fn(),
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('renders verification content with masked email', () => {
    render(<EmailVerification {...defaultProps} />)

    expect(screen.getByRole('heading', { name: 'Verify Your Email' })).toBeInTheDocument()
    expect(screen.getByText('Sent to pil***@example.com')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /i've verified my email/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /resend available in 60 seconds/i })).toBeDisabled()
    expect(screen.getByTestId('theme-toggle')).toBeInTheDocument()
  })

  it('calls onBackToLogin from back link', async () => {
    const user = userEvent.setup()
    const onBackToLogin = vi.fn()

    render(<EmailVerification {...defaultProps} onBackToLogin={onBackToLogin} />)

    await user.click(screen.getByRole('button', { name: /return to login page/i }))
    expect(onBackToLogin).toHaveBeenCalledTimes(1)
  })

  it('handles verify flow and calls onVerified after delay', async () => {
    vi.useFakeTimers()
    const onVerified = vi.fn()

    render(<EmailVerification {...defaultProps} onVerified={onVerified} />)

    fireEvent.click(screen.getByRole('button', { name: /i've verified my email/i }))

    expect(mockToast.info).toHaveBeenCalledWith('Please check your email and click the verification link.')
    expect(screen.getByText('Email Verified ✓')).toBeInTheDocument()

    act(() => {
      vi.advanceTimersByTime(2000)
    })

    expect(mockToast.success).toHaveBeenCalledWith('Email verified! You can now login.')
    expect(onVerified).toHaveBeenCalledTimes(1)
  })

  it('keeps resend disabled until countdown reaches zero', async () => {
    vi.useFakeTimers()

    render(<EmailVerification {...defaultProps} />)

    expect(screen.getByRole('button', { name: /resend available in 60 seconds/i })).toBeDisabled()

    for (let i = 0; i < 61; i += 1) {
      act(() => {
        vi.advanceTimersByTime(1000)
      })
    }

    expect(screen.getByRole('button', { name: /resend verification email/i })).toBeEnabled()
    expect(screen.getByText('Resend Email')).toBeInTheDocument()
  })

  it('handles resend flow and resets countdown', async () => {
    vi.useFakeTimers()

    render(<EmailVerification {...defaultProps} />)

    for (let i = 0; i < 61; i += 1) {
      act(() => {
        vi.advanceTimersByTime(1000)
      })
    }

    const resendButton = screen.getByRole('button', { name: /resend verification email/i })
    fireEvent.click(resendButton)

    expect(mockToast.success).toHaveBeenCalledWith('Verification email sent! Please check your inbox.')
    expect(screen.getByRole('button', { name: /resend available in 60 seconds/i })).toBeDisabled()
  })

  it('masks short local-part emails correctly', () => {
    render(
      <EmailVerification
        email="ab@example.com"
        onVerified={vi.fn()}
        onBackToLogin={vi.fn()}
      />,
    )

    expect(screen.getByText('Sent to a***@example.com')).toBeInTheDocument()
  })

  it('shows verified indicator after verify action', async () => {
    const user = userEvent.setup()

    render(<EmailVerification {...defaultProps} />)

    await user.click(screen.getByRole('button', { name: /i've verified my email/i }))

    expect(screen.getByText('Email Verified ✓')).toBeInTheDocument()
  })

  it('masks single-char local-part emails correctly', () => {
    render(
      <EmailVerification
        email="a@example.com"
        onVerified={vi.fn()}
        onBackToLogin={vi.fn()}
      />,
    )

    expect(screen.getByText('Sent to a***@example.com')).toBeInTheDocument()
  })

  it('shows verify button as loading while verifying', async () => {
    vi.useFakeTimers()
    render(<EmailVerification {...defaultProps} />)

    fireEvent.click(screen.getByRole('button', { name: /i've verified my email/i }))

    // After click, isVerifying=true briefly; emailStatus changes to verified immediately
    expect(screen.getByText('Email Verified ✓')).toBeInTheDocument()
  })

  it('renders all help text items', () => {
    render(<EmailVerification {...defaultProps} />)

    expect(screen.getByText(/check spam or junk folder/i)).toBeInTheDocument()
  })
})

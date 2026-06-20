import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { Login } from './Login'

const mockLogin = vi.hoisted(() => vi.fn())
const mockToast = vi.hoisted(() => ({
  success: vi.fn(),
  error: vi.fn(),
}))

vi.mock('@/utils/authService', () => ({
  login: mockLogin,
}))

vi.mock('sonner', () => ({
  toast: mockToast,
}))

vi.mock('../ThemeToggle', () => ({
  ThemeToggle: () => <div data-testid="theme-toggle">Theme Toggle</div>,
}))

describe('Login', () => {
  const defaultProps = {
    onLogin: vi.fn(),
    onSwitchToRegister: vi.fn(),
    onForgotPassword: vi.fn(),
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders login form controls', () => {
    render(<Login {...defaultProps} />)

    expect(screen.getByText('METAR Converter')).toBeInTheDocument()
    expect(screen.getByLabelText(/email address/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/^password$/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /sign in to account/i })).toBeInTheDocument()
    expect(screen.getByTestId('theme-toggle')).toBeInTheDocument()
  })

  it('shows required validation errors for empty form submit', async () => {
    const user = userEvent.setup()
    render(<Login {...defaultProps} />)

    await user.click(screen.getByRole('button', { name: /sign in to account/i }))

    expect(await screen.findByText('Email is required')).toBeInTheDocument()
    expect(await screen.findByText('Password is required')).toBeInTheDocument()
  })

  it('shows invalid email format error', async () => {
    const user = userEvent.setup()
    render(<Login {...defaultProps} />)

    await user.type(screen.getByLabelText(/email address/i), 'invalid-email')
    await user.type(screen.getByLabelText(/^password$/i), 'secret123')
    fireEvent.submit(screen.getByRole('button', { name: /sign in to account/i }).closest('form') as HTMLFormElement)

    expect(await screen.findByText('Please enter a valid email address')).toBeInTheDocument()
  })

  it('shows short password validation error', async () => {
    const user = userEvent.setup()
    render(<Login {...defaultProps} />)

    await user.type(screen.getByLabelText(/email address/i), 'user@example.com')
    await user.type(screen.getByLabelText(/^password$/i), '123')
    await user.click(screen.getByRole('button', { name: /sign in to account/i }))

    expect(await screen.findByText('Password must be at least 6 characters')).toBeInTheDocument()
  })

  it('calls onSwitchToRegister when register link is clicked', async () => {
    const user = userEvent.setup()
    const onSwitchToRegister = vi.fn()

    render(
      <Login
        {...defaultProps}
        onSwitchToRegister={onSwitchToRegister}
      />,
    )

    await user.click(screen.getByRole('button', { name: /go to registration page/i }))
    expect(onSwitchToRegister).toHaveBeenCalledTimes(1)
  })

  it('calls auth login and onLogin on successful submit', async () => {
    const user = userEvent.setup()
    const onLogin = vi.fn()
    mockLogin.mockResolvedValueOnce({
      user: {
        email: 'pilot@example.com',
        metadata: { name: 'Pilot User' },
      },
      session: {
        access_token: 'token-123',
      },
    })

    render(<Login {...defaultProps} onLogin={onLogin} />)

    await user.type(screen.getByLabelText(/email address/i), 'pilot@example.com')
    await user.type(screen.getByLabelText(/^password$/i), 'secret123')
    await user.click(screen.getByRole('button', { name: /sign in to account/i }))

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith({
        email: 'pilot@example.com',
        password: 'secret123',
      })
      expect(onLogin).toHaveBeenCalledWith('pilot@example.com', false, 'token-123', false)
    })
    expect(mockToast.success).toHaveBeenCalledWith('Welcome back, Pilot User!')
  })

  it('shows toast error when login response has no session', async () => {
    const user = userEvent.setup()
    mockLogin.mockResolvedValueOnce({ user: null, session: null })

    render(<Login {...defaultProps} />)

    await user.type(screen.getByLabelText(/email address/i), 'pilot@example.com')
    await user.type(screen.getByLabelText(/^password$/i), 'secret123')
    await user.click(screen.getByRole('button', { name: /sign in to account/i }))

    await waitFor(() => {
      expect(mockToast.error).toHaveBeenCalledWith('Login failed. Please try again.')
    })
  })

  it('shows service error message when login throws', async () => {
    const user = userEvent.setup()
    mockLogin.mockRejectedValueOnce(new Error('Invalid credentials'))

    render(<Login {...defaultProps} />)

    await user.type(screen.getByLabelText(/email address/i), 'pilot@example.com')
    await user.type(screen.getByLabelText(/^password$/i), 'secret123')
    await user.click(screen.getByRole('button', { name: /sign in to account/i }))

    await waitFor(() => {
      expect(mockToast.error).toHaveBeenCalledWith('Invalid credentials')
    })
  })

  it('falls back to user email in welcome toast when metadata.name is missing', async () => {
    const user = userEvent.setup()
    const onLogin = vi.fn()
    mockLogin.mockResolvedValueOnce({
      user: {
        email: 'nometadata@example.com',
        metadata: undefined,
      },
      session: { access_token: 'tok-abc' },
    })

    render(<Login {...defaultProps} onLogin={onLogin} />)

    await user.type(screen.getByLabelText(/email address/i), 'nometadata@example.com')
    await user.type(screen.getByLabelText(/^password$/i), 'secret123')
    await user.click(screen.getByRole('button', { name: /sign in to account/i }))

    await waitFor(() => {
      expect(mockToast.success).toHaveBeenCalledWith('Welcome back, nometadata@example.com!')
    })
  })

  it('renders the remember-me checkbox and forgot-password reset button', () => {
    render(<Login {...defaultProps} />)

    expect(screen.getByLabelText(/remember me/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/forgot password/i)).toBeInTheDocument()
  })
})

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { Register } from './Register'

const mockRegisterUser = vi.hoisted(() => vi.fn())
const mockToast = vi.hoisted(() => ({
  success: vi.fn(),
  error: vi.fn(),
}))

vi.mock('@/utils/authService', () => ({
  register: mockRegisterUser,
}))

vi.mock('sonner', () => ({
  toast: mockToast,
}))

vi.mock('../ThemeToggle', () => ({
  ThemeToggle: () => <div data-testid="theme-toggle">Theme Toggle</div>,
}))

describe('Register', () => {
  const defaultProps = {
    onRegister: vi.fn(),
    onSwitchToLogin: vi.fn(),
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders register controls and theme toggle', () => {
    render(<Register {...defaultProps} />)

    expect(screen.getByRole('heading', { name: 'Create Account' })).toBeInTheDocument()
    expect(screen.getByLabelText(/email address/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/^password$/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/confirm password/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /create account/i })).toBeInTheDocument()
    expect(screen.getByTestId('theme-toggle')).toBeInTheDocument()
  })

  it('shows required validation errors for empty submit', async () => {
    render(<Register {...defaultProps} />)

    fireEvent.submit(screen.getByRole('button', { name: /create account/i }).closest('form') as HTMLFormElement)

    expect(await screen.findByText('Email is required')).toBeInTheDocument()
    expect(await screen.findByText('Password is required')).toBeInTheDocument()
    expect(await screen.findByText('Please confirm your password')).toBeInTheDocument()
  })

  it('shows invalid email and mismatched password errors', async () => {
    const user = userEvent.setup()
    render(<Register {...defaultProps} />)

    await user.type(screen.getByLabelText(/email address/i), 'invalid-email')
    await user.type(screen.getByLabelText(/^password$/i), 'secret123')
    await user.type(screen.getByLabelText(/confirm password/i), 'different456')
    fireEvent.submit(screen.getByRole('button', { name: /create account/i }).closest('form') as HTMLFormElement)

    expect(await screen.findByText('Please enter a valid email address')).toBeInTheDocument()
    expect(await screen.findByText('Passwords do not match')).toBeInTheDocument()
  })

  it('calls onSwitchToLogin when sign-in link is clicked', async () => {
    const user = userEvent.setup()
    const onSwitchToLogin = vi.fn()
    render(<Register {...defaultProps} onSwitchToLogin={onSwitchToLogin} />)

    await user.click(screen.getByRole('button', { name: /go to login page/i }))
    expect(onSwitchToLogin).toHaveBeenCalledTimes(1)
  })

  it('submits successfully and calls onRegister', async () => {
    const user = userEvent.setup()
    const onRegister = vi.fn()
    mockRegisterUser.mockResolvedValueOnce({
      user: { email: 'pilot@example.com' },
      session: null,
    })

    render(<Register {...defaultProps} onRegister={onRegister} />)

    await user.type(screen.getByLabelText(/email address/i), 'pilot@example.com')
    await user.type(screen.getByLabelText(/^password$/i), 'secret123')
    await user.type(screen.getByLabelText(/confirm password/i), 'secret123')
    await user.click(screen.getByLabelText(/accept terms and conditions/i))
    await user.click(screen.getByRole('button', { name: /create account/i }))

    await waitFor(() => {
      expect(mockRegisterUser).toHaveBeenCalledWith({
        email: 'pilot@example.com',
        password: 'secret123',
      })
      expect(onRegister).toHaveBeenCalledWith('pilot@example.com')
    })
    expect(mockToast.success).toHaveBeenCalledWith('Account created! Please check your email to verify your account.')
  })

  it('shows toast error when register response has no user', async () => {
    const user = userEvent.setup()
    mockRegisterUser.mockResolvedValueOnce({ user: null, session: null })

    render(<Register {...defaultProps} />)

    await user.type(screen.getByLabelText(/email address/i), 'pilot@example.com')
    await user.type(screen.getByLabelText(/^password$/i), 'secret123')
    await user.type(screen.getByLabelText(/confirm password/i), 'secret123')
    await user.click(screen.getByLabelText(/accept terms and conditions/i))
    await user.click(screen.getByRole('button', { name: /create account/i }))

    await waitFor(() => {
      expect(mockToast.error).toHaveBeenCalledWith('Registration failed. Please try again.')
    })
  })

  it('shows service error message when register throws', async () => {
    const user = userEvent.setup()
    mockRegisterUser.mockRejectedValueOnce(new Error('Email already in use'))

    render(<Register {...defaultProps} />)

    await user.type(screen.getByLabelText(/email address/i), 'pilot@example.com')
    await user.type(screen.getByLabelText(/^password$/i), 'secret123')
    await user.type(screen.getByLabelText(/confirm password/i), 'secret123')
    await user.click(screen.getByLabelText(/accept terms and conditions/i))
    await user.click(screen.getByRole('button', { name: /create account/i }))

    await waitFor(() => {
      expect(mockToast.error).toHaveBeenCalledWith('Email already in use')
    })
  })

  it('shows short password validation error', async () => {
    const user = userEvent.setup()
    render(<Register {...defaultProps} />)

    await user.type(screen.getByLabelText(/email address/i), 'pilot@example.com')
    await user.type(screen.getByLabelText(/^password$/i), '12345')
    await user.type(screen.getByLabelText(/confirm password/i), '12345')
    fireEvent.submit(screen.getByRole('button', { name: /create account/i }).closest('form') as HTMLFormElement)

    expect(await screen.findByText('Password must be at least 6 characters')).toBeInTheDocument()
  })

  it('renders terms and conditions checkbox', () => {
    render(<Register {...defaultProps} />)

    const terms = screen.getByLabelText(/accept terms and conditions/i)
    expect(terms).toBeInTheDocument()
    expect(terms).not.toBeChecked()
  })
})

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'

import { AuthCallback } from './AuthCallback'

const mockToast = vi.hoisted(() => ({
  success: vi.fn(),
  error: vi.fn(),
}))

vi.mock('sonner', () => ({
  toast: mockToast,
}))

describe('AuthCallback', () => {
  let originalLocation: Location

  beforeEach(() => {
    vi.clearAllMocks()
    originalLocation = window.location

    Object.defineProperty(window, 'location', {
      writable: true,
      value: {
        hash: '',
        href: 'http://localhost/',
      },
    })

    vi.spyOn(console, 'warn').mockImplementation(() => {})
    vi.spyOn(console, 'error').mockImplementation(() => {})
    vi.spyOn(console, 'log').mockImplementation(() => {})
  })

  afterEach(() => {
    vi.useRealTimers()
    vi.restoreAllMocks()
    Object.defineProperty(window, 'location', {
      writable: true,
      value: originalLocation,
    })
  })

  it('shows error state by default when no token is present', async () => {
    render(<AuthCallback />)

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Error' })).toBeInTheDocument()
      expect(screen.getByText('Invalid callback URL. Please try again.')).toBeInTheDocument()
    })
  })

  it('shows error state when callback has no access token', async () => {
    window.location.hash = '#type=signup'

    render(<AuthCallback />)

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Error' })).toBeInTheDocument()
      expect(screen.getByText('Invalid callback URL. Please try again.')).toBeInTheDocument()
      expect(mockToast.error).toHaveBeenCalledWith('Authentication failed')
    })

    await waitFor(() => {
      expect(window.location.href).toBe('/')
      expect(window.location.hash).toBe('')
    }, { timeout: 3000 })
  })

  it('handles signup token with onVerified callback', async () => {
    const onVerified = vi.fn()
    window.location.hash = '#access_token=abc123&type=signup'

    render(<AuthCallback onVerified={onVerified} />)

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Success' })).toBeInTheDocument()
      expect(screen.getByText('Email verified! Redirecting...')).toBeInTheDocument()
      expect(mockToast.success).toHaveBeenCalledWith('Email verified successfully!')
      expect(onVerified).toHaveBeenCalledTimes(1)
    })

    expect(window.location.hash).toBe('')
  })

  it('falls back to onRegister for signup when onVerified is missing', async () => {
    const onRegister = vi.fn()
    window.location.hash = '#access_token=abc123&type=signup'

    render(<AuthCallback onRegister={onRegister} />)

    await waitFor(() => {
      expect(onRegister).toHaveBeenCalledWith('')
    })
  })

  it('redirects to reset route for recovery type', async () => {
    window.location.hash = '#access_token=reset-token&type=recovery'

    render(<AuthCallback />)

    await waitFor(() => {
      expect(window.location.href).toBe('/auth/reset?token=reset-token')
    })
  })

  it('redirects to home route for default callback type', async () => {
    window.location.hash = '#access_token=plain-token&type=magiclink'

    render(<AuthCallback />)

    await waitFor(() => {
      expect(window.location.href).toBe('/')
    })
  })

  it('enters catch path when callback handler throws', async () => {
    const onVerified = vi.fn(() => {
      throw new Error('handler failure')
    })
    window.location.hash = '#access_token=abc123&type=signup'

    render(<AuthCallback onVerified={onVerified} />)

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Error' })).toBeInTheDocument()
      expect(screen.getByText('An error occurred. Please try again.')).toBeInTheDocument()
      expect(mockToast.error).toHaveBeenCalledWith('Authentication failed')
    })

    await waitFor(() => {
      expect(window.location.href).toBe('/')
    }, { timeout: 3000 })
  })
})

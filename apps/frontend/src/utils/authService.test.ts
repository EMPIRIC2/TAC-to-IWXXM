import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import {
  confirmPasswordReset,
  getCurrentUser,
  isLoggedIn,
  login,
  logout,
  register,
  requestPasswordReset,
} from './authService'

const mockSession = {
  access_token: 'access-token',
  refresh_token: 'refresh-token',
  expires_at: Math.floor(Date.now() / 1000) + 3600,
}

const mockUser = {
  id: 'user-1',
  email: 'pilot@example.com',
  metadata: { name: 'Pilot' },
}

describe('authService', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.restoreAllMocks()
    vi.useRealTimers()
  })

  afterEach(() => {
    vi.restoreAllMocks()
    vi.useRealTimers()
  })

  it('stores session tokens on login success', async () => {
    vi.spyOn(global, 'fetch').mockResolvedValue({
      ok: true,
      json: async () => ({ user: mockUser, session: mockSession }),
      status: 200,
      statusText: 'OK',
    } as Response)

    const result = await login({ email: mockUser.email, password: 'Password123!' })

    expect(result.user.email).toBe(mockUser.email)
    expect(localStorage.getItem('access_token')).toBe(mockSession.access_token)
    expect(localStorage.getItem('refresh_token')).toBe(mockSession.refresh_token)
    expect(localStorage.getItem('expires_at')).toBe(String(mockSession.expires_at))
  })

  it('returns service detail on register failure', async () => {
    vi.spyOn(global, 'fetch').mockResolvedValue({
      ok: false,
      json: async () => ({ detail: 'Email already exists' }),
      status: 409,
      statusText: 'Conflict',
    } as Response)

    await expect(
      register({ email: mockUser.email, password: 'Password123!', name: 'Pilot' }),
    ).rejects.toThrow('Email already exists')
  })

  it('registers successfully without storing tokens when session is null', async () => {
    vi.spyOn(global, 'fetch').mockResolvedValue({
      ok: true,
      json: async () => ({ user: mockUser, session: null }),
      status: 200,
      statusText: 'OK',
    } as Response)

    const result = await register({ email: mockUser.email, password: 'Password123!' })

    expect(result.user.email).toBe(mockUser.email)
    expect(localStorage.getItem('access_token')).toBeNull()
    expect(localStorage.getItem('refresh_token')).toBeNull()
  })

  it('falls back to unknown error message when register error body is invalid', async () => {
    vi.spyOn(global, 'fetch').mockResolvedValue({
      ok: false,
      json: async () => {
        throw new Error('invalid json')
      },
      status: 500,
      statusText: 'Internal Server Error',
    } as unknown as Response)

    await expect(register({ email: mockUser.email, password: 'Password123!' })).rejects.toThrow('Unknown error')
  })

  it('falls back to unknown error message when login error body is invalid', async () => {
    vi.spyOn(global, 'fetch').mockResolvedValue({
      ok: false,
      json: async () => {
        throw new Error('invalid json')
      },
      status: 500,
      statusText: 'Internal Server Error',
    } as unknown as Response)

    await expect(login({ email: mockUser.email, password: 'Password123!' })).rejects.toThrow('Unknown error')
  })

  it('skips refresh when token is still valid', async () => {
    localStorage.setItem('access_token', 'valid-token')
    localStorage.setItem('expires_at', String(Math.floor(Date.now() / 1000) + 600))

    const fetchSpy = vi.spyOn(global, 'fetch').mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => mockUser,
    } as Response)

    const user = await getCurrentUser()

    expect(user.email).toBe(mockUser.email)
    expect(fetchSpy).toHaveBeenCalledTimes(1)
    expect(fetchSpy).toHaveBeenCalledWith(
      expect.stringContaining('/auth/me'),
      expect.objectContaining({ method: 'GET' }),
    )
  })

  it('clears tokens and throws when refresh endpoint returns non-ok', async () => {
    localStorage.setItem('access_token', 'expired-token')
    localStorage.setItem('refresh_token', 'refresh-token')
    localStorage.setItem('expires_at', String(Math.floor(Date.now() / 1000) - 1))

    vi.spyOn(global, 'fetch').mockResolvedValue({
      ok: false,
      status: 401,
      json: async () => ({ detail: 'expired refresh token' }),
    } as Response)

    await expect(getCurrentUser()).rejects.toThrow('Failed to refresh token')
    expect(localStorage.getItem('access_token')).toBeNull()
    expect(localStorage.getItem('refresh_token')).toBeNull()
    expect(localStorage.getItem('expires_at')).toBeNull()
  })

  it('throws no-access-token when expiry is valid but access token is missing', async () => {
    localStorage.setItem('expires_at', String(Math.floor(Date.now() / 1000) + 1200))

    await expect(getCurrentUser()).rejects.toThrow('No access token')
  })

  it('clears tokens when get current user endpoint fails', async () => {
    localStorage.setItem('access_token', 'valid-token')
    localStorage.setItem('refresh_token', 'refresh-token')
    localStorage.setItem('expires_at', String(Math.floor(Date.now() / 1000) + 1200))

    vi.spyOn(global, 'fetch').mockResolvedValue({
      ok: false,
      status: 403,
      json: async () => ({ detail: 'forbidden' }),
    } as Response)

    await expect(getCurrentUser()).rejects.toThrow('Failed to get user info')
    expect(localStorage.getItem('access_token')).toBeNull()
    expect(localStorage.getItem('refresh_token')).toBeNull()
    expect(localStorage.getItem('expires_at')).toBeNull()
  })

  it('refreshes expired token before requesting current user', async () => {
    localStorage.setItem('access_token', 'expired-token')
    localStorage.setItem('refresh_token', 'refresh-token')
    localStorage.setItem('expires_at', String(Math.floor(Date.now() / 1000) - 10))

    const fetchSpy = vi.spyOn(global, 'fetch')
    fetchSpy
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({
          access_token: 'new-access',
          refresh_token: 'new-refresh',
          expires_at: Math.floor(Date.now() / 1000) + 1800,
        }),
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockUser,
      } as Response)

    const user = await getCurrentUser()

    expect(user.email).toBe(mockUser.email)
    expect(fetchSpy).toHaveBeenNthCalledWith(
      1,
      expect.stringContaining('/auth/refresh'),
      expect.objectContaining({ method: 'POST' }),
    )
    expect(fetchSpy).toHaveBeenNthCalledWith(
      2,
      expect.stringContaining('/auth/me'),
      expect.objectContaining({ method: 'GET' }),
    )
    expect(localStorage.getItem('access_token')).toBe('new-access')
  })

  it('throws when token is expired and no refresh token exists', async () => {
    localStorage.setItem('access_token', 'expired-token')
    localStorage.setItem('expires_at', String(Math.floor(Date.now() / 1000) - 1))

    await expect(getCurrentUser()).rejects.toThrow('No refresh token available')
  })

  it('clears tokens on logout even if request fails', async () => {
    localStorage.setItem('access_token', 'token')
    localStorage.setItem('refresh_token', 'refresh')
    localStorage.setItem('expires_at', String(Math.floor(Date.now() / 1000) + 3600))

    vi.spyOn(global, 'fetch').mockRejectedValue(new Error('Network error'))

    await logout()

    expect(localStorage.getItem('access_token')).toBeNull()
    expect(localStorage.getItem('refresh_token')).toBeNull()
    expect(localStorage.getItem('expires_at')).toBeNull()
  })

  it('returns immediately from logout when there is no access token', async () => {
    const fetchSpy = vi.spyOn(global, 'fetch')

    await logout()

    expect(fetchSpy).not.toHaveBeenCalled()
  })

  it('reports login state from token and expiry', () => {
    localStorage.setItem('access_token', 'token')
    localStorage.setItem('expires_at', String(Math.floor(Date.now() / 1000) + 1000))
    expect(isLoggedIn()).toBe(true)

    localStorage.setItem('expires_at', String(Math.floor(Date.now() / 1000) - 1))
    expect(isLoggedIn()).toBe(false)
  })

  it('requests password reset and returns backend message', async () => {
    vi.spyOn(global, 'fetch').mockResolvedValue({
      ok: true,
      json: async () => ({ message: 'Reset email sent' }),
    } as Response)

    const result = await requestPasswordReset(mockUser.email)

    expect(result.message).toBe('Reset email sent')
  })

  it('throws backend detail when reset request fails', async () => {
    vi.spyOn(global, 'fetch').mockResolvedValue({
      ok: false,
      json: async () => ({ detail: 'Rate limited' }),
    } as Response)

    await expect(requestPasswordReset(mockUser.email)).rejects.toThrow('Rate limited')
  })

  it('confirms password reset with bearer token', async () => {
    const fetchSpy = vi.spyOn(global, 'fetch').mockResolvedValue({
      ok: true,
      json: async () => ({ message: 'Password updated' }),
    } as Response)

    const result = await confirmPasswordReset('reset-token', 'NewPassword123!')

    expect(result.message).toBe('Password updated')
    expect(fetchSpy).toHaveBeenCalledWith(
      expect.stringContaining('/auth/password-reset/confirm'),
      expect.objectContaining({
        method: 'POST',
        headers: expect.objectContaining({ Authorization: 'Bearer reset-token' }),
      }),
    )
  })

  it('throws default error when confirm password reset fails without detail', async () => {
    vi.spyOn(global, 'fetch').mockResolvedValue({
      ok: false,
      json: async () => ({}),
    } as Response)

    await expect(confirmPasswordReset('reset-token', 'NewPassword123!')).rejects.toThrow('Failed to reset password')
  })
})

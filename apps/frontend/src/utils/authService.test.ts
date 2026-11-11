import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import {
  confirmEmail,
  confirmPasswordReset,
  getCurrentUser,
  isLoggedIn,
  login,
  logout,
  register,
  requestPasswordReset,
} from './authService';

const mockSession = {
  access_token: 'access-token',
  refresh_token: 'refresh-token',
  expires_at: Math.floor(Date.now() / 1000) + 3600,
};

const mockUser = {
  id: 'user-1',
  email: 'pilot@example.com',
  user_metadata: { name: 'Pilot' },
};

const authMock = {
  signInWithPassword: vi.fn(),
  signUp: vi.fn(),
  signOut: vi.fn(),
  verifyOtp: vi.fn(),
  getUser: vi.fn(),
  refreshSession: vi.fn(),
  resetPasswordForEmail: vi.fn(),
  updateUser: vi.fn(),
};

vi.mock('./supabase/client', () => ({
  getSupabaseClient: () => ({ auth: authMock }),
}));

describe('authService', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('stores session tokens on login success', async () => {
    authMock.signInWithPassword.mockResolvedValue({
      data: { user: mockUser, session: mockSession },
      error: null,
    });

    const result = await login({ email: mockUser.email, password: 'Password123!' });

    expect(result.user.email).toBe(mockUser.email);
    expect(localStorage.getItem('access_token')).toBe(mockSession.access_token);
    expect(localStorage.getItem('refresh_token')).toBe(mockSession.refresh_token);
    expect(localStorage.getItem('expires_at')).toBe(String(mockSession.expires_at));
  });

  it('confirmEmail stores session tokens on success', async () => {
    authMock.verifyOtp.mockResolvedValue({
      data: { user: mockUser, session: mockSession },
      error: null,
    });

    const result = await confirmEmail({ token_hash: 'hash123', type: 'email' });
    expect(result.user.email).toBe(mockUser.email);
    expect(localStorage.getItem('access_token')).toBe(mockSession.access_token);
  });

  it('confirmEmail defaults type to email and skips store when session null', async () => {
    authMock.verifyOtp.mockResolvedValue({
      data: { user: mockUser, session: null },
      error: null,
    });

    await confirmEmail({ token_hash: 'hash123' });
    expect(authMock.verifyOtp).toHaveBeenCalledWith({
      token_hash: 'hash123',
      type: 'email',
    });
    expect(localStorage.getItem('access_token')).toBeNull();
  });

  it('confirmEmail surfaces message on failure', async () => {
    authMock.verifyOtp.mockResolvedValue({
      data: { user: null, session: null },
      error: { message: 'bad hash' },
    });

    await expect(confirmEmail({ token_hash: 'bad' })).rejects.toThrow('bad hash');
  });

  it('confirmEmail falls back when error has empty message', async () => {
    authMock.verifyOtp.mockResolvedValue({
      data: { user: null, session: null },
      error: { message: '' },
    });

    await expect(confirmEmail({ token_hash: 'bad' })).rejects.toThrow(
      'Email confirmation failed',
    );
  });

  it('falls back to default register message when error has no message', async () => {
    authMock.signUp.mockResolvedValue({
      data: { user: null, session: null },
      error: { message: '' },
    });

    await expect(
      register({ email: mockUser.email, password: 'Password123!' }),
    ).rejects.toThrow('Registration failed');
  });

  it('falls back to default login message when error has no message', async () => {
    authMock.signInWithPassword.mockResolvedValue({
      data: { user: null, session: null },
      error: { message: '' },
    });

    await expect(
      login({ email: mockUser.email, password: 'Password123!' }),
    ).rejects.toThrow('Login failed');
  });

  it('returns service detail on register failure', async () => {
    authMock.signUp.mockResolvedValue({
      data: { user: null, session: null },
      error: { message: 'Email already exists' },
    });

    await expect(
      register({ email: mockUser.email, password: 'Password123!', name: 'Pilot' }),
    ).rejects.toThrow('Email already exists');
  });

  it('registers successfully without storing tokens when session is null', async () => {
    authMock.signUp.mockResolvedValue({
      data: { user: mockUser, session: null },
      error: null,
    });

    const result = await register({ email: mockUser.email, password: 'Password123!' });

    expect(result.user.email).toBe(mockUser.email);
    expect(localStorage.getItem('access_token')).toBeNull();
  });

  it('stores session tokens on register success', async () => {
    authMock.signUp.mockResolvedValue({
      data: { user: mockUser, session: mockSession },
      error: null,
    });

    await register({ email: mockUser.email, password: 'Password123!', name: 'Pilot' });

    expect(localStorage.getItem('access_token')).toBe(mockSession.access_token);
    expect(authMock.signUp).toHaveBeenCalledWith(
      expect.objectContaining({
        email: mockUser.email,
        options: { data: { name: 'Pilot' } },
      }),
    );
  });

  it('skips refresh when token is still valid', async () => {
    localStorage.setItem('access_token', 'valid-token');
    localStorage.setItem('expires_at', String(Math.floor(Date.now() / 1000) + 600));
    authMock.getUser.mockResolvedValue({
      data: { user: mockUser },
      error: null,
    });

    const user = await getCurrentUser();

    expect(user.email).toBe(mockUser.email);
    expect(authMock.refreshSession).not.toHaveBeenCalled();
    expect(authMock.getUser).toHaveBeenCalledWith('valid-token');
  });

  it('clears tokens and throws when refresh fails', async () => {
    localStorage.setItem('access_token', 'expired-token');
    localStorage.setItem('refresh_token', 'refresh-token');
    localStorage.setItem('expires_at', String(Math.floor(Date.now() / 1000) - 1));

    authMock.refreshSession.mockResolvedValue({
      data: { session: null },
      error: { message: 'expired' },
    });

    await expect(getCurrentUser()).rejects.toThrow('Failed to refresh token');
    expect(localStorage.getItem('access_token')).toBeNull();
  });

  it('throws no-access-token when expiry is valid but access token is missing', async () => {
    localStorage.setItem('expires_at', String(Math.floor(Date.now() / 1000) + 1200));

    await expect(getCurrentUser()).rejects.toThrow('No access token');
  });

  it('clears tokens when get current user fails', async () => {
    localStorage.setItem('access_token', 'valid-token');
    localStorage.setItem('expires_at', String(Math.floor(Date.now() / 1000) + 1200));

    authMock.getUser.mockResolvedValue({
      data: { user: null },
      error: { message: 'forbidden' },
    });

    await expect(getCurrentUser()).rejects.toThrow('Failed to get user info');
    expect(localStorage.getItem('access_token')).toBeNull();
  });

  it('refreshes expired token before requesting current user', async () => {
    localStorage.setItem('access_token', 'expired-token');
    localStorage.setItem('refresh_token', 'refresh-token');
    localStorage.setItem('expires_at', String(Math.floor(Date.now() / 1000) - 10));

    authMock.refreshSession.mockResolvedValue({
      data: {
        session: {
          access_token: 'new-access',
          refresh_token: 'new-refresh',
          expires_at: Math.floor(Date.now() / 1000) + 1800,
        },
      },
      error: null,
    });
    authMock.getUser.mockResolvedValue({
      data: { user: mockUser },
      error: null,
    });

    const user = await getCurrentUser();
    expect(user.email).toBe(mockUser.email);
    expect(localStorage.getItem('access_token')).toBe('new-access');
    expect(authMock.getUser).toHaveBeenCalledWith('new-access');
  });

  it('logout clears tokens even when signOut throws', async () => {
    localStorage.setItem('access_token', 'tok');
    authMock.signOut.mockRejectedValue(new Error('network'));
    await logout();
    expect(localStorage.getItem('access_token')).toBeNull();
  });

  it('requestPasswordReset and confirmPasswordReset succeed', async () => {
    authMock.resetPasswordForEmail.mockResolvedValue({ data: {}, error: null });
    authMock.updateUser.mockResolvedValue({ data: { user: mockUser }, error: null });

    await expect(requestPasswordReset(mockUser.email)).resolves.toEqual({
      message: 'Password reset email sent',
    });
    await expect(confirmPasswordReset('tok', 'NewPass1!')).resolves.toEqual({
      message: 'Password updated',
    });
  });

  it('isLoggedIn reflects token presence and expiry', () => {
    expect(isLoggedIn()).toBe(false);
    localStorage.setItem('access_token', 'tok');
    localStorage.setItem('expires_at', String(Math.floor(Date.now() / 1000) + 600));
    expect(isLoggedIn()).toBe(true);
  });
});

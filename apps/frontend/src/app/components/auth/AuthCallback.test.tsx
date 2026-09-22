import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { act, fireEvent, render, screen, waitFor } from '@testing-library/react';

import { AuthCallback } from './AuthCallback';

const mockToast = vi.hoisted(() => ({
  success: vi.fn(),
  error: vi.fn(),
}));

const mockConfirmEmail = vi.hoisted(() => vi.fn());

vi.mock('sonner', () => ({
  toast: mockToast,
}));

vi.mock('@/utils/authService', () => ({
  confirmEmail: mockConfirmEmail,
}));

describe('AuthCallback', () => {
  let originalLocation: Location;

  beforeEach(() => {
    vi.clearAllMocks();
    originalLocation = window.location;

    Object.defineProperty(window, 'location', {
      writable: true,
      value: {
        hash: '',
        href: 'http://localhost/',
        search: '',
        pathname: '/',
      },
    });

    vi.spyOn(console, 'warn').mockImplementation(() => {});
    vi.spyOn(console, 'error').mockImplementation(() => {});
    vi.spyOn(console, 'log').mockImplementation(() => {});
  });

  afterEach(() => {
    vi.useRealTimers();
    vi.restoreAllMocks();
    Object.defineProperty(window, 'location', {
      writable: true,
      value: originalLocation,
    });
  });

  it('shows error state by default when no token is present', async () => {
    render(<AuthCallback />);

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Error' })).toBeInTheDocument();
      expect(
        screen.getByText('Invalid callback URL. Please try again.'),
      ).toBeInTheDocument();
    });
  });

  it('shows error state when callback has no access token', async () => {
    window.location.hash = '#type=signup';

    render(<AuthCallback />);

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Error' })).toBeInTheDocument();
      expect(
        screen.getByText('Invalid callback URL. Please try again.'),
      ).toBeInTheDocument();
      expect(mockToast.error).toHaveBeenCalledWith('Authentication failed');
    });

    await waitFor(
      () => {
        expect(window.location.href).toBe('/');
        expect(window.location.hash).toBe('');
      },
      { timeout: 3000 },
    );
  });

  it('confirms email via token_hash query params', async () => {
    const onVerified = vi.fn();
    window.location.search = '?token_hash=hash123&type=email';
    window.location.pathname = '/auth/confirm';
    mockConfirmEmail.mockResolvedValue({
      user: { id: 'u1', email: 'op@example.com', metadata: {} },
      session: {
        access_token: 'at',
        refresh_token: 'rt',
        expires_at: 99,
      },
    });

    render(<AuthCallback onVerified={onVerified} />);

    await waitFor(() => {
      expect(mockConfirmEmail).toHaveBeenCalledWith({
        token_hash: 'hash123',
        type: 'email',
      });
      expect(mockToast.success).toHaveBeenCalledWith('Email verified successfully!');
      expect(onVerified).toHaveBeenCalledTimes(1);
    });
  });

  it('token_hash recovery redirects to reset with access token', async () => {
    window.location.search = '?token_hash=hash123&type=recovery';
    window.location.pathname = '/auth/confirm';
    mockConfirmEmail.mockResolvedValue({
      user: { id: 'u1', email: 'op@example.com', metadata: {} },
      session: {
        access_token: 'reset-at',
        refresh_token: 'rt',
        expires_at: 99,
      },
    });

    render(<AuthCallback />);

    await waitFor(() => {
      expect(window.location.href).toBe('/auth/reset?token=reset-at');
    });
  });

  it('token_hash recovery without session redirects home', async () => {
    window.location.search = '?token_hash=hash123&type=recovery';
    mockConfirmEmail.mockResolvedValue({
      user: { id: 'u1', email: 'op@example.com', metadata: {} },
      session: null,
    });

    render(<AuthCallback />);

    await waitFor(() => {
      expect(window.location.href).toBe('/');
    });
  });

  it('token_hash uses onLogin when onVerified is absent', async () => {
    const onLogin = vi.fn();
    window.location.search = '?token_hash=hash123&type=email';
    mockConfirmEmail.mockResolvedValue({
      user: { id: 'u1', email: 'op@example.com', metadata: {} },
      session: {
        access_token: 'at',
        refresh_token: 'rt',
        expires_at: 99,
      },
    });

    render(<AuthCallback onLogin={onLogin} />);

    await waitFor(() => {
      expect(onLogin).toHaveBeenCalledWith('op@example.com', false, 'at');
    });
  });

  it('token_hash uses onRegister when session is missing', async () => {
    const onRegister = vi.fn();
    window.location.search = '?token_hash=hash123&type=email';
    mockConfirmEmail.mockResolvedValue({
      user: { id: 'u1', email: 'op@example.com', metadata: {} },
      session: null,
    });

    render(<AuthCallback onRegister={onRegister} />);

    await waitFor(() => {
      expect(onRegister).toHaveBeenCalledWith('op@example.com');
    });
  });

  it('token_hash without handlers redirects home', async () => {
    window.location.search = '?token_hash=hash123&type=email';
    mockConfirmEmail.mockResolvedValue({
      user: { id: 'u1', email: 'op@example.com', metadata: {} },
      session: null,
    });

    render(<AuthCallback />);

    await waitFor(() => {
      expect(window.location.href).toBe('/');
    });
  });

  it('handles signup token with onVerified callback', async () => {
    const onVerified = vi.fn();
    window.location.hash = '#access_token=abc123&type=signup';

    render(<AuthCallback onVerified={onVerified} />);

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Success' })).toBeInTheDocument();
      expect(screen.getByText('Email verified! Redirecting...')).toBeInTheDocument();
      expect(mockToast.success).toHaveBeenCalledWith('Email verified successfully!');
      expect(onVerified).toHaveBeenCalledTimes(1);
    });

    expect(window.location.hash).toBe('');
  });

  it('falls back to onRegister for signup when onVerified is missing', async () => {
    const onRegister = vi.fn();
    window.location.hash = '#access_token=abc123&type=signup';

    render(<AuthCallback onRegister={onRegister} />);

    await waitFor(() => {
      expect(onRegister).toHaveBeenCalledWith('');
    });
  });

  it('signup with neither onVerified nor onRegister still succeeds', async () => {
    window.location.hash = '#access_token=abc123&type=signup';
    render(<AuthCallback />);
    await waitFor(() => {
      expect(mockToast.success).toHaveBeenCalled();
    });
  });

  it('redirects to reset route for recovery type', async () => {
    window.location.hash = '#access_token=reset-token&type=recovery';

    render(<AuthCallback />);

    await waitFor(() => {
      expect(window.location.href).toBe('/auth/reset?token=reset-token');
    });
  });

  it('redirects to home route for default callback type', async () => {
    window.location.hash = '#access_token=plain-token&type=magiclink';

    render(<AuthCallback />);

    await waitFor(() => {
      expect(window.location.href).toBe('/');
    });
  });

  it('enters catch path when callback handler throws', async () => {
    const onVerified = vi.fn(() => {
      throw new Error('handler failure');
    });
    window.location.hash = '#access_token=abc123&type=signup';

    render(<AuthCallback onVerified={onVerified} />);

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Error' })).toBeInTheDocument();
      expect(screen.getByText('handler failure')).toBeInTheDocument();
      expect(mockToast.error).toHaveBeenCalledWith('Authentication failed');
    });

    await waitFor(
      () => {
        expect(window.location.href).toBe('/');
        expect(window.location.hash).toBe('');
      },
      { timeout: 3000 },
    );
  });

  it('uses default catch message when thrown value has no Error message', async () => {
    const onVerified = vi.fn(() => {
      throw new Error('');
    });
    window.location.hash = '#access_token=abc123&type=signup';

    render(<AuthCallback onVerified={onVerified} />);

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Error' })).toBeInTheDocument();
      expect(
        screen.getByText('An error occurred. Please try again.'),
      ).toBeInTheDocument();
      expect(mockToast.error).toHaveBeenCalledWith('Authentication failed');
    });
  });

  it('redirects home after catch block timeout using fake timers', async () => {
    vi.useFakeTimers();
    const onVerified = vi.fn(() => {
      throw new Error('handler failure');
    });
    window.location.hash = '#access_token=abc123&type=signup';

    render(<AuthCallback onVerified={onVerified} />);

    await act(async () => {
      await Promise.resolve();
    });

    expect(screen.getByRole('heading', { name: 'Error' })).toBeInTheDocument();

    act(() => {
      vi.advanceTimersByTime(2000);
    });

    expect(window.location.href).toBe('/');
    expect(window.location.hash).toBe('');
  });

  it('redirects to login when return button is clicked on error state', async () => {
    render(<AuthCallback />);

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Error' })).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole('button', { name: /return to login/i }));

    expect(window.location.href).toBe('/');
    expect(window.location.hash).toBe('');
  });
});

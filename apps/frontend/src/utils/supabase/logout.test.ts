import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { signOutWithScope } from './logout';

const signOut = vi.fn();

vi.mock('./client', () => ({
  getSupabaseClient: () => ({ auth: { signOut } }),
}));

describe('signOutWithScope', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  afterEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it('returns true when no access token is stored', async () => {
    await expect(signOutWithScope('local')).resolves.toBe(true);
    expect(signOut).not.toHaveBeenCalled();
  });

  it('returns true on successful sign out with bearer token', async () => {
    localStorage.setItem('access_token', 'test-access-token');
    localStorage.setItem('expires_at', String(Math.floor(Date.now() / 1000) + 3600));
    signOut.mockResolvedValue({ error: null });

    const result = await signOutWithScope('global');

    expect(result).toBe(true);
    expect(signOut).toHaveBeenCalledWith({ scope: 'global' });
  });

  it('returns false on auth error', async () => {
    localStorage.setItem('access_token', 'test-access-token');
    localStorage.setItem('expires_at', String(Math.floor(Date.now() / 1000) + 3600));
    signOut.mockResolvedValue({ error: { message: 'Unauthorized' } });

    await expect(signOutWithScope('others')).resolves.toBe(false);
  });

  it('returns false when signOut throws', async () => {
    localStorage.setItem('access_token', 'test-access-token');
    localStorage.setItem('expires_at', String(Math.floor(Date.now() / 1000) + 3600));
    signOut.mockRejectedValue(new Error('Network error'));

    await expect(signOutWithScope('local')).resolves.toBe(false);
  });
});

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { signOutWithScope } from './logout';

describe('signOutWithScope', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    localStorage.clear();
  });

  afterEach(() => {
    vi.restoreAllMocks();
    localStorage.clear();
  });

  it('returns true when no access token is stored', async () => {
    const fetchSpy = vi.spyOn(global, 'fetch');

    await expect(signOutWithScope('local')).resolves.toBe(true);
    expect(fetchSpy).not.toHaveBeenCalled();
  });

  it('returns true on successful sign out with bearer token', async () => {
    localStorage.setItem('access_token', 'test-access-token');
    localStorage.setItem('expires_at', String(Math.floor(Date.now() / 1000) + 3600));

    const fetchSpy = vi.spyOn(global, 'fetch').mockResolvedValue({
      ok: true,
      statusText: 'OK',
    } as Response);

    const result = await signOutWithScope('global');

    expect(result).toBe(true);
    expect(fetchSpy).toHaveBeenCalledWith(
      expect.stringContaining('/logout'),
      expect.objectContaining({
        method: 'POST',
        credentials: 'include',
        headers: expect.objectContaining({
          Authorization: 'Bearer test-access-token',
        }),
      }),
    );
  });

  it('returns false on non-ok response', async () => {
    localStorage.setItem('access_token', 'test-access-token');
    localStorage.setItem('expires_at', String(Math.floor(Date.now() / 1000) + 3600));

    vi.spyOn(global, 'fetch').mockResolvedValue({
      ok: false,
      status: 401,
      statusText: 'Unauthorized',
    } as Response);

    await expect(signOutWithScope('others')).resolves.toBe(false);
  });

  it('returns false when fetch throws', async () => {
    localStorage.setItem('access_token', 'test-access-token');
    localStorage.setItem('expires_at', String(Math.floor(Date.now() / 1000) + 3600));

    vi.spyOn(global, 'fetch').mockRejectedValue(new Error('Network error'));

    await expect(signOutWithScope('local')).resolves.toBe(false);
  });
});

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { signOutWithScope } from './logout'

describe('signOutWithScope', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('returns true on successful sign out', async () => {
    vi.spyOn(global, 'fetch').mockResolvedValue({
      ok: true,
      statusText: 'OK',
    } as Response)

    const result = await signOutWithScope('global')

    expect(result).toBe(true)
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/logout'),
      expect.objectContaining({
        method: 'POST',
        credentials: 'include',
      }),
    )
  })

  it('returns false on non-ok response', async () => {
    vi.spyOn(global, 'fetch').mockResolvedValue({
      ok: false,
      statusText: 'Unauthorized',
    } as Response)

    await expect(signOutWithScope('others')).resolves.toBe(false)
  })

  it('returns false when fetch throws', async () => {
    vi.spyOn(global, 'fetch').mockRejectedValue(new Error('Network error'))

    await expect(signOutWithScope('local')).resolves.toBe(false)
  })
})

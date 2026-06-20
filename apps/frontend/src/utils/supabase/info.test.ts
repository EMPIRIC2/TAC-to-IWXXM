import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

describe('supabase info exports', () => {
  beforeEach(() => {
    vi.resetModules()
    vi.restoreAllMocks()
  })

  afterEach(() => {
    vi.unstubAllEnvs()
    vi.restoreAllMocks()
  })

  it('extracts project id and API URL from environment', async () => {
    vi.stubEnv('VITE_SUPABASE_URL', 'https://demo-project.supabase.co')
    vi.stubEnv('VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY', 'anon-key')

    const info = await import('./info')

    expect(info.projectId).toBe('demo-project')
    expect(info.supabaseApiUrl).toBe('https://demo-project.supabase.co')
    expect(info.publicAnonKey).toBe('anon-key')
  })

  it('falls back to empty values and warns when env vars are missing', async () => {
    vi.stubEnv('VITE_SUPABASE_URL', '')
    vi.stubEnv('VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY', '')

    const warnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {})
    const info = await import('./info')

    expect(info.projectId).toBe('')
    expect(info.supabaseApiUrl).toBe('')
    expect(info.publicAnonKey).toBe('')
    expect(warnSpy).toHaveBeenCalledTimes(2)
  })
})

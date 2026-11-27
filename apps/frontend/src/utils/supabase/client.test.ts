/**
 * Supabase browser client coverage (DI-008 leftover after drawer removal).
 *
 * [Corpus: fr] #1696
 */
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

const createClient = vi.fn(() => ({
  auth: { signOut: vi.fn() },
  from: vi.fn(),
}));

vi.mock('@supabase/supabase-js', () => ({
  createClient: (...args: unknown[]) => createClient(...args),
}));

const getSupabaseUrl = vi.fn();
const getSupabasePublishableKey = vi.fn();

vi.mock('../runtime-config', () => ({
  getSupabaseUrl: () => getSupabaseUrl(),
  getSupabasePublishableKey: () => getSupabasePublishableKey(),
}));

describe('supabase client', () => {
  beforeEach(() => {
    vi.resetModules();
    vi.clearAllMocks();
    getSupabaseUrl.mockReturnValue('https://demo.supabase.co');
    getSupabasePublishableKey.mockReturnValue('anon-key');
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('builds a singleton client with auth session options', async () => {
    const mod = await import('./client');
    const first = mod.getSupabaseClient();
    const second = mod.getSupabaseClient();

    expect(first).toBe(second);
    expect(createClient).toHaveBeenCalledTimes(1);
    expect(createClient).toHaveBeenCalledWith(
      'https://demo.supabase.co',
      'anon-key',
      {
        auth: {
          persistSession: true,
          autoRefreshToken: true,
        },
      },
    );
  });

  it('logs when runtime config is missing and still constructs a client', async () => {
    getSupabaseUrl.mockReturnValue('');
    getSupabasePublishableKey.mockReturnValue('');
    const errorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    const mod = await import('./client');
    expect(mod.getSupabaseClient()).toBeTruthy();
    expect(errorSpy).toHaveBeenCalled();
    expect(createClient).toHaveBeenCalledWith('', '', expect.any(Object));
  });

  it('proxies legacy supabase property access onto the singleton', async () => {
    const mod = await import('./client');
    const client = mod.getSupabaseClient() as {
      from: ReturnType<typeof vi.fn>;
      supabaseUrl: string;
    };
    client.from.mockReturnValue('table');
    client.supabaseUrl = 'https://demo.supabase.co';

    expect(mod.supabase.from('metar')).toBe('table');
    expect(client.from).toHaveBeenCalledWith('metar');
    // Non-function properties are returned as-is (Proxy get branch).
    expect(mod.supabase.supabaseUrl).toBe('https://demo.supabase.co');
  });
});

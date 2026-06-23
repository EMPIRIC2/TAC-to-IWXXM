/**
 * Supabase client initialization — uses runtime config when available.
 */

import { createClient, type SupabaseClient } from '@supabase/supabase-js';

import { getSupabasePublishableKey, getSupabaseUrl } from './runtime-config';

let client: SupabaseClient | null = null;

function buildClient(): SupabaseClient {
  const supabaseUrl = getSupabaseUrl();
  const supabaseAnonKey = getSupabasePublishableKey();

  if (!supabaseUrl || !supabaseAnonKey) {
    console.error(
      'Missing Supabase configuration. Set /config.json or VITE_SUPABASE_URL + VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY',
    );
  }

  return createClient(supabaseUrl, supabaseAnonKey, {
    auth: {
      persistSession: true,
      autoRefreshToken: true,
    },
  });
}

/** Lazily construct the singleton Supabase browser client. */
export function getSupabaseClient(): SupabaseClient {
  if (!client) {
    client = buildClient();
  }
  return client;
}

/** @deprecated Prefer ``getSupabaseClient()`` — kept for existing imports. */
export const supabase = new Proxy({} as SupabaseClient, {
  get(_target, prop) {
    const value = (getSupabaseClient() as unknown as Record<string | symbol, unknown>)[
      prop
    ];
    return typeof value === 'function' ? value.bind(getSupabaseClient()) : value;
  },
});

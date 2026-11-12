import type { APIRequestContext } from '@playwright/test';

/**
 * Supabase GoTrue helpers for FE-direct Auth E2E (F31).
 *
 * API `/auth/login` is removed; tests that need a Bearer JWT call Supabase.
 */

/** Supabase project URL for FE-direct Auth (F31). */
export const E2E_SUPABASE_URL =
  process.env.E2E_SUPABASE_URL ??
  process.env.VITE_SUPABASE_URL ??
  process.env.SUPABASE_URL ??
  process.env.SUPABASE_PROJECT_URL ??
  '';

/** Supabase publishable (anon) key for password grant in E2E. */
export const E2E_SUPABASE_ANON_KEY =
  process.env.E2E_SUPABASE_ANON_KEY ??
  process.env.VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY ??
  process.env.SUPABASE_PUBLISHABLE_KEY ??
  '';

/**
 * Obtain an access token via Supabase GoTrue password grant (F31 FE-direct).
 *
 * @param request - Playwright API request context
 * @param email - Operator email
 * @param password - Operator password
 * @returns Access token string
 */
export async function loginAccessTokenViaSupabase(
  request: APIRequestContext,
  email: string,
  password: string,
): Promise<string> {
  if (!E2E_SUPABASE_URL || !E2E_SUPABASE_ANON_KEY) {
    throw new Error(
      'loginAccessTokenViaSupabase requires E2E_SUPABASE_URL + E2E_SUPABASE_ANON_KEY (or VITE_/SUPABASE_*)',
    );
  }
  const base = E2E_SUPABASE_URL.replace(/\/$/, '');
  const response = await request.post(`${base}/auth/v1/token?grant_type=password`, {
    headers: {
      apikey: E2E_SUPABASE_ANON_KEY,
      Authorization: `Bearer ${E2E_SUPABASE_ANON_KEY}`,
      'Content-Type': 'application/json',
    },
    data: { email, password },
    timeout: 30_000,
  });
  if (!response.ok()) {
    throw new Error(
      `Supabase password grant failed: ${response.status()} ${await response.text()}`,
    );
  }
  const body = (await response.json()) as { access_token?: string };
  const token = body.access_token ?? '';
  if (!token) {
    throw new Error('Supabase password grant returned no access_token');
  }
  return token;
}

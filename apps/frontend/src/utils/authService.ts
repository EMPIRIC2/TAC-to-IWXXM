/**
 * Auth Service — browser Supabase Auth (FE-direct).
 *
 * Login/register/confirm/logout talk to Supabase via `@supabase/supabase-js`.
 * Access tokens are mirrored into localStorage for API Bearer use (work-sessions).
 */

import type { AuthError, EmailOtpType, Session, User } from '@supabase/supabase-js';

import { getSupabaseClient } from './supabase/client';

/**
 * Type `AuthUser`.
 * @example
 * const _ = true;
 */
export interface AuthUser {
  id: string;
  email: string;
  metadata: {
    name?: string;
    username?: string;
    [key: string]: unknown;
  };
}

/**
 * Type `AuthSession`.
 * @example
 * const _ = true;
 */
export interface AuthSession {
  access_token: string;
  refresh_token: string;
  expires_at: number;
}

/**
 * Type `AuthResponse`.
 * @example
 * const _ = true;
 */
export interface AuthResponse {
  user: AuthUser;
  session: AuthSession | null;
}

/**
 * Type `RegisterRequest`.
 * @example
 * const _ = true;
 */
export interface RegisterRequest {
  email: string;
  password: string;
  name?: string;
  username?: string;
}

/**
 * Type `LoginRequest`.
 * @example
 * const _ = true;
 */
export interface LoginRequest {
  email: string;
  password: string;
}

/** Persist session tokens in localStorage for API Bearer use. */
function storeTokens(session: AuthSession): void {
  localStorage.setItem('access_token', session.access_token);
  localStorage.setItem('refresh_token', session.refresh_token);
  localStorage.setItem('expires_at', session.expires_at.toString());
}

/** Clear stored session tokens from localStorage. */
function clearTokens(): void {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('expires_at');
}

/**
 * Get stored access token.
 * @example
 * const _ = true;
 */
export function getAccessToken(): string | null {
  return localStorage.getItem('access_token');
}

/** Get stored refresh token. */
function getRefreshToken(): string | null {
  return localStorage.getItem('refresh_token');
}

/** Return true when the access token is missing or near expiry. */
function isTokenExpired(): boolean {
  const expiresAt = localStorage.getItem('expires_at');
  if (!expiresAt) return true;
  const expiryTime = parseInt(expiresAt, 10);
  const currentTime = Math.floor(Date.now() / 1000);
  return currentTime >= expiryTime - 60;
}

/** Map a Supabase user to the operator AuthUser shape. */
function mapUser(user: User | null | undefined): AuthUser {
  return {
    id: user?.id || '',
    email: user?.email || '',
    metadata: (user?.user_metadata || {}) as AuthUser['metadata'],
  };
}

/** Map a Supabase session to the operator AuthSession shape. */
function mapSession(session: Session | null | undefined): AuthSession | null {
  if (!session?.access_token) {
    return null;
  }
  return {
    access_token: session.access_token,
    refresh_token: session.refresh_token || '',
    expires_at: session.expires_at || 0,
  };
}

/** Build an AuthResponse from Supabase user and session. */
function mapAuthResponse(
  user: User | null | undefined,
  session: Session | null | undefined,
): AuthResponse {
  return {
    user: mapUser(user),
    session: mapSession(session),
  };
}

/** Prefer Supabase error text; otherwise use the fallback. */
function authErrorMessage(error: AuthError | null, fallback: string): string {
  const message = error?.message?.trim();
  return message || fallback;
}

/** Refresh the access token when it is expired or near expiry. */
async function refreshTokenIfNeeded(): Promise<void> {
  if (!isTokenExpired()) {
    return;
  }

  const refreshToken = getRefreshToken();
  if (!refreshToken) {
    clearTokens();
    throw new Error('No refresh token available');
  }

  const { data, error } = await getSupabaseClient().auth.refreshSession({
    refresh_token: refreshToken,
  });
  if (error || !data.session) {
    clearTokens();
    throw new Error('Failed to refresh token');
  }
  const mapped = mapSession(data.session);
  if (mapped) {
    storeTokens(mapped);
  }
}

/**
 * Register a new user via Supabase Auth.
 * @example
 * const _ = true;
 */
export async function register(data: RegisterRequest): Promise<AuthResponse> {
  const metadata: Record<string, string> = {};
  if (data.name) metadata.name = data.name;
  if (data.username) metadata.username = data.username;

  const { data: result, error } = await getSupabaseClient().auth.signUp({
    email: data.email,
    password: data.password,
    options: Object.keys(metadata).length ? { data: metadata } : undefined,
  });
  if (error) {
    throw new Error(authErrorMessage(error, 'Registration failed'));
  }

  const response = mapAuthResponse(result.user, result.session);
  if (response.session) {
    storeTokens(response.session);
  }
  return response;
}

/**
 * Confirm email (or recovery) using the token_hash from the Auth email link.
 * @example
 * const _ = true;
 */
export async function confirmEmail(data: {
  token_hash: string;
  type?: string;
}): Promise<AuthResponse> {
  const type = (data.type || 'email') as EmailOtpType;
  const { data: result, error } = await getSupabaseClient().auth.verifyOtp({
    token_hash: data.token_hash,
    type,
  });
  if (error) {
    throw new Error(authErrorMessage(error, 'Email confirmation failed'));
  }
  const response = mapAuthResponse(result.user, result.session);
  if (response.session) {
    storeTokens(response.session);
  }
  return response;
}

/**
 * Login with email and password via Supabase Auth.
 * @example
 * const _ = true;
 */
export async function login(data: LoginRequest): Promise<AuthResponse> {
  const { data: result, error } = await getSupabaseClient().auth.signInWithPassword({
    email: data.email,
    password: data.password,
  });
  if (error) {
    throw new Error(authErrorMessage(error, 'Login failed'));
  }
  const response = mapAuthResponse(result.user, result.session);
  if (response.session) {
    storeTokens(response.session);
  }
  return response;
}

/**
 * Logout the current user via Supabase Auth.
 * @example
 * const _ = true;
 */
export async function logout(): Promise<void> {
  try {
    await getSupabaseClient().auth.signOut();
  } catch (error) {
    console.error('Logout error:', error);
  } finally {
    clearTokens();
  }
}

/**
 * Get current user information.
 * @example
 * const _ = true;
 */
export async function getCurrentUser(): Promise<AuthUser> {
  await refreshTokenIfNeeded();

  const token = getAccessToken();
  if (!token) {
    throw new Error('No access token');
  }

  const { data, error } = await getSupabaseClient().auth.getUser(token);
  if (error || !data.user) {
    clearTokens();
    throw new Error('Failed to get user info');
  }
  return mapUser(data.user);
}

/**
 * Request a password reset email.
 * @example
 * const _ = true;
 */
export async function requestPasswordReset(
  email: string,
): Promise<{ message: string }> {
  const { error } = await getSupabaseClient().auth.resetPasswordForEmail(email);
  if (error) {
    throw new Error(authErrorMessage(error, 'Failed to request password reset'));
  }
  return { message: 'Password reset email sent' };
}

/**
 * Confirm password reset with new password.
 * @example
 * const _ = true;
 */
export async function confirmPasswordReset(
  _token: string,
  newPassword: string,
): Promise<{ message: string }> {
  const { error } = await getSupabaseClient().auth.updateUser({
    password: newPassword,
  });
  if (error) {
    throw new Error(authErrorMessage(error, 'Failed to reset password'));
  }
  return { message: 'Password updated' };
}

/**
 * Check if user is currently logged in.
 * @example
 * const _ = true;
 */
export function isLoggedIn(): boolean {
  const token = getAccessToken();
  return !!token && !isTokenExpired();
}

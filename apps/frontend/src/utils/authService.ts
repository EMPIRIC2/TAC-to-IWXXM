/**
 * Auth Service API Client
 * 
 * Handles all authentication requests through the merged API host.
 * Auth routes are served at /auth/* on VITE_API_BASE_URL.
 */

import { authUrl, getApiBaseUrl } from './apiBase';

const API_BASE_URL = getApiBaseUrl();

console.log('[Auth Service] Initialized with URL:', API_BASE_URL);

export interface AuthUser {
  id: string;
  email: string;
  metadata: {
    name?: string;
    username?: string;
    [key: string]: unknown;
  };
}

export interface AuthSession {
  access_token: string;
  refresh_token: string;
  expires_at: number;
}

export interface AuthResponse {
  user: AuthUser;
  session: AuthSession | null;
}

export interface RegisterRequest {
  email: string;
  password: string;
  name?: string;
  username?: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

/**
 * Store tokens in localStorage
 */
function storeTokens(session: AuthSession): void {
  localStorage.setItem('access_token', session.access_token);
  localStorage.setItem('refresh_token', session.refresh_token);
  localStorage.setItem('expires_at', session.expires_at.toString());
}

/**
 * Clear stored tokens
 */
function clearTokens(): void {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('expires_at');
}

/**
 * Get stored access token
 */
export function getAccessToken(): string | null {
  return localStorage.getItem('access_token');
}

/**
 * Get stored refresh token
 */
function getRefreshToken(): string | null {
  return localStorage.getItem('refresh_token');
}

/**
 * Check if token is expired or about to expire (within 1 minute)
 */
function isTokenExpired(): boolean {
  const expiresAt = localStorage.getItem('expires_at');
  if (!expiresAt) return true;
  
  const expiryTime = parseInt(expiresAt, 10);
  const currentTime = Math.floor(Date.now() / 1000);
  
  // Consider expired if less than 1 minute remaining
  return currentTime >= (expiryTime - 60);
}

/**
 * Refresh the access token if needed
 */
async function refreshTokenIfNeeded(): Promise<void> {
  if (!isTokenExpired()) {
    console.log('[Auth Service] Token not expired, skipping refresh');
    return;
  }
  
  const refreshToken = getRefreshToken();
  if (!refreshToken) {
    console.error('[Auth Service] No refresh token available');
    throw new Error('No refresh token available');
  }
  
  console.log('[Auth Service] Refreshing token');
  
  try {
    const response = await fetch(authUrl('/refresh'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
    
    console.log('[Auth Service] Refresh response status:', response.status);
    
    if (!response.ok) {
      clearTokens();
      throw new Error('Failed to refresh token');
    }
    
    const session: AuthSession = await response.json();
    storeTokens(session);
    console.log('[Auth Service] Token refreshed successfully');
  } catch (error) {
    console.error('[Auth Service] Token refresh error:', error);
    clearTokens();
    throw error;
  }
}

/**
 * Register a new user
 */
export async function register(data: RegisterRequest): Promise<AuthResponse> {
  const url = authUrl('/register');
  console.log('[Auth Service] Registering user:', { email: data.email, url });
  
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    
    console.log('[Auth Service] Register response status:', response.status, response.statusText);
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      console.error('[Auth Service] Register error:', error);
      throw new Error(error.detail || 'Registration failed');
    }
    
    const result: AuthResponse = await response.json();
    console.log('[Auth Service] Register success for:', result.user?.email);
    
    if (result.session) {
      storeTokens(result.session);
    }
    
    return result;
  } catch (error) {
    console.error('[Auth Service] Register exception:', error);
    throw error;
  }
}

/**
 * Login with email and password
 */
export async function login(data: LoginRequest): Promise<AuthResponse> {
  const url = authUrl('/login');
  console.log('[Auth Service] Logging in user:', { email: data.email, url });
  
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    
    console.log('[Auth Service] Login response status:', response.status, response.statusText);
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      console.error('[Auth Service] Login error:', error);
      throw new Error(error.detail || 'Login failed');
    }
    
    const result: AuthResponse = await response.json();
    console.log('[Auth Service] Login success for:', result.user?.email);
    
    if (result.session) {
      storeTokens(result.session);
    }
    
    return result;
  } catch (error) {
    console.error('[Auth Service] Login exception:', error);
    throw error;
  }
}

/**
 * Logout the current user
 */
export async function logout(): Promise<void> {
  const token = getAccessToken();
  if (!token) return;
  
  try {
    await fetch(authUrl('/logout'), {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` },
    });
  } catch (error) {
    console.error('Logout error:', error);
  } finally {
    clearTokens();
  }
}

/**
 * Get current user information
 */
export async function getCurrentUser(): Promise<AuthUser> {
  console.log('[Auth Service] Getting current user');
  
  try {
    await refreshTokenIfNeeded();
    
    const token = getAccessToken();
    if (!token) {
      throw new Error('No access token');
    }
    
    const response = await fetch(authUrl('/me'), {
      method: 'GET',
      headers: { 'Authorization': `Bearer ${token}` },
    });
    
    console.log('[Auth Service] Get user response status:', response.status);
    
    if (!response.ok) {
      clearTokens();
      throw new Error('Failed to get user info');
    }
    
    const user = await response.json();
    console.log('[Auth Service] Got current user:', user.email);
    return user;
  } catch (error) {
    console.error('[Auth Service] Get user error:', error);
    throw error;
  }
}

/**
 * Request a password reset email
 */
export async function requestPasswordReset(email: string): Promise<{ message: string }> {
  const response = await fetch(authUrl('/password-reset/request'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email }),
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to request password reset');
  }
  
  return await response.json();
}

/**
 * Confirm password reset with new password
 * Requires reset token from email link
 */
export async function confirmPasswordReset(token: string, newPassword: string): Promise<{ message: string }> {
  const response = await fetch(authUrl('/password-reset/confirm'), {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify({ new_password: newPassword }),
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to reset password');
  }
  
  return await response.json();
}

/**
 * Check if user is currently logged in
 */
export function isLoggedIn(): boolean {
  const token = getAccessToken();
  return !!token && !isTokenExpired();
}

/**
 * Unified API base URL helpers (VITE_API_BASE_URL).
 * Single host for /api/v1/* and /auth/* per ADR-002 and deploy.md.
 */

const DEFAULT_DEV_API = 'http://localhost:18001';

function trimBaseUrl(url: string): string {
  return url.trim().replace(/\/+$/, '');
}

export function getApiBaseUrl(): string {
  const raw = import.meta.env.VITE_API_BASE_URL?.trim() ?? '';
  if (!raw) {
    return DEFAULT_DEV_API;
  }
  return trimBaseUrl(raw);
}

export function requireApiBaseUrl(): string {
  const raw = import.meta.env.VITE_API_BASE_URL?.trim() ?? '';
  if (!raw && import.meta.env.MODE === 'production') {
    throw new Error('VITE_API_BASE_URL must be set in production builds');
  }
  return trimBaseUrl(raw || DEFAULT_DEV_API);
}

export function apiUrl(path: string): string {
  const base = getApiBaseUrl();
  if (path.startsWith('/api/v1')) {
    return `${base}${path}`;
  }
  const normalized = path.startsWith('/') ? path : `/${path}`;
  return `${base}/api/v1${normalized}`;
}

export function authUrl(path: string): string {
  const base = getApiBaseUrl();
  const normalized = path.startsWith('/auth')
    ? path
    : `/auth${path.startsWith('/') ? path : `/${path}`}`;
  return `${base}${normalized}`;
}

export function adminUrl(path: string): string {
  const base = getApiBaseUrl();
  const normalized = path.startsWith('/admin')
    ? path
    : `/admin${path.startsWith('/') ? path : `/${path}`}`;
  return `${base}${normalized}`;
}

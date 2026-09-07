/**
 * Unified API base URL helpers.
 * Prefers runtime `/config.json` (via runtime-config) over bake-time
 * VITE_API_BASE_URL so DOKS/custom-domain deploys are not stuck on a stale
 * Render hostname (BUG-2026-08-04).
 */

import {
  getApiBaseUrl as getRuntimeApiBaseUrl,
  getRuntimeConfig,
} from './runtime-config';

const DEFAULT_DEV_API = 'http://localhost:18001';

function trimBaseUrl(url: string): string {
  return url.trim().replace(/\/+$/, '');
}

/** API base URL: runtime config after init, else Vite / local default. */
export function getApiBaseUrl(): string {
  return getRuntimeApiBaseUrl();
}

/**
 * Ensure a production build has a configured API host (config.json or VITE).
 * Rejects the silent localhost fallback when MODE is production.
 */
export function requireApiBaseUrl(): string {
  const base = getApiBaseUrl();
  if (import.meta.env.MODE === 'production') {
    const vite = import.meta.env.VITE_API_BASE_URL?.trim() ?? '';
    const runtime = getRuntimeConfig().api.baseUrl?.trim() ?? '';
    if (!vite && (!runtime || trimBaseUrl(runtime) === DEFAULT_DEV_API)) {
      throw new Error(
        'API base URL must be set via /config.json or VITE_API_BASE_URL in production builds',
      );
    }
  }
  return base;
}

/**
 * Build a fully qualified URL for an API v1 route.
 *
 * @param path - Route path; `/api/v1` prefix is added when absent.
 * @returns Absolute URL against the configured API base.
 */
export function apiUrl(path: string): string {
  const base = getApiBaseUrl();
  if (path.startsWith('/api/v1')) {
    return `${base}${path}`;
  }
  const normalized = path.startsWith('/') ? path : `/${path}`;
  return `${base}/api/v1${normalized}`;
}

/**
 * Build a fully qualified URL for an auth route on the API host.
 *
 * @param path - Auth subpath; `/auth` prefix is added when absent.
 * @returns Absolute auth URL against the configured API base.
 */
export function authUrl(path: string): string {
  const base = getApiBaseUrl();
  const normalized = path.startsWith('/auth')
    ? path
    : `/auth${path.startsWith('/') ? path : `/${path}`}`;
  return `${base}${normalized}`;
}

/**
 * Build a fully qualified URL for an admin route on the API host.
 *
 * @param path - Admin subpath; `/admin` prefix is added when absent.
 * @returns Absolute admin URL against the configured API base.
 */
export function adminUrl(path: string): string {
  const base = getApiBaseUrl();
  const normalized = path.startsWith('/admin')
    ? path
    : `/admin${path.startsWith('/') ? path : `/${path}`}`;
  return `${base}${normalized}`;
}

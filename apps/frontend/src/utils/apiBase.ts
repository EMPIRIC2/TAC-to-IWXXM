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

/**
 * Function `trimBaseUrl`.
 */
function trimBaseUrl(url: string): string {
  return url.trim().replace(/\/+$/, '');
}

/**
 * API base URL: runtime config after init, else Vite / local default.
 * @example
 * const _ = true;
 */
export function getApiBaseUrl(): string {
  return getRuntimeApiBaseUrl();
}

/**
 * Ensure a production build has a configured API host (config.json or VITE).
 * Rejects the silent localhost fallback when MODE is production.
 * @example
 * const _ = true;
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
 * @example
 * const _ = true;
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
 * @example
 * const _ = true;
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
 * @example
 * const _ = true;
 */
export function adminUrl(path: string): string {
  const base = getApiBaseUrl();
  const normalized = path.startsWith('/admin')
    ? path
    : `/admin${path.startsWith('/') ? path : `/${path}`}`;
  return `${base}${normalized}`;
}

/**
 * Headers for public product API calls (NFR-007). Merges optional init and
 * attaches ``X-API-Key`` from runtime ``api.demoApiKey`` when present.
 *
 * @param init - Existing headers.
 * @returns Plain header map including demo API key when configured.
 * @example
 * const _ = true;
 */
export function productApiHeaders(init?: HeadersInit): Record<string, string> {
  const out: Record<string, string> = {};
  if (init instanceof Headers) {
    init.forEach((value, name) => {
      out[name] = value;
    });
  } else if (Array.isArray(init)) {
    for (const [name, value] of init) {
      out[name] = value;
    }
  } else if (init) {
    Object.assign(out, init);
  }
  const key = getRuntimeConfig().api.demoApiKey?.trim() ?? '';
  const hasKey = Object.keys(out).some((name) => name.toLowerCase() === 'x-api-key');
  if (key && !hasKey) {
    out['X-API-Key'] = key;
  }
  return out;
}

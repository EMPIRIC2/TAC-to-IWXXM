/**
 * Runtime configuration loaded from /config.json with VITE_* fallback for local dev.
 * @example
 * const _ = true;
 */

export type MetarRuntimeConfig = {
  environment: string;
  api: {
    baseUrl: string;
    frontendUrl: string;
    corsOrigins?: string[];
    /** Demo API key for public routes (NFR-007 / A-007). */
    demoApiKey?: string;
  };
  supabase: {
    url: string;
    publishableKey?: string;
  };
  /** Optional Sentry DSN (EV-052); unset = disabled. */
  sentryDsn?: string;
};

let cachedConfig: MetarRuntimeConfig | null = null;

/**
 * Function `configFromViteEnv`.
 */
function configFromViteEnv(): MetarRuntimeConfig {
  return {
    environment: import.meta.env.MODE || 'development',
    api: {
      baseUrl: (import.meta.env.VITE_API_BASE_URL || 'http://localhost:18001').trim(),
      frontendUrl: (import.meta.env.VITE_APP_URL || 'http://localhost:18000').trim(),
      demoApiKey: (import.meta.env.VITE_DEMO_API_KEY || '').trim() || undefined,
    },
    supabase: {
      url: (import.meta.env.VITE_SUPABASE_URL || '').trim(),
      publishableKey: (
        import.meta.env.VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY || ''
      ).trim(),
    },
    sentryDsn: (import.meta.env.VITE_SENTRY_DSN || '').trim() || undefined,
  };
}

/**
 * Fill Auth bootstrap gaps when ``/config.json`` has URL but omits the
 * publishable key (DOKS ConfigMap drift). Prefer config.json values; merge
 * bake-time Vite env only for empty fields. [Corpus: api] [Corpus: env]
 */
function mergeViteAuthBootstrap(config: MetarRuntimeConfig): MetarRuntimeConfig {
  const vite = configFromViteEnv();
  const supabase = { ...(config.supabase || { url: '' }) };
  if (!String(supabase.url || '').trim() && vite.supabase.url) {
    supabase.url = vite.supabase.url;
  }
  if (!String(supabase.publishableKey || '').trim() && vite.supabase.publishableKey) {
    supabase.publishableKey = vite.supabase.publishableKey;
  }
  return { ...config, supabase };
}

/**
 * Load runtime config once per session (network fetch then Vite env fallback).
 * @example
 * const _ = true;
 */
export async function initRuntimeConfig(): Promise<MetarRuntimeConfig> {
  if (cachedConfig) {
    return cachedConfig;
  }

  try {
    const response = await fetch('/config.json', { cache: 'no-store' });
    if (response.ok) {
      cachedConfig = mergeViteAuthBootstrap(
        (await response.json()) as MetarRuntimeConfig,
      );
      return cachedConfig;
    }
  } catch {
    // Local dev may not have config.json until prepare-config runs.
  }

  cachedConfig = configFromViteEnv();
  return cachedConfig;
}

/**
 * Return loaded config.
 * After ``initRuntimeConfig``, returns the cached ``/config.json`` (or Vite
 * fallback from init). Before init, reads Vite env fresh (not cached) so
 * bake-time stubs and tests stay consistent.
 * @example
 * const _ = true;
 */
export function getRuntimeConfig(): MetarRuntimeConfig {
  if (cachedConfig) {
    return cachedConfig;
  }
  return configFromViteEnv();
}

/**
 * API base URL for merged backend (/api/v1/* and /auth/*).
 * @example
 * const _ = true;
 */
export function getApiBaseUrl(): string {
  return getRuntimeConfig().api.baseUrl.trim().replace(/\/+$/, '');
}

/**
 * Supabase project URL.
 * @example
 * const _ = true;
 */
export function getSupabaseUrl(): string {
  return getRuntimeConfig().supabase.url;
}

/**
 * Supabase publishable key for optional Auth FE client (F31 / F21 Amended).
 * @example
 * const _ = true;
 */
export function getSupabasePublishableKey(): string {
  return getRuntimeConfig().supabase.publishableKey || '';
}

/**
 * Runtime configuration loaded from /config.json with VITE_* fallback for local dev.
 */

export type MetarRuntimeConfig = {
  environment: string;
  api: {
    baseUrl: string;
    frontendUrl: string;
    corsOrigins?: string[];
    disableAuth?: boolean;
  };
  supabase: {
    url: string;
    publishableKey?: string;
  };
};

let cachedConfig: MetarRuntimeConfig | null = null;

function configFromViteEnv(): MetarRuntimeConfig {
  return {
    environment: import.meta.env.MODE || 'development',
    api: {
      baseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:18001',
      frontendUrl: import.meta.env.VITE_APP_URL || 'http://localhost:18000',
    },
    supabase: {
      url: import.meta.env.VITE_SUPABASE_URL || '',
      publishableKey: import.meta.env.VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY || '',
    },
  };
}

/**
 * Load runtime config once per session (network fetch then Vite env fallback).
 */
export async function initRuntimeConfig(): Promise<MetarRuntimeConfig> {
  if (cachedConfig) {
    return cachedConfig;
  }

  try {
    const response = await fetch('/config.json', { cache: 'no-store' });
    if (response.ok) {
      cachedConfig = (await response.json()) as MetarRuntimeConfig;
      return cachedConfig;
    }
  } catch {
    // Local dev may not have config.json until prepare-config runs.
  }

  cachedConfig = configFromViteEnv();
  return cachedConfig;
}

/** Return loaded config; throws if ``initRuntimeConfig`` was not called. */
export function getRuntimeConfig(): MetarRuntimeConfig {
  if (!cachedConfig) {
    cachedConfig = configFromViteEnv();
  }
  return cachedConfig;
}

/** API base URL for merged backend (/api/v1, /auth, /admin). */
export function getApiBaseUrl(): string {
  return getRuntimeConfig().api.baseUrl.replace(/\/$/, '');
}

/** Supabase project URL. */
export function getSupabaseUrl(): string {
  return getRuntimeConfig().supabase.url;
}

/** Supabase publishable key for browser client. */
export function getSupabasePublishableKey(): string {
  return getRuntimeConfig().supabase.publishableKey || '';
}

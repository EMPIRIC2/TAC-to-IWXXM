/** Shared env variable names — keep in sync with Python metar_shared.constants. */
export const METAR_CORS_ORIGINS_ENV = 'METAR_CORS_ORIGINS';
export const VITE_API_BASE_URL_ENV = 'VITE_API_BASE_URL';
export const VITE_SUPABASE_URL_ENV = 'VITE_SUPABASE_URL';
export const VITE_SUPABASE_PUBLISHABLE_KEY_ENV =
  'VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY';
export const VITE_APP_URL_ENV = 'VITE_APP_URL';

/**
 * Parse a comma-separated CORS origins env value into trimmed non-empty entries.
 *
 * @param raw - Raw env string, or `undefined` when unset.
 * @returns Origin strings; empty when input is blank or undefined.
 */
export function parseCommaSeparatedOrigins(raw: string | undefined): string[] {
  if (raw === undefined) {
    return [];
  }
  const trimmed = raw.trim();
  if (!trimmed) {
    return [];
  }
  return trimmed
    .split(',')
    .map((part) => part.trim())
    .filter((part) => part.length > 0);
}

export type {
  PendingFilePayload,
  WorkSession,
  WorkSessionListResponse,
  WorkSessionProduct,
  WorkSessionStatus,
  WorkSessionUpsertPayload,
} from './work-session';

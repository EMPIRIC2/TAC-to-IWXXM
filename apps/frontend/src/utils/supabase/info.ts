/**
 * Supabase project information
 * Extracted from environment variables for use in frontend components
 *
 * IMPORTANT: These MUST be provided at build time via environment variables:
 * - VITE_SUPABASE_URL: Your Supabase project URL
 * - VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY: Your Supabase publishable/anon key
 *
 * Do NOT hardcode credentials - they are publicly visible in the built app!
 */

// Extract project ID from Supabase URL
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || '';

if (!supabaseUrl) {
  console.warn('⚠️ VITE_SUPABASE_URL not set. Supabase integration will not work.');
}

export const projectId = supabaseUrl.split('//')[1]?.split('.')[0] || '';

// Public anon key for Supabase client
export const publicAnonKey =
  import.meta.env.VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY || '';

if (!publicAnonKey) {
  console.warn(
    '⚠️ VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY not set. Supabase integration will not work.',
  );
}

/**
 * Supabase URL for API calls
 */
export const supabaseApiUrl = supabaseUrl;

/** Edge function deployment slug for the bundled Hono server. */
export const edgeServerSlug = 'make-server-2e3cda33';

/**
 * Build the full HTTPS URL for a Supabase edge function subpath.
 *
 * @param subpath - Path after the deployment slug (e.g. ``database/upload``)
 * @returns Edge function URL for the current project
 */
export function edgeFunctionUrl(subpath: string): string {
  return `https://${projectId}.supabase.co/functions/v1/${edgeServerSlug}/${subpath}`;
}

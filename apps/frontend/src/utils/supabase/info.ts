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
export const publicAnonKey = import.meta.env.VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY || '';

if (!publicAnonKey) {
  console.warn('⚠️ VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY not set. Supabase integration will not work.');
}

/**
 * Supabase URL for API calls
 */
export const supabaseApiUrl = supabaseUrl;

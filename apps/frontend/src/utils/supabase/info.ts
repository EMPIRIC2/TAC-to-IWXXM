/**
 * Supabase project information from runtime config (with VITE fallback).
 */

import { getSupabasePublishableKey, getSupabaseUrl } from '../runtime-config';

export const supabaseApiUrl = getSupabaseUrl();
export const projectId = supabaseApiUrl.split('//')[1]?.split('.')[0] || '';
export const publicAnonKey = getSupabasePublishableKey();

if (!supabaseApiUrl) {
  console.warn('⚠️ Supabase URL not set. Supabase integration will not work.');
}

if (!publicAnonKey) {
  console.warn(
    '⚠️ Supabase publishable key not set. Supabase integration will not work.',
  );
}

export const edgeServerSlug = 'make-server-2e3cda33';

export function edgeFunctionUrl(subpath: string): string {
  return `https://${projectId}.supabase.co/functions/v1/${edgeServerSlug}/${subpath}`;
}

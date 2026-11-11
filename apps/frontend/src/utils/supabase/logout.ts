import { getAccessToken } from '../authService';
import { getSupabaseClient } from './client';

/**
 * Sign out the user with the requested Supabase scope.
 *
 * Uses the browser Supabase client (FE-direct Auth).
 */
export async function signOutWithScope(
  scope: 'global' | 'local' | 'others',
): Promise<boolean> {
  const token = getAccessToken();
  if (!token) {
    return true;
  }

  try {
    const { error } = await getSupabaseClient().auth.signOut({ scope });
    if (error) {
      console.error('Logout failed:', error.message);
      return false;
    }
    return true;
  } catch (error) {
    console.error('Logout error:', error);
    return false;
  }
}

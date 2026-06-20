import { authUrl } from '../apiBase';

/**
 * Sign out user with specified scope
 * Delegates to merged API auth routes for session management
 */

export async function signOutWithScope(scope: 'global' | 'local' | 'others'): Promise<boolean> {
  try {
    const response = await fetch(authUrl('/logout'), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ scope }),
      credentials: 'include',
    });

    if (!response.ok) {
      console.error('Logout failed:', response.statusText);
      return false;
    }

    return true;
  } catch (error) {
    console.error('Logout error:', error);
    return false;
  }
}

import { supabase } from './client';
import { toast } from 'sonner';

export type LogoutScope = 'global' | 'local' | 'others';

/**
 * Sign out with optional scope control
 * @param scope - 'global' (default): all sessions for user are terminated
 *                'local': only current session is terminated
 *                'others': all but current session are terminated
 */
export async function signOutWithScope(scope: LogoutScope = 'global'): Promise<boolean> {
  try {
    const { error } = await supabase.auth.signOut({ scope });

    if (error) {
      console.error(`Sign out error (${scope} scope):`, error);
      toast.error(error.message || `Failed to sign out (${scope})`);
      return false;
    }

    switch (scope) {
      case 'local':
        toast.success('✓ Signed out from this device');
        break;
      case 'others':
        toast.success('✓ Signed out from other devices');
        break;
      case 'global':
      default:
        toast.success('✓ Signed out from all devices');
    }

    return true;
  } catch (error) {
    console.error('Unexpected sign out error:', error);
    toast.error('An error occurred during sign out');
    return false;
  }
}

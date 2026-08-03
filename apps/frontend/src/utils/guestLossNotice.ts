/**
 * Guest loss-of-progress notice (F31 / UJ-045 / TC-F31-002).
 *
 * Persistent while the user is a guest **and** local/unsaved work exists.
 * Distinct from the F22 first-visit privacy notice.
 */

export interface GuestLossNoticeInput {
  /** True when a Supabase Auth session is active. */
  isLoggedIn: boolean;
  /** True when IndexedDB / guest converter state has unsaved or draft work. */
  hasLocalUnsavedWork: boolean;
}

/**
 * Whether the persistent guest loss-of-progress banner should render.
 *
 * Parameters
 * ----------
 * input :
 *     Login + local-work flags.
 *
 * Returns
 * -------
 * boolean
 *     ``true`` only for guests with local work (UJ-045 / ``D-S038-uj``).
 */
export function shouldShowGuestLossOfProgressNotice(
  input: GuestLossNoticeInput,
): boolean {
  if (input.isLoggedIn) {
    return false;
  }
  return input.hasLocalUnsavedWork;
}

/**
 * Human-readable copy for the persistent guest banner (UJ-045).
 */
export const GUEST_LOSS_OF_PROGRESS_MESSAGE =
  'Progress may be lost without signing in. Local drafts stay on this device only until you log in.';

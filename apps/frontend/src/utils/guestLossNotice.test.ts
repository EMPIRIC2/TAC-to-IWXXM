/**
 * Guest loss-of-progress copy — avoid “Sign in log in” with StatusBanner action.
 *
 * Evidence: EV-staging-adv-ux-reprobe viewport metrics (guest-loss noticeText).
 */

import { describe, expect, it } from 'vitest';

import {
  GUEST_LOSS_OF_PROGRESS_MESSAGE,
  shouldShowGuestLossOfProgressNotice,
} from './guestLossNotice';

describe('guestLossNotice', () => {
  it('shows only for guests with local work', () => {
    expect(
      shouldShowGuestLossOfProgressNotice({
        isLoggedIn: false,
        hasLocalUnsavedWork: true,
      }),
    ).toBe(true);
    expect(
      shouldShowGuestLossOfProgressNotice({
        isLoggedIn: true,
        hasLocalUnsavedWork: true,
      }),
    ).toBe(false);
  });

  it('does not end with log-in phrasing that duplicates the Sign in action', () => {
    expect(GUEST_LOSS_OF_PROGRESS_MESSAGE.toLowerCase()).toMatch(/lost/);
    expect(GUEST_LOSS_OF_PROGRESS_MESSAGE.toLowerCase()).not.toMatch(
      /until you log in/,
    );
    // Combined banner text is message + action "Sign in" — avoid trailing "log in"
    const withAction = `${GUEST_LOSS_OF_PROGRESS_MESSAGE} Sign in`;
    expect(withAction.toLowerCase()).not.toMatch(/log in\.?\s*sign in/);
    expect(withAction.toLowerCase()).not.toMatch(/sign in\.?\s*log in/);
  });
});

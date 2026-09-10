/**
 * Unit tests for beta feedback URL helpers (EV-1150).
 */

import { describe, expect, it } from 'vitest';

import {
  BETA_BADGE_LABEL,
  BETA_FEEDBACK_HELP,
  BETA_FEEDBACK_ISSUES_URL,
  BETA_FEEDBACK_LINK_LABEL,
} from './betaFeedback';
import { findInternalDocRefs } from './internalDocRefGuard';

describe('betaFeedback', () => {
  it('points at the shared beta-feedback Issues URL', () => {
    expect(BETA_FEEDBACK_ISSUES_URL).toBe(
      'https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/new?labels=beta-feedback',
    );
    expect(BETA_FEEDBACK_ISSUES_URL).toContain('labels=beta-feedback');
  });

  it('uses plain-language copy without internal doc refs', () => {
    for (const text of [
      BETA_BADGE_LABEL,
      BETA_FEEDBACK_HELP,
      BETA_FEEDBACK_LINK_LABEL,
    ]) {
      expect(findInternalDocRefs(text)).toEqual([]);
    }
  });
});

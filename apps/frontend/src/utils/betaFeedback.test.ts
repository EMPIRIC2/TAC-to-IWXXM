/**
 * Unit tests for beta feedback URL helpers (EV-1150).
 */

import { describe, expect, it } from 'vitest';

import {
  BETA_BADGE_LABEL,
  BETA_FEEDBACK_HELP,
  BETA_FEEDBACK_ISSUES_URL,
  BETA_FEEDBACK_LINK_LABEL,
  buildBetaFeedbackIssueUrl,
  FEEDBACK_BUTTON_LABEL,
  FEEDBACK_CATEGORY_LABEL,
  FEEDBACK_CATEGORY_LABELS,
  FEEDBACK_CONTACT_LABEL,
  FEEDBACK_DIALOG_INTRO,
  FEEDBACK_MESSAGE_LABEL,
  FEEDBACK_MESSAGE_REQUIRED,
  FEEDBACK_OPEN_LABEL,
  FEEDBACK_PAGE_HINT,
  FEEDBACK_PAGE_LABEL,
  FEEDBACK_POPUP_BLOCKED,
  FEEDBACK_SUBMIT_LABEL,
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
      FEEDBACK_BUTTON_LABEL,
      FEEDBACK_OPEN_LABEL,
      FEEDBACK_DIALOG_INTRO,
      FEEDBACK_CATEGORY_LABEL,
      FEEDBACK_MESSAGE_LABEL,
      FEEDBACK_CONTACT_LABEL,
      FEEDBACK_PAGE_LABEL,
      FEEDBACK_PAGE_HINT,
      FEEDBACK_SUBMIT_LABEL,
      FEEDBACK_MESSAGE_REQUIRED,
      FEEDBACK_POPUP_BLOCKED,
      ...Object.values(FEEDBACK_CATEGORY_LABELS),
    ]) {
      expect(findInternalDocRefs(text)).toEqual([]);
    }
  });

  it('puts category and message on the beta-feedback URL and omits untyped report text', () => {
    const href = buildBetaFeedbackIssueUrl({
      category: 'bug',
      message: 'Button missing',
      contact: '  ',
      page: '',
    });
    const url = new URL(href);
    expect(url.searchParams.get('labels')).toBe('beta-feedback');
    expect(url.searchParams.get('title')).toBe('Beta feedback: Bug');
    const body = url.searchParams.get('body') ?? '';
    expect(body).toBe('Category: Bug\n\nButton missing');
    expect(body).not.toMatch(/METAR|<\?xml/);
    expect(
      href.startsWith('https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/new?'),
    ).toBe(true);
  });

  it('omits contact and page when they are absent and includes them when set', () => {
    const omitted = new URL(
      buildBetaFeedbackIssueUrl({
        category: 'other',
        message: '  A note  ',
      }),
    );
    expect(omitted.searchParams.get('title')).toBe('Beta feedback: Other');
    expect(omitted.searchParams.get('body')).toBe('Category: Other\n\nA note');

    const filled = new URL(
      buildBetaFeedbackIssueUrl({
        category: 'feature',
        message: 'Add this',
        contact: ' ada@example.com ',
        page: ' https://example.test/convert ',
      }),
    );
    expect(filled.searchParams.get('body')).toBe(
      'Category: Feature\n\nAdd this\n\nContact: ada@example.com\n\nPage: https://example.test/convert',
    );
  });
});

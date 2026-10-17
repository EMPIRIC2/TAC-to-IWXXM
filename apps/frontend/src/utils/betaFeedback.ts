/**
 * Shared beta feedback URL and operator copy (EV-1150 / ADR-043).
 *
 * Plain-language only — no internal planning vocabulary.
 */

/** GitHub Issues new-issue URL with the shared beta-feedback label. */
export const BETA_FEEDBACK_ISSUES_URL =
  'https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/new?labels=beta-feedback';

/** Short badge label shown next to beta controls. */
export const BETA_BADGE_LABEL = 'Beta';

/** One-line help near Dissemination / Send controls. */
export const BETA_FEEDBACK_HELP =
  'This feature is in beta. Share feedback via GitHub Issues.';

/** Accessible name for the feedback link. */
export const BETA_FEEDBACK_LINK_LABEL = 'Send beta feedback on GitHub';

/** Footer control label. */
export const FEEDBACK_BUTTON_LABEL = 'Feedback';

/** Accessible name for the footer Feedback control. */
export const FEEDBACK_OPEN_LABEL = 'Open feedback';

/** Dialog introduction. Nothing here is stored by the app. */
export const FEEDBACK_DIALOG_INTRO =
  'Report a bug, ask for a feature, or send a note. Submit opens a GitHub issue. This page does not save what you type.';

/** Category field label. */
export const FEEDBACK_CATEGORY_LABEL = 'Category';

/** Message field label. */
export const FEEDBACK_MESSAGE_LABEL = 'Message';

/** Optional contact field label. */
export const FEEDBACK_CONTACT_LABEL = 'Email or contact (optional)';

/** Optional page field label. */
export const FEEDBACK_PAGE_LABEL = 'Page (optional)';

/** Hint under the page field. */
export const FEEDBACK_PAGE_HINT =
  'Filled with this page. Clear it if you do not want it in the issue.';

/** Submit control label. */
export const FEEDBACK_SUBMIT_LABEL = 'Submit feedback';

/** Shown when the message is empty. */
export const FEEDBACK_MESSAGE_REQUIRED = 'Enter a message.';

/** Shown when the browser blocks the new tab. */
export const FEEDBACK_POPUP_BLOCKED =
  'The feedback page did not open. Allow pop-ups for this site and try again.';

/** Operator labels for the three feedback categories. */
export const FEEDBACK_CATEGORY_LABELS = {
  bug: 'Bug',
  feature: 'Feature',
  other: 'Other',
} as const;

/**
 * Category stored in the GitHub issue body.
 * @example
 * const _ = true;
 */
export type FeedbackCategory = keyof typeof FEEDBACK_CATEGORY_LABELS;

/**
 * Fields the operator typed. TAC and IWXXM are not included unless they paste them.
 * @example
 * const _ = true;
 */
export interface FeedbackIssueDraft {
  category: FeedbackCategory;
  message: string;
  contact?: string;
  page?: string;
}

/**
 * True when `value` is bug, feature, or other.
 * @param value - Select value
 * @returns Whether the value is a feedback category
 * @example
 * const _ = true;
 */
export function isFeedbackCategory(value: string): value is FeedbackCategory {
  return Object.hasOwn(FEEDBACK_CATEGORY_LABELS, value);
}

/**
 * Build the shared beta-feedback issue URL with the category and message in the body.
 * @param draft - Operator input
 * @returns Absolute GitHub new-issue URL
 * @example
 * const _ = true;
 */
export function buildBetaFeedbackIssueUrl(draft: FeedbackIssueDraft): string {
  const categoryLabel = FEEDBACK_CATEGORY_LABELS[draft.category];
  const lines = [`Category: ${categoryLabel}`, '', draft.message.trim()];
  const contact = draft.contact?.trim() ?? '';
  if (contact) {
    lines.push('', `Contact: ${contact}`);
  }
  const page = draft.page?.trim() ?? '';
  if (page) {
    lines.push('', `Page: ${page}`);
  }
  const url = new URL(BETA_FEEDBACK_ISSUES_URL);
  url.searchParams.set('title', `Beta feedback: ${categoryLabel}`);
  url.searchParams.set('body', lines.join('\n'));
  return url.toString();
}

/**
 * Open the feedback issue in a new tab.
 * @param url - Absolute issue URL
 * @returns False when the browser blocks the tab
 * @example
 * const _ = true;
 */
export function openBetaFeedbackIssue(url: string): boolean {
  const popup = window.open(url, '_blank', 'noopener,noreferrer');
  return popup !== null;
}

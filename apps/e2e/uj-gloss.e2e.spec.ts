/**
 * F38 Glossary — shell page, prefs opt-out, validation copy (UJ-GLOSS).
 *
 * Asserts structure via testids; avoids locking STE paraphrase wording.
 */
import { expect, test } from '@playwright/test';
import {
  dismissPrivacyNoticeIfPresent,
  openPublicConverter,
} from './playwright-e2e-helpers';

test.describe('Glossary shell page (F38 / UJ-GLOSS)', () => {
  test('success: Glossary page shows beta, citation, and seeded entry', async ({
    page,
  }) => {
    await openPublicConverter(page);
    await dismissPrivacyNoticeIfPresent(page);
    await page.getByTestId('shell-nav-glossary').click();
    await expect(page.getByTestId('annex3-glossary-page')).toBeVisible();
    await expect(page.getByTestId('glossary-beta-badge')).toBeVisible();
    await expect(page.getByTestId('glossary-citation')).toBeVisible();
    await expect(page.getByTestId('glossary-entry-sigmet')).toBeVisible();
    await expect(page.getByTestId('glossary-limited-meaning')).toBeVisible();
  });

  test('failure: search with no match leaves entry list empty of SIGMET', async ({
    page,
  }) => {
    await openPublicConverter(page);
    await dismissPrivacyNoticeIfPresent(page);
    await page.getByTestId('shell-nav-glossary').click();
    await page.getByTestId('glossary-search').fill('zzzz-no-match-xyz');
    await expect(page.getByTestId('glossary-entry-sigmet')).toHaveCount(0);
    await expect(page.getByTestId('glossary-entry-list')).toBeVisible();
  });

  test('validation mode: prefs opt-out control is reachable from converter', async ({
    page,
  }) => {
    await openPublicConverter(page);
    await dismissPrivacyNoticeIfPresent(page);
    await page
      .getByRole('button', { name: 'Open user preferences', exact: true })
      .click();
    await expect(page.getByTestId('glossary-hover-enabled')).toBeVisible();
    await expect(page.getByTestId('glossary-hover-enabled')).toBeChecked();
  });
});

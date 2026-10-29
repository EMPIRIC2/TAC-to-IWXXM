/**
 * H6′ — Dissemination ops shell tab removed from the public operator nav.
 *
 * Convert-side DisseminationDrawer coverage remains in
 * `uj027-030-dissemination-drawer.e2e.spec.ts`.
 */
import { expect, test } from '@playwright/test';
import {
  dismissPrivacyNoticeIfPresent,
  openPublicConverter,
} from './playwright-e2e-helpers';

test.describe('Dissemination ops shell tab', () => {
  test('public shell has no Dissemination ops tab or page', async ({ page }) => {
    await openPublicConverter(page);
    await dismissPrivacyNoticeIfPresent(page);

    await expect(page.getByTestId('app-shell-nav')).toBeVisible();
    await expect(page.getByTestId('shell-nav-converter')).toBeVisible();
    await expect(page.getByTestId('shell-nav-history')).toBeVisible();
    await expect(page.getByTestId('shell-nav-catalog')).toBeVisible();
    await expect(page.getByTestId('shell-nav-dissemination-ops')).toHaveCount(0);
    await expect(page.getByTestId('dissemination-ops-page')).toHaveCount(0);
  });
});

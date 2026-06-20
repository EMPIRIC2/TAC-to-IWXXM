/**
 * Credential preflight guard.
 *
 * This file is named "00-preflight" so it sorts before all other spec files
 * and runs first. It verifies that the admin credentials are configured AND
 * actually work against the app.  When credentials are wrong you get one clear
 * failure here instead of 12+ repeated timeout failures scattered across the
 * rest of the suite.
 *
 * If your test run does not need admin credentials (smoke / CI without secrets)
 * run only the credential-free spec files instead:
 *
 *   make test-e2e-playwright-smoke
 */
import { expect, test } from '@playwright/test';
import { ADMIN_EMAIL, ADMIN_PASSWORD } from './playwright-e2e-helpers';

test.describe('Preflight: Admin Credential Guard', () => {
  test('admin credentials are configured and authenticate successfully', async ({ page }) => {
    if (!ADMIN_EMAIL || !ADMIN_PASSWORD) {
      throw new Error(
        'Preflight failed: PLAYWRIGHT_ADMIN_EMAIL and PLAYWRIGHT_ADMIN_PASSWORD are not set.\n' +
          'Set them in your shell or .env before running login-dependent tests.\n' +
          'To skip login tests entirely, run: make test-e2e-playwright-smoke'
      );
    }

    await page.goto('/');
    await expect(page.getByRole('heading', { name: /METAR Converter/i })).toBeVisible();

    await page.locator('#email').fill(ADMIN_EMAIL);
    await page.locator('#password').fill(ADMIN_PASSWORD);
    await page.getByRole('button', { name: /sign in to account/i }).click();

    await expect(
      page.getByRole('heading', { name: /Admin Dashboard/i }),
      `Preflight failed: login with "${ADMIN_EMAIL}" did not reach the Admin Dashboard. ` +
        'PLAYWRIGHT_ADMIN_EMAIL / PLAYWRIGHT_ADMIN_PASSWORD appear to be invalid. ' +
        'Fix the credentials before re-running the full suite.'
    ).toBeVisible({ timeout: 15000 });
  });
});

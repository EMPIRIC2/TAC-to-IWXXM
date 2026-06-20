import { expect, test } from '@playwright/test';
import { ADMIN_EMAIL, ADMIN_PASSWORD, loginAsAdmin } from './playwright-e2e-helpers';

test.describe('Workflow: Logout Protection', () => {
  test('logout options are visible and this-device logout returns user to login form', async ({
    page,
  }) => {
    test.skip(
      !ADMIN_EMAIL || !ADMIN_PASSWORD,
      'Requires PLAYWRIGHT_ADMIN_EMAIL and PLAYWRIGHT_ADMIN_PASSWORD',
    );

    await loginAsAdmin(page);

    await page.getByRole('button', { name: /Logout options/i }).click();
    await expect(page.getByText('This Device')).toBeVisible();
    await expect(page.getByText('All Devices')).toBeVisible();
    await expect(page.getByText('Other Devices')).toBeVisible();

    await page.getByRole('button', { name: /Sign out from this device only/i }).click();

    await expect(page.locator('#email')).toBeVisible({ timeout: 10000 });
    await expect(page.locator('#password')).toBeVisible();
    await expect(
      page.getByRole('button', { name: /Sign in to account/i }),
    ).toBeVisible();

    await page.goto('/');
    await expect(page.locator('#email')).toBeVisible({ timeout: 10000 });
    await expect(page.getByRole('heading', { name: /METAR Converter/i })).toBeVisible();
  });
});

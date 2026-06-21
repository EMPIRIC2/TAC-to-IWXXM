import { expect, test } from '@playwright/test';
import { gotoLogin, loginAsAdmin } from './playwright-e2e-helpers';

test.describe('Authentication Flow', () => {
  test('login page loads correctly', async ({ page }) => {
    await gotoLogin(page);

    await expect(page.locator('#email')).toBeVisible();
    await expect(page.locator('#password')).toBeVisible();
    await expect(
      page.getByRole('button', { name: /sign in to account/i }),
    ).toBeVisible();
  });

  test('empty login validation shows required messages', async ({ page }) => {
    await gotoLogin(page);

    await page.getByRole('button', { name: /sign in to account/i }).click();

    await expect(page.getByText('Email is required')).toBeVisible();
    await expect(page.getByText('Password is required')).toBeVisible();
  });

  test('admin login reaches the admin dashboard', async ({ page }, testInfo) => {
    if (!process.env.ADMIN_EMAIL || !process.env.ADMIN_PASSWORD) {
      testInfo.skip(
        true,
        'Admin login requires ADMIN_EMAIL and ADMIN_PASSWORD (set in CI secrets for T2/T3)',
      );
    }

    await loginAsAdmin(page);

    await expect(page.getByText(/Logged in as: admin@metar\.local/i)).toBeVisible();
    await expect(
      page.getByRole('heading', { name: 'User Approvals', exact: true }),
    ).toBeVisible();
  });
});

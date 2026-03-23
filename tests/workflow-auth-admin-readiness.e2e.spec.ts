import { expect, test } from '@playwright/test';
import { ADMIN_EMAIL, ADMIN_PASSWORD, loginAsAdmin, openConverterFromAdmin } from './playwright-e2e-helpers';

test.describe('Workflow: Auth And Admin Readiness', () => {
  test('startup, login, admin readiness, and converter transition are stable', async ({ page }) => {
    test.skip(
      !ADMIN_EMAIL || !ADMIN_PASSWORD,
      'Requires PLAYWRIGHT_ADMIN_EMAIL and PLAYWRIGHT_ADMIN_PASSWORD'
    );

    await page.goto('/');
    await expect(page.getByRole('heading', { name: /METAR Converter/i })).toBeVisible();
    await expect(page.locator('#email')).toBeVisible();
    await expect(page.locator('#password')).toBeVisible();

    await loginAsAdmin(page);

    await expect(page.getByRole('heading', { name: /Admin Dashboard/i })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'User Approvals', exact: true })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'System Settings', exact: true })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'System Monitoring', exact: true })).toBeVisible();

    await openConverterFromAdmin(page);

    await expect(page.getByRole('heading', { name: /METAR.*IWXXM.*Converter/i })).toBeVisible();
    await expect(page.getByLabel(/Switch view/i)).toBeVisible();
    await expect(page.getByRole('button', { name: /Open user preferences/i })).toBeVisible();
  });

  test('admin panel navigation loop remains stable across repeated transitions', async ({ page }) => {
    test.skip(
      !ADMIN_EMAIL || !ADMIN_PASSWORD,
      'Requires PLAYWRIGHT_ADMIN_EMAIL and PLAYWRIGHT_ADMIN_PASSWORD'
    );

    await loginAsAdmin(page);

    for (let i = 0; i < 2; i += 1) {
      await page.getByText('System Settings').first().click();
      await expect(page.getByRole('heading', { name: 'System Settings', exact: true }).nth(1)).toBeVisible();

      await page.getByText('System Monitoring').first().click();
      await expect(page.getByRole('heading', { name: 'System Monitoring', exact: true }).nth(1)).toBeVisible();

      await page.getByText('User Approvals').first().click();
      await expect(page.getByRole('heading', { name: 'User Approvals', exact: true }).nth(1)).toBeVisible();
    }

    await openConverterFromAdmin(page);
    await expect(page.getByRole('heading', { name: /METAR.*IWXXM.*Converter/i })).toBeVisible();

    const viewSelect = page.getByLabel(/Switch view/i);
    await viewSelect.selectOption('admin');
    await expect(page.getByRole('heading', { name: /Admin Dashboard/i })).toBeVisible();
  });
});

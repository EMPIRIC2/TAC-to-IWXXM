import { expect, test } from '@playwright/test';
import { loginAsAdmin, openConverterFromAdmin } from './playwright-e2e-helpers';

test.describe('Admin Navigation', () => {
  test('admin dashboard renders after login', async ({ page }) => {
    await loginAsAdmin(page);

    await expect(page.getByRole('heading', { name: /Admin Dashboard/i })).toBeVisible();
    await expect(
      page.getByRole('heading', { name: 'User Approvals', exact: true }).first(),
    ).toBeVisible();
    await expect(
      page.getByRole('heading', { name: 'System Settings', exact: true }),
    ).toBeVisible();
    await expect(
      page.getByRole('heading', { name: 'System Monitoring', exact: true }),
    ).toBeVisible();
  });

  test('admin panels can be switched', async ({ page }) => {
    await loginAsAdmin(page);

    await page.getByText('System Settings').first().click();
    await expect(
      page.getByRole('heading', { name: 'System Settings', exact: true }).nth(1),
    ).toBeVisible();

    await page.getByText('System Monitoring').first().click();
    await expect(
      page.getByRole('heading', { name: 'System Monitoring', exact: true }).nth(1),
    ).toBeVisible();
  });

  test('admin can switch to converter and back from the view selector', async ({
    page,
  }) => {
    await loginAsAdmin(page);
    await openConverterFromAdmin(page);

    const viewSelect = page.getByLabel(/Switch view/i);
    await expect(viewSelect).toBeVisible();
    await expect(
      page.getByRole('heading', { name: /METAR.*IWXXM.*Converter/i }),
    ).toBeVisible();

    await viewSelect.selectOption('admin');
    await expect(page.getByRole('heading', { name: /Admin Dashboard/i })).toBeVisible();
  });

  test('logout scope menu is available from the admin dashboard', async ({ page }) => {
    await loginAsAdmin(page);

    await page.getByRole('button', { name: /Logout options/i }).click();

    await expect(page.getByText('This Device')).toBeVisible();
    await expect(page.getByText('All Devices')).toBeVisible();
    await expect(page.getByText('Other Devices')).toBeVisible();
  });
});

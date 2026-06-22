import { expect, test } from '@playwright/test';
import {
  ADMIN_EMAIL,
  ADMIN_PASSWORD,
  loginAsAdmin,
  openConverterFromAdmin,
} from './playwright-e2e-helpers';

test.describe('Workflow: Narrative Full Journey', () => {
  test('login -> preferences -> conversion -> theme -> logout', async ({ page }) => {
    test.skip(
      !ADMIN_EMAIL || !ADMIN_PASSWORD,
      'Requires PLAYWRIGHT_ADMIN_EMAIL and PLAYWRIGHT_ADMIN_PASSWORD',
    );

    await page.goto('/');
    await expect(page.getByRole('heading', { name: /METAR Converter/i })).toBeVisible();

    await loginAsAdmin(page);
    await expect(page.getByRole('heading', { name: /Admin Dashboard/i })).toBeVisible();

    await openConverterFromAdmin(page);
    await expect(
      page.getByRole('heading', { name: /METAR.*IWXXM.*Converter/i }),
    ).toBeVisible();

    await page.getByRole('button', { name: /Open user preferences/i }).click();
    await expect(
      page.getByRole('heading', { name: /User Preferences/i }),
    ).toBeVisible();

    await page.locator('#bulletin-id').fill('SZZZ99');
    await page.locator('#issuing-center').fill('KJFK');
    await page.locator('#iwxxm-version').selectOption('2023-1');
    await page.locator('#on-error').selectOption('fail');
    await page.getByRole('button', { name: /Save Preferences/i }).click();

    await expect(page.getByText(/Preferences saved successfully/i).first()).toBeVisible(
      {
        timeout: 10000,
      },
    );
    await page.getByRole('button', { name: 'Cancel', exact: true }).click();

    await page.getByLabel(/Expand parameters/i).click();
    await expect(page.locator('#param-bulletin-id')).toHaveValue('SZZZ99');
    await expect(page.locator('#param-issuing-center')).toHaveValue('KJFK');
    await expect(page.locator('#param-iwxxm-version')).toHaveValue('2023-1');
    await expect(page.locator('#param-on-error')).toHaveValue('fail');

    await page
      .getByLabel(/Enter METAR data manually/i)
      .fill('METAR KJFK 121251Z 24016G28KT 3SM -RA BR BKN020 OVC040 14/11 A2990');
    await page
      .getByRole('button', { name: /Convert METAR files to IWXXM XML/i })
      .click();

    await expect(page.getByRole('region', { name: /conversion results/i })).toBeVisible(
      { timeout: 15000 },
    );
    await expect(
      page
        .locator('pre')
        .filter({ hasText: /iwxxm|metar:/i })
        .first(),
    ).toBeVisible();

    const themeSwitch = page.getByRole('switch', { name: /Switch to .* mode/i });
    const initialThemeState = await themeSwitch.getAttribute('aria-checked');
    await themeSwitch.click();
    await expect
      .poll(async () => themeSwitch.getAttribute('aria-checked'))
      .not.toBe(initialThemeState);

    await page.getByRole('button', { name: /Logout options/i }).click();
    await expect(page.getByText('This Device')).toBeVisible();
    await page.getByRole('button', { name: /Sign out from this device only/i }).click();

    await expect(page.locator('#email')).toBeVisible({ timeout: 15000 });
    await expect(page.locator('#password')).toBeVisible();
    await expect(
      page.getByRole('button', { name: /Sign in to account/i }),
    ).toBeVisible();
  });
});

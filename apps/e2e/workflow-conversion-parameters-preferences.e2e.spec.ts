/**
 * Conversion parameters + slim user preferences (EV-040 / EV-061).
 */
import { expect, test } from '@playwright/test';
import { convertManualMetar, openPublicConverter } from './playwright-e2e-helpers';

test.describe('Workflow: Conversion Parameters And Preferences', () => {
  test('changing parameters before manual conversion produces conversion output', async ({
    page,
  }) => {
    await openPublicConverter(page);

    await page.getByLabel(/Expand parameters/i).click();
    await page.locator('#param-iwxxm-version').selectOption('2023-1');
    await page.locator('#param-on-error').selectOption('warn');

    await convertManualMetar(
      page,
      'METAR KJFK 121251Z 24016G28KT 3SM -RA BR BKN020 OVC040 14/11 A2990',
    );

    await expect(page.getByRole('region', { name: /conversion results/i })).toBeVisible(
      { timeout: 10000 },
    );
    await expect(
      page
        .locator('pre')
        .filter({ hasText: /iwxxm|metar:/i })
        .first(),
    ).toBeVisible();
  });

  test('preferences save display name and output extension', async ({ page }) => {
    await openPublicConverter(page);

    await page.getByRole('button', { name: /Open user preferences/i }).click();
    await expect(
      page.getByRole('heading', { name: /User Preferences/i }),
    ).toBeVisible();

    await page.locator('#display-name').fill('E2E Operator');
    await page.locator('#output-extension').selectOption('.iwxxm');
    await page.getByRole('button', { name: /Save preferences/i }).click();

    await expect(page.getByText(/Preferences saved successfully/i).first()).toBeVisible(
      { timeout: 5000 },
    );
    // Dialog stays open after save — close before reopening.
    await page.getByRole('button', { name: /^Cancel$/i }).click();
    await expect(page.getByRole('heading', { name: /User Preferences/i })).toHaveCount(
      0,
    );

    await page.getByRole('button', { name: /Open user preferences/i }).click();
    await expect(page.locator('#display-name')).toHaveValue('E2E Operator');
    await expect(page.locator('#output-extension')).toHaveValue('.iwxxm');
  });
});

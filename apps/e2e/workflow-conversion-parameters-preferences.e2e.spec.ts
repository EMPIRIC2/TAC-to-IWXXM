/**
 * Conversion parameters on the public converter (F21 — no Auth).
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

  test('preferences save and apply to converter parameter controls', async ({
    page,
  }) => {
    await openPublicConverter(page);

    await page.getByRole('button', { name: /Open user preferences/i }).click();
    await expect(
      page.getByRole('heading', { name: /User Preferences/i }),
    ).toBeVisible();

    await page.locator('#iwxxm-version').selectOption('2023-1');
    await page.getByRole('button', { name: /Save Preferences/i }).click();

    await page.getByLabel(/Expand parameters/i).click();
    await expect(page.locator('#param-iwxxm-version')).toHaveValue('2023-1');
  });
});

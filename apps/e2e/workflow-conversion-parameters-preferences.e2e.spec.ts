/**
 * Conversion parameters + slim user preferences (EV-040 / EV-061).
 */
import { expect, test } from '@playwright/test';
import {
  convertManualMetar,
  openConvertIwxxmTab,
  openPublicConverter,
} from './playwright-e2e-helpers';

test.describe('Workflow: Conversion Parameters And Preferences', () => {
  test('changing parameters before manual conversion produces conversion output', async ({
    page,
  }) => {
    await openPublicConverter(page);

    await page.getByLabel('Expand parameters', { exact: true }).click();
    await page.locator('#param-iwxxm-version').selectOption('2023-1');
    await page.locator('#param-on-error').selectOption('warn');

    await convertManualMetar(
      page,
      'METAR KJFK 121251Z 24016G28KT 3SM -RA BR BKN020 OVC040 14/11 A2990',
    );

    await openConvertIwxxmTab(page, 10_000);
    await expect(page.getByTestId('iwxxm-preview-xml')).toBeVisible();
  });

  test('preferences save display name and output extension', async ({ page }) => {
    await openPublicConverter(page);

    await page
      .getByRole('button', { name: 'Open user preferences', exact: true })
      .click();
    await expect(
      page.getByRole('heading', { name: 'User Preferences', exact: true }),
    ).toBeVisible();

    await page.locator('#display-name').fill('E2E Operator');
    await page.locator('#output-extension').selectOption('.iwxxm');
    // Privacy settings uses the same button name, so this stays inside the dialog.
    await page
      .getByRole('dialog', { name: 'User Preferences', exact: true })
      .getByRole('button', { name: 'Save preferences', exact: true })
      .click();

    await expect(
      page
        .getByRole('dialog', { name: 'User Preferences', exact: true })
        .getByText('Preferences saved successfully', { exact: true }),
    ).toBeVisible({ timeout: 5000 });
    await expect(
      page.locator('[data-sonner-toast] [data-title]', {
        hasText: /^Preferences saved successfully$/,
      }),
    ).toBeVisible();
    // Dialog stays open after save — close before reopening.
    // targets the Cancel button in preferences
    await page.getByRole('button', { name: /^Cancel$/i }).click();
    // Opposite state: the User Preferences heading is visible before Cancel.
    await expect(
      page.getByRole('heading', { name: 'User Preferences', exact: true }),
    ).toHaveCount(0);

    await page
      .getByRole('button', { name: 'Open user preferences', exact: true })
      .click();
    await expect(page.locator('#display-name')).toHaveValue('E2E Operator');
    await expect(page.locator('#output-extension')).toHaveValue('.iwxxm');
  });
});

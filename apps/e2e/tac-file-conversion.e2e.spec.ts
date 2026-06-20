import { expect, test } from '@playwright/test';
import {
  convertManualMetar,
  openConverterForE2e,
  openConverterWithMockSession,
} from './playwright-e2e-helpers';

test.describe('TAC File Conversion', () => {
  test('manual METAR input converts to IWXXM', async ({ page }) => {
    await openConverterForE2e(page);

    await convertManualMetar(
      page,
      'METAR KJFK 121251Z 24016G28KT 3SM -RA BR BKN020 OVC040 14/11 A2990'
    );

    await expect(page.getByRole('region', { name: /conversion results/i })).toBeVisible({ timeout: 10000 });
    await expect(page.locator('pre').filter({ hasText: /iwxxm|metar:/i }).first()).toBeVisible();
  });

  test('COR METAR input produces correction output', async ({ page }) => {
    await openConverterForE2e(page);

    await convertManualMetar(
      page,
      'METAR COR FAOR 101200Z 12012KT 9999 FEW020 22/14 Q1018'
    );

    const xmlOutput = page.locator('pre').filter({ hasText: /iwxxm|metar:/i }).first();
    await expect(xmlOutput).toBeVisible({ timeout: 10000 });
    await expect(xmlOutput).toContainText('reportStatus="CORRECTION"');
  });

  test('clear removes manual input', async ({ page }) => {
    await openConverterForE2e(page);

    const manualInput = page.getByLabel(/Enter METAR data manually/i);
    await manualInput.fill('METAR KDEN 121653Z 02006KT 10SM SCT050 21/08 A3010');
    await page.getByRole('button', { name: /Clear all pending files and manual input/i }).click();

    await expect(manualInput).toHaveValue('');
  });

  test('mocked success conversion shows success notification and results', async ({ page }) => {
    await page.route('**/api/v1/convert', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          results: [
            {
              name: 'manual_input.txt',
              content: '<iwxxm:METAR>mock-success</iwxxm:METAR>',
              source: 'manual_input',
              size_bytes: 39,
            },
          ],
          errors: [],
          issues: [],
          total_processed: 1,
          successful: 1,
          failed: 0,
        }),
      });
    });

    await openConverterWithMockSession(page);
    await convertManualMetar(page, 'METAR KJFK 121251Z 24016G28KT 3SM -RA BR BKN020 OVC040 14/11 A2990');

    await expect(page.getByText(/Successfully converted 1 file\(s\)/i)).toBeVisible({ timeout: 10000 });
    await expect(page.getByRole('region', { name: /conversion results/i })).toBeVisible();
    await expect(page.getByText('manual_input.txt')).toBeVisible();
  });

  test('mocked empty conversion result shows no-files-converted notification', async ({ page }) => {
    await page.route('**/api/v1/convert', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          results: [],
          errors: [],
          issues: [],
          total_processed: 1,
          successful: 0,
          failed: 0,
        }),
      });
    });

    await openConverterWithMockSession(page);
    await convertManualMetar(page, 'METAR EMPTY RESULTS CASE');

    await expect(page.getByText(/No files were converted/i).first()).toBeVisible({ timeout: 10000 });
    await expect(page.getByText(/Conversion Error/i).first()).toBeVisible();
  });

  test('mocked unauthorized conversion shows authentication notification', async ({ page }) => {
    await page.route('**/api/v1/convert', async (route) => {
      await route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({
          message: '401 unauthorized',
          errors: [],
        }),
      });
    });

    await openConverterWithMockSession(page);
    await convertManualMetar(page, 'METAR KDEN 121653Z 02006KT 10SM SCT050 21/08 A3010');

    await expect(
      page.getByText(/Authentication failed\. Please ensure you are logged in\./i).first()
    ).toBeVisible({ timeout: 10000 });
    await expect(page.getByText(/Conversion Error/i).first()).toBeVisible();
  });
});

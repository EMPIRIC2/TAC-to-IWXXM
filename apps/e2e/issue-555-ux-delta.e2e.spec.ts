/**
 * UJ-001 delta — error log + accumulate results (F7.r / #903 supersedes #555 replace).
 */
import { expect, test } from '@playwright/test';
import {
  convertManualMetar,
  openConvertConsoleTab,
  openConvertDownloadsTab,
  openConverterForE2e,
  openConvertSettings,
} from './playwright-e2e-helpers';

test.describe('UJ-001 delta — accumulate results + error log', () => {
  test('second successful convert accumulates with first result card', async ({
    page,
  }) => {
    await openConverterForE2e(page);

    const metarA = 'METAR KJFK 121251Z 24016G28KT 3SM -RA BR BKN020 OVC040 14/11 A2990';
    const metarB = 'METAR KDEN 121653Z 02006KT 10SM SCT050 21/08 A3010';

    await convertManualMetar(page, metarA);
    await openConvertDownloadsTab(page, 10_000);
    await expect(page.locator('[data-testid^="result-item-"]')).toHaveCount(1);

    await convertManualMetar(page, metarB);
    // Wait for accumulate before Downloads — openConvertDownloadsTab only
    // requires count > 0 and can race the second convert landing.
    await expect
      .poll(async () => page.locator('[data-testid^="result-item-"]').count(), {
        timeout: 30_000,
      })
      .toBe(2);
    await openConvertDownloadsTab(page, 10_000);
    const resultsRegion = page.getByRole('region', {
      name: 'Conversion results',
      exact: true,
    });
    // F7.r / #903 — accumulate (do not replace) across successful converts.
    const downloadSelects = resultsRegion.locator(
      '[data-testid^="convert-download-select-"]',
    );
    await expect(downloadSelects).toHaveCount(2);
    await expect(resultsRegion).toContainText('KJFK');
    await expect(resultsRegion).toContainText('KDEN');
    await openConvertSettings(page);
    await expect(page.getByTestId('download-zip-button')).toHaveAccessibleName(
      /download all 2 converted files as zip/i,
    );
  });

  test('invalid convert shows error log panel', async ({ page }) => {
    await openConverterForE2e(page);
    await convertManualMetar(page, 'METAR NOT A VALID');

    await openConvertConsoleTab(page);
    const errorLog = page.getByLabel('Conversion error log', { exact: true });
    await expect(errorLog).toBeVisible({
      timeout: 10000,
    });
    await expect(errorLog.getByText(/All conversions failed/i)).toBeVisible();
    await expect(errorLog.getByText(/No ICAO code found in TAC text/i)).toBeVisible();
  });
});

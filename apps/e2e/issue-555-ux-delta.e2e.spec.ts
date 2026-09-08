/**
 * UJ-001 delta — error log + accumulate results (F7.r / #903 supersedes #555 replace).
 */
import { expect, test } from '@playwright/test';
import { convertManualMetar, openConverterForE2e } from './playwright-e2e-helpers';

test.describe('UJ-001 delta — accumulate results + error log', () => {
  test('second successful convert accumulates with first result card', async ({
    page,
  }) => {
    await openConverterForE2e(page);

    const metarA = 'METAR KJFK 121251Z 24016G28KT 3SM -RA BR BKN020 OVC040 14/11 A2990';
    const metarB = 'METAR KDEN 121653Z 02006KT 10SM SCT050 21/08 A3010';

    await convertManualMetar(page, metarA);
    await expect(page.getByRole('region', { name: /conversion results/i })).toBeVisible(
      {
        timeout: 10000,
      },
    );

    await convertManualMetar(page, metarB);
    const resultsRegion = page.getByRole('region', { name: /conversion results/i });
    await expect(resultsRegion).toBeVisible({ timeout: 10000 });
    // F7.r / #903 — accumulate (do not replace) across successful converts.
    await expect(resultsRegion.getByText(/KJFK/i).first()).toBeVisible();
    await expect(resultsRegion.getByText(/KDEN/i).first()).toBeVisible();
    await expect(page.getByTestId('download-zip-button')).toHaveAccessibleName(
      /download all 2 converted files as zip/i,
    );
  });

  test('invalid convert shows error log panel', async ({ page }) => {
    await openConverterForE2e(page);
    await convertManualMetar(page, 'METAR NOT A VALID');

    const errorLog = page.getByLabel(/conversion error log/i);
    await expect(errorLog).toBeVisible({
      timeout: 10000,
    });
    await expect(errorLog.getByText(/All conversions failed/i)).toBeVisible();
    await expect(errorLog.getByText(/No ICAO code found in TAC text/i)).toBeVisible();
  });
});

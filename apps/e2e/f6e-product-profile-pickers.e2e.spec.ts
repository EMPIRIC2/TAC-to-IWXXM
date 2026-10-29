/**
 * T8.4 / H6 — F6.e product + Conversion library pickers (UJ-005) + UJ-008 smoke + UJ-050.
 *
 * Spec: docs/user-journeys.md UJ-005 / UJ-008 / UJ-050; docs/test-plan.md TC-F6-001,
 * TC-F6-010; TC-EVBRIDGE-007 (library hard cut).
 * F21: public convert — no Auth login fixture.
 */
import { expect, test } from '@playwright/test';
import {
  convertManualMetar,
  fillManualTac,
  openConvertDownloadsTab,
  openConvertSettings,
  openPublicConverter,
  playwrightApiBaseUrl,
} from './playwright-e2e-helpers';

const METAR_TAC = 'METAR KJFK 121251Z 24016G28KT 3SM -RA BR BKN020 OVC040 14/11 A2990';
const SPECI_TAC = 'SPECI KJFK 122045Z 18012KT 5SM 15/07 A3005=';

async function requireF6ePickers(page: import('@playwright/test').Page): Promise<void> {
  // Product / library / params live in Settings; seed TAC so the shell is open.
  await fillManualTac(page, 'METAR');
  await openConvertSettings(page);
  await expect(page.getByTestId('convert-setup')).toBeVisible();
  await expect(page.locator('#param-product')).toBeVisible();
  await page.getByTestId('convert-advanced-engines').locator('summary').click();
  await expect(page.getByTestId('conversion-library-select')).toBeVisible();
  await page.getByLabel('Expand parameters', { exact: true }).click();
  await expect(page.locator('#param-iwxxm-version')).toBeVisible();
}

test.describe('H6 / T8.4: F6.e product + Conversion library pickers', () => {
  test('UJ-005: METAR ICAO Conversion library via product/library pickers', async ({
    page,
  }) => {
    await openPublicConverter(page);
    await requireF6ePickers(page);

    await page.locator('#param-product').selectOption('METAR');
    await page
      .getByTestId('conversion-library-select')
      .selectOption('LIB.CONVERSION.ICAO_2025');
    await page.locator('#param-iwxxm-version').selectOption('2025-2');

    await convertManualMetar(page, METAR_TAC);

    await openConvertDownloadsTab(page, 30_000);
    await expect(
      // targets the converted XML content region for this result
      page.getByRole('region', { name: /^Converted XML content for .+$/ }),
    ).toBeVisible({ timeout: 15000 });
  });

  test('UJ-005: SPECI via explicit product + ICAO Conversion library', async ({
    page,
  }) => {
    await openPublicConverter(page);
    await requireF6ePickers(page);

    await page.locator('#param-product').selectOption('SPECI');
    await page
      .getByTestId('conversion-library-select')
      .selectOption('LIB.CONVERSION.ICAO_2025');

    await convertManualMetar(page, SPECI_TAC);

    await openConvertDownloadsTab(page, 30_000);
  });

  test('UJ-005: US Conversion library selectable with METAR', async ({ page }) => {
    await openPublicConverter(page);
    await requireF6ePickers(page);

    await page.locator('#param-product').selectOption('METAR');
    await page
      .getByTestId('conversion-library-select')
      .selectOption('LIB.CONVERSION.US_FAA_NWS');

    await convertManualMetar(page, METAR_TAC);

    await openConvertDownloadsTab(page, 30_000);
  });

  test('UJ-008: convert still reaches API after picker interaction', async ({
    page,
  }) => {
    await openPublicConverter(page);
    await requireF6ePickers(page);
    const api = playwrightApiBaseUrl();
    let hit = false;
    await page.route(`${api}/api/v1/convert`, async (route) => {
      hit = true;
      await route.continue();
    });
    await page
      .getByTestId('conversion-library-select')
      .selectOption('LIB.CONVERSION.ICAO_2025');
    await convertManualMetar(page, METAR_TAC);
    await openConvertDownloadsTab(page, 30_000);
    expect(hit).toBe(true);
  });
});

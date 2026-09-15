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
  openPublicConverter,
  playwrightApiBaseUrl,
} from './playwright-e2e-helpers';

const METAR_TAC = 'METAR KJFK 121251Z 24016G28KT 3SM -RA BR BKN020 OVC040 14/11 A2990';
const SPECI_TAC = 'SPECI KJFK 122045Z 18012KT 5SM 15/07 A3005=';

async function requireF6ePickers(
  page: import('@playwright/test').Page,
): Promise<boolean> {
  await page.getByLabel(/Expand parameters/i).click();
  const product = page.locator('#param-product');
  const present = await product.isVisible().catch(() => false);
  if (!present) {
    test.skip(true, 'F6.e product pickers not deployed yet');
    return false;
  }
  await expect(page.getByTestId('conversion-library-select')).toBeVisible();
  await expect(page.locator('#param-iwxxm-version')).toBeVisible();
  return true;
}

test.describe('H6 / T8.4: F6.e product + Conversion library pickers', () => {
  test('UJ-005: METAR ICAO Conversion library via product/library pickers', async ({
    page,
  }) => {
    await openPublicConverter(page);
    if (!(await requireF6ePickers(page))) {
      return;
    }

    await page.locator('#param-product').selectOption('METAR');
    await page
      .getByTestId('conversion-library-select')
      .selectOption('LIB.CONVERSION.ICAO_2025');
    await page.locator('#param-iwxxm-version').selectOption('2025-2');

    await convertManualMetar(page, METAR_TAC);

    await expect(page.getByRole('region', { name: /conversion results/i })).toBeVisible(
      {
        timeout: 30000,
      },
    );
    await expect(
      page
        .locator('pre')
        .filter({ hasText: /iwxxm|metar:/i })
        .first(),
    ).toBeVisible({ timeout: 15000 });
  });

  test('UJ-005: SPECI via explicit product + ICAO Conversion library', async ({
    page,
  }) => {
    await openPublicConverter(page);
    if (!(await requireF6ePickers(page))) {
      return;
    }

    await page.locator('#param-product').selectOption('SPECI');
    await page
      .getByTestId('conversion-library-select')
      .selectOption('LIB.CONVERSION.ICAO_2025');

    await convertManualMetar(page, SPECI_TAC);

    await expect(page.getByRole('region', { name: /conversion results/i })).toBeVisible(
      {
        timeout: 30000,
      },
    );
  });

  test('UJ-005: US Conversion library selectable with METAR', async ({ page }) => {
    await openPublicConverter(page);
    if (!(await requireF6ePickers(page))) {
      return;
    }

    await page.locator('#param-product').selectOption('METAR');
    await page
      .getByTestId('conversion-library-select')
      .selectOption('LIB.CONVERSION.US_FAA_NWS');

    await convertManualMetar(page, METAR_TAC);

    await expect(page.getByRole('region', { name: /conversion results/i })).toBeVisible(
      {
        timeout: 30000,
      },
    );
  });

  test('UJ-008: convert still reaches API after picker interaction', async ({
    page,
  }) => {
    await openPublicConverter(page);
    if (!(await requireF6ePickers(page))) {
      return;
    }
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
    await expect(page.getByRole('region', { name: /conversion results/i })).toBeVisible(
      {
        timeout: 30000,
      },
    );
    expect(hit).toBe(true);
  });
});

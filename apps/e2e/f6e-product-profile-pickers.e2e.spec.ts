/**
 * T8.4 / H6 — F6.e product + profile pickers (UJ-005) + UJ-008 smoke.
 *
 * Spec: docs/user-journeys.md UJ-005 / UJ-008; docs/test-plan.md TC-F6-001, TC-F6-010.
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
    test.skip(
      true,
      'F6.e product/profile pickers not deployed yet (needs M8 frontend)',
    );
    return false;
  }
  await expect(page.locator('#param-profile')).toBeVisible();
  await expect(page.locator('#param-iwxxm-version')).toBeVisible();
  return true;
}

test.describe('H6 / T8.4: F6.e product + profile pickers', () => {
  test('UJ-005: METAR annex3 convert via product/profile pickers', async ({ page }) => {
    await openPublicConverter(page);
    if (!(await requireF6ePickers(page))) {
      return;
    }

    await page.locator('#param-product').selectOption('METAR');
    await page.locator('#param-profile').selectOption('annex3');
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

  test('UJ-005: SPECI annex3 via explicit product', async ({ page }) => {
    await openPublicConverter(page);
    if (!(await requireF6ePickers(page))) {
      return;
    }

    await page.locator('#param-product').selectOption('SPECI');
    await page.locator('#param-profile').selectOption('annex3');

    await convertManualMetar(page, SPECI_TAC);

    await expect(page.getByRole('region', { name: /conversion results/i })).toBeVisible(
      {
        timeout: 30000,
      },
    );
  });

  test('UJ-005: iwxxm_us profile selectable with METAR', async ({ page }) => {
    await openPublicConverter(page);
    if (!(await requireF6ePickers(page))) {
      return;
    }

    await page.locator('#param-product').selectOption('METAR');
    await page.locator('#param-profile').selectOption('iwxxm_us');

    await convertManualMetar(page, METAR_TAC);

    await expect(page.getByRole('region', { name: /conversion results/i })).toBeVisible(
      {
        timeout: 30000,
      },
    );
  });

  test('UJ-008 smoke: unknown product rejected by convert API', async ({ request }) => {
    const apiBase = playwrightApiBaseUrl();

    const convert = await request.post(`${apiBase}/api/v1/convert`, {
      multipart: {
        manual_text: METAR_TAC,
        product: 'NOTAPRODUCT',
        profile: 'annex3',
        lint: 'false',
      },
    });

    expect([400, 422]).toContain(convert.status());
    const text = (await convert.text()).toLowerCase();
    expect(text).toMatch(/unsupported_product|unknown|product|conversion failed|error/);
  });
});

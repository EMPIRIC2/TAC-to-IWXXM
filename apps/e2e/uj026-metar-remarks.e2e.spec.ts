/**
 * UJ-026 / #667 — METAR REMARKS retain / exclusion (API + UI smoke).
 *
 * Spec: docs/user-journeys.md UJ-026; docs/test-plan.md TC-F6-013.
 * F21: public convert — no Auth login / Bearer.
 */
import { expect, test } from '@playwright/test';
import {
  convertManualMetar,
  openPublicConverter,
  playwrightApiBaseUrl,
} from './playwright-e2e-helpers';

const TAC_RMK = 'METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005 RMK AO2 SLP176=';
const TAC_FREE =
  'METAR KJFK 231751Z 18012KT 10SM CLR 15/07 A3005 RMK AO2 WND DATA ESTMD=';

test.describe('UJ-026: METAR REMARKS retain / exclusion', () => {
  test('API: annex3 convert returns REMARKS_EXCLUDED', async ({ request }) => {
    const convert = await request.post(`${playwrightApiBaseUrl()}/api/v1/convert`, {
      multipart: {
        manual_text: TAC_RMK,
        product: 'METAR',
        profile: 'annex3',
        iwxxm_version: '2025-2',
        lint: 'false',
      },
    });
    expect(convert.status()).toBe(200);
    const payload = await convert.json();
    const codes = (payload.issues || []).map((i: { code?: string }) => i.code);
    expect(codes).toContain('REMARKS_EXCLUDED');
    const xml = payload.results?.[0]?.content || '';
    expect(xml).not.toContain('iwxxm-us:Addendum');
  });

  test('API: iwxxm_us convert retains humanReadableText', async ({ request }) => {
    const convert = await request.post(`${playwrightApiBaseUrl()}/api/v1/convert`, {
      multipart: {
        manual_text: TAC_FREE,
        product: 'METAR',
        profile: 'iwxxm_us',
        iwxxm_version: '2025-2',
        lint: 'false',
      },
    });
    expect(convert.status()).toBe(200);
    const payload = await convert.json();
    const xml = payload.results?.[0]?.content || '';
    expect(xml).toContain('iwxxm-us:humanReadableText');
    expect(xml).toContain('WND DATA ESTMD');
  });

  test('UI: annex3 convert with RMK still yields results', async ({ page }) => {
    await openPublicConverter(page);
    const product = page.locator('#param-product');
    if (!(await product.isVisible().catch(() => false))) {
      await page
        .getByLabel(/Expand parameters/i)
        .click()
        .catch(() => undefined);
    }
    await page.locator('#param-product').selectOption('METAR');
    await page.locator('#param-profile').selectOption('annex3');
    await convertManualMetar(page, TAC_RMK);
    await expect(page.getByRole('region', { name: /conversion results/i })).toBeVisible(
      {
        timeout: 30000,
      },
    );
  });
});

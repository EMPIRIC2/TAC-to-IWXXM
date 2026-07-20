/**
 * UJ-026 / #667 — METAR REMARKS retain / exclusion (API + UI smoke).
 *
 * Spec: docs/user-journeys.md UJ-026; docs/test-plan.md TC-F6-013.
 * API assertions are the hard gate; UI checks soft-fail if issue chips are absent.
 */
import { expect, test } from '@playwright/test';
import {
  ADMIN_EMAIL,
  ADMIN_PASSWORD,
  convertManualMetar,
  loginAndOpenConverter,
} from './playwright-e2e-helpers';

const TAC_RMK = 'METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005 RMK AO2 SLP176=';
const TAC_FREE =
  'METAR KJFK 231751Z 18012KT 10SM CLR 15/07 A3005 RMK AO2 WND DATA ESTMD=';

function apiBase(): string {
  return (
    process.env.PLAYWRIGHT_API_BASE_URL ||
    process.env.LIVE_API_URL ||
    'https://metar-to-iwxxm-api.onrender.com'
  ).replace(/\/$/, '');
}

test.describe('UJ-026: METAR REMARKS retain / exclusion', () => {
  test.beforeEach(() => {
    test.skip(
      !ADMIN_EMAIL || !ADMIN_PASSWORD,
      'Requires PLAYWRIGHT_ADMIN_EMAIL / ADMIN_EMAIL credentials',
    );
  });

  test('API: annex3 convert returns REMARKS_EXCLUDED', async ({ request }) => {
    const login = await request.post(`${apiBase()}/auth/login`, {
      data: { email: ADMIN_EMAIL, password: ADMIN_PASSWORD },
    });
    test.skip(!login.ok(), `live login failed: ${login.status()}`);
    const body = await login.json();
    const token = body.access_token || body.token || body.session?.access_token;
    test.skip(!token, 'login missing access_token');

    const convert = await request.post(`${apiBase()}/api/v1/convert`, {
      headers: { Authorization: `Bearer ${token}` },
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
    const login = await request.post(`${apiBase()}/auth/login`, {
      data: { email: ADMIN_EMAIL, password: ADMIN_PASSWORD },
    });
    test.skip(!login.ok(), `live login failed: ${login.status()}`);
    const body = await login.json();
    const token = body.access_token || body.token || body.session?.access_token;
    test.skip(!token, 'login missing access_token');

    const convert = await request.post(`${apiBase()}/api/v1/convert`, {
      headers: { Authorization: `Bearer ${token}` },
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
    await loginAndOpenConverter(page);
    const product = page.locator('#param-product');
    if (await product.isVisible().catch(() => false)) {
      await page
        .getByLabel(/Expand parameters/i)
        .click()
        .catch(() => undefined);
      await page.locator('#param-product').selectOption('METAR');
      await page.locator('#param-profile').selectOption('annex3');
    }
    await convertManualMetar(page, TAC_RMK);
    await expect(page.getByRole('region', { name: /conversion results/i })).toBeVisible(
      {
        timeout: 30000,
      },
    );
  });
});

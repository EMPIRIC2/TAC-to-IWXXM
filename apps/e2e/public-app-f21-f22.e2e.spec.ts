/**
 * T7.1 — Public app F21/F22 Playwright smoke (UJ-001/033 + Auth-gone + privacy).
 *
 * Spec: docs/test-plan.md TC-F21-auth-gone, TC-F22-001..003, TC-004;
 * docs/user-journeys.md UJ-001 / UJ-033; S023 / EV-017.
 */
import { expect, test } from '@playwright/test';
import {
  convertManualMetar,
  openPublicConverter,
  openSignInFormThenReturn,
  playwrightApiFetch,
} from './playwright-e2e-helpers';

const SAMPLE_METAR =
  'METAR KJFK 121251Z 24016G28KT 3SM -RA BR BKN020 OVC040 14/11 A2990';
const LOWER_ST_MAARTEN = 'metar tncm 081200z 14006kt 9999 few020 28/24 q1013=';

test.describe('T7.1 — Public app + privacy (F21/F22)', () => {
  test('UJ-001: public convert without JWT (optional Sign in OK)', async ({ page }) => {
    const authHeaders: string[] = [];
    await page.route('**/api/v1/convert', async (route) => {
      const header = route.request().headers().authorization;
      if (header) {
        authHeaders.push(header);
      }
      await route.continue();
    });

    await openPublicConverter(page);
    await openSignInFormThenReturn(page);
    // Opposite state: the email field is on the sign-in form.
    await expect(page.locator('#email')).toHaveCount(0);

    await convertManualMetar(page, SAMPLE_METAR);
    await expect(page.getByRole('region', { name: /conversion results/i })).toBeVisible(
      {
        timeout: 15_000,
      },
    );
    expect(authHeaders).toEqual([]);
  });

  test('TC-F6-055: lowercase St Maarten METAR converts on the public page', async ({
    page,
  }) => {
    await openPublicConverter(page);
    await convertManualMetar(page, LOWER_ST_MAARTEN);
    const results = page.getByRole('region', { name: /conversion results/i });
    await expect(results).toBeVisible({ timeout: 15_000 });
    await expect(results).not.toContainText(/no METAR\/SPECI report found/i);
    await expect(results).toContainText(/TNCM/i);
  });

  test('TC-F22-001: first-visit privacy notice discloses IndexedDB', async ({
    page,
  }) => {
    await page.goto('/');
    await page.evaluate(() => {
      localStorage.setItem(
        'tac_privacy_preferences',
        JSON.stringify({
          schemaVersion: 2,
          necessary: true,
          analytics: false,
          marketing: false,
          workHistoryLocal: true,
          saleOrSharingOptOut: false,
          targetedAdvertisingOptOut: false,
          noticeAcknowledgedAt: null,
          noticeSchemaVersion: null,
          termsAcknowledgedAt: '2026-01-01T00:00:00.000Z',
        }),
      );
    });
    await page.reload();
    await expect(page.getByRole('heading', { name: /^TAC to IWXXM$/ })).toBeVisible({
      timeout: 10_000,
    });

    const notice = page.getByTestId('privacy-notice');
    await expect(notice).toBeVisible();
    await expect(notice).toContainText(/IndexedDB/i);

    await page.getByRole('button', { name: /dismiss privacy notice/i }).click();
    // Opposite state: the notice is visible before dismiss.
    await expect(notice).toHaveCount(0);

    await page.reload();
    await expect(page.getByRole('heading', { name: /^TAC to IWXXM$/ })).toBeVisible();
    // Opposite state: the same notice was visible before dismiss.
    await expect(page.getByTestId('privacy-notice')).toHaveCount(0);
  });

  test('TC-F22-002: Privacy settings opens from footer and discloses storage', async ({
    page,
  }) => {
    await openPublicConverter(page);

    // Footer control (exact) — notice also has "Open privacy settings from notice".
    await page
      .getByRole('button', { name: 'Open privacy settings', exact: true })
      .click();
    await expect(page.getByTestId('privacy-settings-dialog')).toBeVisible();
    await expect(page.getByText(/Work history and converter sessions/i)).toBeVisible();
    await expect(page.getByLabel(/necessary storage always enabled/i)).toBeDisabled();

    // Footer Cancel can sit below the viewport on provisional DOKS layouts.
    await page.keyboard.press('Escape');
    // Opposite state: the dialog is open before Escape.
    await expect(page.getByTestId('privacy-settings-dialog')).toHaveCount(0);
  });

  test('TC-F22-003: GPC signal shows enforced opt-outs in settings', async ({
    page,
  }) => {
    await page.addInitScript(() => {
      Object.defineProperty(navigator, 'globalPrivacyControl', {
        configurable: true,
        get: () => true,
      });
    });

    await page.goto('/');
    await expect(page.getByRole('heading', { name: /^TAC to IWXXM$/ })).toBeVisible({
      timeout: 10_000,
    });
    const notice = page.getByTestId('privacy-notice');
    await expect(notice).toBeVisible();
    await page.getByRole('button', { name: /dismiss privacy notice/i }).click();
    // Opposite state: the notice is visible on first visit before dismiss.
    await expect(notice).toHaveCount(0);

    await page
      .getByRole('button', { name: 'Open privacy settings', exact: true })
      .click();
    await expect(page.getByTestId('privacy-settings-dialog')).toBeVisible();
    await expect(page.getByTestId('privacy-gpc-active')).toBeVisible();
  });

  test('TC-F31-003: /auth/login rejects bad credentials (Auth restored)', async ({
    request,
  }) => {
    const response = await playwrightApiFetch(request, '/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      data: { email: 'x@y.z', password: 'nope' },
      timeout: 15_000,
    });
    // F21 Amended / F31 — route exists; invalid credentials → 401 (not 404).
    expect(response.status()).toBe(401);
  });
});

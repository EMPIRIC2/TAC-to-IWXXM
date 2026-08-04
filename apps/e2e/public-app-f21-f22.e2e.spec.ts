/**
 * T7.1 — Public app F21/F22 Playwright smoke (UJ-001/033 + Auth-gone + privacy).
 *
 * Spec: docs/test-plan.md TC-F21-auth-gone, TC-F22-001..003, TC-004;
 * docs/user-journeys.md UJ-001 / UJ-033; S023 / EV-017.
 */
import { expect, test } from '@playwright/test';
import {
  convertManualMetar,
  dismissPrivacyNoticeIfPresent,
  openPublicConverter,
  playwrightApiFetch,
} from './playwright-e2e-helpers';

const SAMPLE_METAR =
  'METAR KJFK 121251Z 24016G28KT 3SM -RA BR BKN020 OVC040 14/11 A2990';

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
    await expect(page.locator('#email')).toHaveCount(0);

    await convertManualMetar(page, SAMPLE_METAR);
    await expect(page.getByRole('region', { name: /conversion results/i })).toBeVisible(
      {
        timeout: 15_000,
      },
    );
    expect(authHeaders).toEqual([]);
  });

  test('TC-F22-001: first-visit privacy notice discloses IndexedDB', async ({
    page,
  }) => {
    await page.goto('/');
    await page.evaluate(() => {
      localStorage.removeItem('tac_privacy_preferences');
    });
    await page.reload();
    await expect(
      page.getByRole('heading', { name: /METAR.*IWXXM.*Converter/i }),
    ).toBeVisible({ timeout: 10_000 });

    const notice = page.getByTestId('privacy-notice');
    await expect(notice).toBeVisible();
    await expect(notice).toContainText(/IndexedDB/i);

    await page.getByRole('button', { name: /dismiss privacy notice/i }).click();
    await expect(notice).toHaveCount(0);

    await page.reload();
    await expect(
      page.getByRole('heading', { name: /METAR.*IWXXM.*Converter/i }),
    ).toBeVisible();
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
    await expect(
      page.getByRole('heading', { name: /METAR.*IWXXM.*Converter/i }),
    ).toBeVisible({ timeout: 10_000 });
    await dismissPrivacyNoticeIfPresent(page);
    await expect(page.getByTestId('privacy-notice')).toHaveCount(0);

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

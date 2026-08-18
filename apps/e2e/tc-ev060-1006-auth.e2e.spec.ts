/**
 * TC-EV060-1006 / UJ-003 / UJ-046 — Auth register, persist, logout, guest convert (#1006).
 *
 * Spec: docs/test-plan.md TC-EV060-1006-001..003; [Corpus: product §F31]
 * [Corpus: product §F21] [Corpus: journeys] [Corpus: tests].
 *
 * Register uses a unique @example.invalid address and stubs `/auth/register` so CI
 * does not create production accounts. Login/logout persist requires E2E_USER_* /
 * ADMIN_* (same as TC-F31-003/004).
 */
import { expect, test } from '@playwright/test';
import {
  convertManualMetar,
  E2E_USER_EMAIL,
  E2E_USER_PASSWORD,
  gotoRegister,
  loginAsE2EUser,
  openPublicConverter,
  playwrightApiFetch,
} from './playwright-e2e-helpers';

const SAMPLE_METAR =
  'METAR KJFK 121251Z 24016G28KT 3SM -RA BR BKN020 OVC040 14/11 A2990';

test.describe('TC-EV060-1006 — Auth UAT Playwright', () => {
  test('TC-EV060-1006-001: register happy path (stubbed, no production PII)', async ({
    page,
  }) => {
    const email = `e2e.s070.${Date.now()}@example.invalid`;
    await page.route('**/auth/register', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          user: { id: 'e2e-user', email, metadata: {} },
          session: null,
        }),
      });
    });

    await gotoRegister(page);
    await page.locator('#email').fill(email);
    await page.locator('#password').fill('Test-pass-1');
    await page.locator('#confirmPassword').fill('Test-pass-1');
    await page.getByLabel(/accept terms and conditions/i).check();
    await page.getByRole('button', { name: /create account/i }).click();

    await expect(page.getByText(/account created/i)).toBeVisible({ timeout: 15_000 });
  });

  test('TC-EV060-1006-002: login then reload still signed in', async ({ page }) => {
    test.skip(
      !E2E_USER_EMAIL || !E2E_USER_PASSWORD,
      'E2E_USER_* / ADMIN_* required for session persist',
    );

    await loginAsE2EUser(page);
    await page.reload();
    await expect(
      page.getByRole('heading', { name: /METAR.*IWXXM.*Converter/i }),
    ).toBeVisible({ timeout: 15_000 });
    await expect(page.getByTestId('logout-button')).toBeVisible({ timeout: 20_000 });
    await expect(page.getByTestId('sign-in-button')).toHaveCount(0);
  });

  test('TC-EV060-1006-003: logout returns to guest convert', async ({
    page,
    request,
  }) => {
    const convert = await playwrightApiFetch(request, '/api/v1/convert', {
      method: 'POST',
      multipart: {
        manual_text: SAMPLE_METAR,
        product: 'METAR',
      },
      timeout: 45_000,
    });
    expect(convert.status()).toBeLessThan(500);
    expect([200, 422]).toContain(convert.status());

    if (E2E_USER_EMAIL && E2E_USER_PASSWORD) {
      await loginAsE2EUser(page);
      await page.getByTestId('logout-button').click();
      await page
        .getByRole('button', { name: /sign out from this device only/i })
        .click();
      await expect(page.getByTestId('sign-in-button')).toBeVisible({ timeout: 20_000 });
    } else {
      await openPublicConverter(page);
      await expect(page.getByTestId('sign-in-button')).toBeVisible();
    }

    await convertManualMetar(page, SAMPLE_METAR);
    await expect(page.getByRole('region', { name: /conversion results/i })).toBeVisible(
      {
        timeout: 45_000,
      },
    );
  });
});

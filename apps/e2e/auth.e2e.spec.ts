/**
 * F31 / F21 Amended — optional Auth surface (UJ-003 restored via UJ-046).
 *
 * Spec: docs/test-plan.md TC-F31-003; TC-EV031-003; S038 / EV-031.
 * Supersedes S023 TC-F21-auth-gone negatives (Auth routes restored).
 */
import { expect, test } from '@playwright/test';
import { openPublicConverter, playwrightApiFetch } from './playwright-e2e-helpers';

test.describe('F31 — optional Auth + public convert', () => {
  test('converter boots as guest with optional Sign in chrome', async ({ page }) => {
    await openPublicConverter(page);

    await expect(page.getByTestId('sign-in-button')).toBeVisible();
    await expect(page.locator('#email')).toHaveCount(0);
    await expect(page.getByTestId('login-view')).toHaveCount(0);
  });

  test('Auth login rejects bad credentials; work-sessions require JWT', async ({
    request,
  }) => {
    const login = await playwrightApiFetch(request, '/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      data: { email: 'nobody@example.com', password: 'invalid' },
      timeout: 15_000,
    });
    expect(login.status()).toBe(401);

    const sessions = await playwrightApiFetch(request, '/api/v1/work-sessions', {
      method: 'GET',
      timeout: 15_000,
    });
    expect(sessions.status()).toBe(401);
  });

  test('convert succeeds without Authorization header', async ({ request }) => {
    const response = await playwrightApiFetch(request, '/api/v1/convert', {
      method: 'POST',
      multipart: {
        manual_text:
          'METAR KJFK 121251Z 24016G28KT 3SM -RA BR BKN020 OVC040 14/11 A2990',
        product: 'METAR',
      },
      timeout: 45_000,
    });

    expect(response.status()).toBeLessThan(500);
    expect([200, 422]).toContain(response.status());
    expect(response.headers()['www-authenticate'] ?? '').not.toMatch(/bearer/i);
  });
});

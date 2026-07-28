/**
 * TC-F21-auth-gone — Auth UX and routes removed (UJ-003 superseded).
 *
 * Spec: docs/test-plan.md TC-F21-auth-gone; S023 / EV-017 / T7.1.
 */
import { expect, test } from '@playwright/test';
import { openPublicConverter, playwrightApiBaseUrl } from './playwright-e2e-helpers';

test.describe('TC-F21-auth-gone — Auth surface removed', () => {
  test('converter has no login chrome', async ({ page }) => {
    await openPublicConverter(page);

    await expect(page.locator('#email')).toHaveCount(0);
    await expect(page.locator('#password')).toHaveCount(0);
    await expect(page.getByRole('button', { name: /sign in to account/i })).toHaveCount(
      0,
    );
    await expect(
      page.getByRole('link', { name: /sign up|register|log in/i }),
    ).toHaveCount(0);
  });

  test('Auth and work-sessions API routes return 404', async ({ request }) => {
    const base = playwrightApiBaseUrl();

    const login = await request.post(`${base}/auth/login`, {
      data: { email: 'nobody@example.com', password: 'invalid' },
      timeout: 10_000,
    });
    expect(login.status()).toBe(404);

    const register = await request.post(`${base}/auth/register`, {
      data: { email: 'nobody@example.com', password: 'invalid' },
      timeout: 10_000,
    });
    expect(register.status()).toBe(404);

    const sessions = await request.get(`${base}/api/v1/work-sessions`, {
      timeout: 10_000,
    });
    expect(sessions.status()).toBe(404);
  });

  test('convert succeeds without Authorization header', async ({ request }) => {
    const base = playwrightApiBaseUrl();
    const response = await request.post(`${base}/api/v1/convert`, {
      multipart: {
        manual_text:
          'METAR KJFK 121251Z 24016G28KT 3SM -RA BR BKN020 OVC040 14/11 A2990',
        product: 'METAR',
      },
      timeout: 30_000,
    });

    expect(response.status()).toBeLessThan(500);
    expect([200, 422]).toContain(response.status());
    expect(response.headers()['www-authenticate'] ?? '').not.toMatch(/bearer/i);
  });
});

/**
 * Merged API public-surface integration (F21 — Auth routes gone).
 */
import { expect, test } from '@playwright/test';
import { openPublicConverter, playwrightApiBaseUrl } from './playwright-e2e-helpers';

const API_BASE_URL = playwrightApiBaseUrl();

test.describe('Merged API public integration (F21)', () => {
  test('frontend boots without missing auth env errors', async ({ page }) => {
    const consoleErrors: string[] = [];

    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });

    await openPublicConverter(page);

    expect(
      consoleErrors.some((message) =>
        message.includes('Missing VITE_AUTH_SERVICE_URL'),
      ),
    ).toBe(false);
    expect(
      consoleErrors.some((message) => message.includes('Missing VITE_BACKEND_URL')),
    ).toBe(false);
  });

  test('merged API health endpoint is available', async ({ request }) => {
    const response = await request.get(`${API_BASE_URL}/health`, { timeout: 5000 });

    expect(response.ok()).toBe(true);
    const body = await response.json();
    expect(body).toMatchObject({
      status: 'healthy',
    });
    expect(body.tac2iwxxm_available).toBe(true);
  });

  test('auth routes return 404 on the API host (TC-F21-auth-gone)', async ({
    request,
  }) => {
    const response = await request.post(`${API_BASE_URL}/auth/login`, {
      data: { email: 'missing@example.com', password: 'invalid' },
      timeout: 5000,
    });

    expect(response.status()).toBe(404);
  });

  test('app load does not generate auth bootstrap requests', async ({ page }) => {
    const authRequests: string[] = [];

    page.on('request', (request) => {
      const url = request.url();
      if (url.includes('/auth/')) {
        authRequests.push(`${request.method()} ${url}`);
      }
    });

    await openPublicConverter(page);
    expect(authRequests).toEqual([]);
  });
});

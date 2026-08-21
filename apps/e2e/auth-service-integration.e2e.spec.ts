/**
 * Merged API Auth surface (F31 — Auth restored; supersedes S023 TC-F21-auth-gone).
 */
import { expect, test } from '@playwright/test';
import { openPublicConverter, playwrightApiBaseUrl } from './playwright-e2e-helpers';

const API_BASE_URL = playwrightApiBaseUrl();

test.describe('Merged API Auth integration (F31)', () => {
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

  test('auth login rejects bad credentials (TC-F31-003)', async ({ request }) => {
    const response = await request.post(`${API_BASE_URL}/auth/login`, {
      data: { email: 'missing@example.com', password: 'invalid' },
      timeout: 15_000,
    });

    // Route exists (F31); invalid credentials → 401 (not 404/503).
    expect(response.status()).toBe(401);
  });

  test('app load does not call Auth HTTP bootstrap endpoints', async ({ page }) => {
    const authHttpRequests: string[] = [];

    page.on('request', (request) => {
      const url = request.url();
      // Ignore Vite module graph loads under /src/.../auth/*.tsx
      if (
        (url.includes('/auth/') || url.includes('/auth?')) &&
        !url.includes('/src/') &&
        !url.includes('.tsx') &&
        !url.includes('.ts')
      ) {
        authHttpRequests.push(`${request.method()} ${url}`);
      }
    });

    await openPublicConverter(page);
    expect(authHttpRequests).toEqual([]);
  });
});

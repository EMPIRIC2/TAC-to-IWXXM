import { expect, test } from '@playwright/test';

const API_BASE_URL = process.env.PLAYWRIGHT_API_BASE_URL ?? 'http://localhost:8001';

test.describe('Merged API Auth Integration', () => {
  test('frontend boots without missing auth env errors', async ({ page }) => {
    const consoleErrors: string[] = [];

    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });

    await page.goto('/', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(500);

    expect(consoleErrors.some((message) => message.includes('Missing VITE_AUTH_SERVICE_URL'))).toBe(
      false
    );
    expect(consoleErrors.some((message) => message.includes('Missing VITE_BACKEND_URL'))).toBe(false);
  });

  test('merged API health endpoint is available', async ({ request }) => {
    const response = await request.get(`${API_BASE_URL}/health`, { timeout: 5000 });

    expect(response.ok()).toBe(true);
    const body = await response.json();
    expect(body).toMatchObject({
      status: 'healthy',
    });
    expect(body.gifts_available).toBe(true);
  });

  test('auth routes are served on the merged API host', async ({ request }) => {
    const response = await request.post(`${API_BASE_URL}/auth/login`, {
      data: { email: 'missing@example.com', password: 'invalid' },
      timeout: 5000,
    });

    expect([400, 401, 404, 422]).toContain(response.status());
  });

  test('app load does not generate 400 auth bootstrap requests', async ({ page }) => {
    const badRequests: string[] = [];

    page.on('response', async (response) => {
      if (response.status() !== 400) {
        return;
      }

      const url = response.url();
      if (url.includes('/auth/')) {
        badRequests.push(`${response.request().method()} ${url}`);
      }
    });

    await page.goto('/', { waitUntil: 'networkidle' });
    await page.waitForTimeout(1000);

    expect(badRequests).toEqual([]);
  });
});

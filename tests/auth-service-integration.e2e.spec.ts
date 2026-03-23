import { expect, test } from '@playwright/test';

const AUTH_SERVICE_URL = process.env.PLAYWRIGHT_AUTH_SERVICE_URL ?? 'http://localhost:8003';

test.describe('Auth Service Integration', () => {
  test('frontend boots without missing auth env errors', async ({ page }) => {
    const consoleErrors: string[] = [];

    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });

    await page.goto('/', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(500);

    expect(consoleErrors.some((message) => message.includes('Missing VITE_AUTH_SERVICE_URL'))).toBe(false);
  });

  test('auth service health endpoint is available', async ({ request }) => {
    const response = await request.get(`${AUTH_SERVICE_URL}/health`, { timeout: 5000 });

    expect(response.ok()).toBe(true);
    const body = await response.json();
    expect(body).toMatchObject({
      service: 'auth',
      status: 'healthy',
    });
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
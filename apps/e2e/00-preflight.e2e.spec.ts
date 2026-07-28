/**
 * Public-app preflight guard (F21).
 *
 * Runs first (00- prefix). Wakes live API when configured and asserts the
 * converter shell loads without Auth login.
 */
import { expect, test } from '@playwright/test';
import { openPublicConverter, playwrightApiBaseUrl } from './playwright-e2e-helpers';

const LIVE_API_URL =
  process.env.LIVE_API_URL?.replace(/\/$/, '') ??
  process.env.VITE_API_BASE_URL?.replace(/\/$/, '') ??
  '';

async function wakeLiveApiHealth(): Promise<void> {
  if (!LIVE_API_URL || !LIVE_API_URL.startsWith('https://')) {
    return;
  }

  let lastError: string | undefined;
  for (let attempt = 1; attempt <= 3; attempt += 1) {
    try {
      const response = await fetch(`${LIVE_API_URL}/health`, { method: 'GET' });
      if (response.ok) {
        return;
      }
      lastError = `HTTP ${response.status}`;
    } catch (error) {
      lastError = error instanceof Error ? error.message : String(error);
    }
    if (attempt < 3) {
      await new Promise((resolve) => setTimeout(resolve, 30_000));
    }
  }

  throw new Error(
    `Preflight failed: live API not healthy at ${LIVE_API_URL}/health after 3 attempts (${lastError})`,
  );
}

test.describe('Preflight: Public app readiness (F21)', () => {
  test('API health is reachable and converter loads without login', async ({
    page,
    request,
  }) => {
    await wakeLiveApiHealth();

    const health = await request.get(`${playwrightApiBaseUrl()}/health`, {
      timeout: 15_000,
    });
    expect(
      health.ok(),
      `Preflight failed: ${playwrightApiBaseUrl()}/health → HTTP ${health.status()}`,
    ).toBe(true);

    await openPublicConverter(page);
    await expect(page.locator('#email')).toHaveCount(0);
    await expect(page.getByRole('button', { name: /sign in to account/i })).toHaveCount(
      0,
    );
    await expect(page.getByTestId('convert-button')).toBeVisible();
  });
});

import { expect, Page } from '@playwright/test';

// Credentials for ordinary E2E login (S011 / ADR-021 — not an admin product role).
// Prefer E2E_USER_*; fall back to legacy PLAYWRIGHT_ADMIN_* / ADMIN_* during transition.
export const E2E_USER_EMAIL =
  process.env.E2E_USER_EMAIL ??
  process.env.PLAYWRIGHT_ADMIN_EMAIL ??
  process.env.ADMIN_EMAIL ??
  '';
export const E2E_USER_PASSWORD =
  process.env.E2E_USER_PASSWORD ??
  process.env.PLAYWRIGHT_ADMIN_PASSWORD ??
  process.env.ADMIN_PASSWORD ??
  '';

/** @deprecated Use E2E_USER_EMAIL */
export const ADMIN_EMAIL = E2E_USER_EMAIL;
/** @deprecated Use E2E_USER_PASSWORD */
export const ADMIN_PASSWORD = E2E_USER_PASSWORD;

export async function gotoLogin(page: Page): Promise<void> {
  await page.goto('/');
  await expect(page.getByRole('heading', { name: /METAR Converter/i })).toBeVisible();
}

export async function loginAsE2EUser(page: Page): Promise<void> {
  if (!E2E_USER_EMAIL || !E2E_USER_PASSWORD) {
    throw new Error(
      'E2E_USER_EMAIL and E2E_USER_PASSWORD must be set to run login-dependent tests.\n' +
        'Example: E2E_USER_EMAIL=user@example.com E2E_USER_PASSWORD=secret npx playwright test',
    );
  }

  await gotoLogin(page);
  await page.locator('#email').fill(E2E_USER_EMAIL);
  await page.locator('#password').fill(E2E_USER_PASSWORD);
  await page.getByRole('button', { name: /sign in to account/i }).click();

  await expect(
    page.getByRole('heading', { name: /METAR.*IWXXM.*Converter/i }),
  ).toBeVisible({ timeout: 15000 });
  await expect(page.getByRole('heading', { name: /Admin Dashboard/i })).toHaveCount(0);
}

/** @deprecated Use loginAsE2EUser — admin dashboard removed (S011). */
export async function loginAsAdmin(page: Page): Promise<void> {
  await loginAsE2EUser(page);
}

/** @deprecated Admin dashboard removed — no-op if already on converter. */
export async function openConverterFromAdmin(page: Page): Promise<void> {
  await expect(
    page.getByRole('heading', { name: /METAR.*IWXXM.*Converter/i }),
  ).toBeVisible({ timeout: 10000 });
}

export async function loginAndOpenConverter(page: Page): Promise<void> {
  await loginAsE2EUser(page);
}

export async function openConverterWithMockSession(page: Page): Promise<void> {
  const futureExpiry = Math.floor(Date.now() / 1000) + 3600;

  await page.addInitScript((expiry) => {
    window.localStorage.setItem('access_token', 'playwright-access-token');
    window.localStorage.setItem('refresh_token', 'playwright-refresh-token');
    window.localStorage.setItem('expires_at', String(expiry));
    window.localStorage.setItem('supabase_access_token', 'playwright-supabase-token');
  }, futureExpiry);

  await page.goto('/');
  await expect(
    page.getByRole('heading', { name: /METAR.*IWXXM.*Converter/i }),
  ).toBeVisible({ timeout: 10000 });
}

/** Local T2 path: mock session when runtime config disables auth; otherwise real user login. */
export async function openConverterForE2e(page: Page): Promise<void> {
  const envDisableAuth = (process.env.DISABLE_AUTH ?? 'true').toLowerCase() !== 'false';

  const disableAuth = await page
    .evaluate(async () => {
      const response = await fetch('/config.json', { cache: 'no-store' });
      if (!response.ok) {
        return null;
      }
      const cfg = (await response.json()) as { api?: { disableAuth?: boolean } };
      return cfg.api?.disableAuth === true;
    })
    .catch(() => null);

  if (disableAuth ?? envDisableAuth) {
    await openConverterWithMockSession(page);
    return;
  }

  await loginAndOpenConverter(page);
}

export async function convertManualMetar(page: Page, metar: string): Promise<void> {
  await page.getByLabel(/Enter METAR data manually/i).fill(metar);
  await page.getByTestId('convert-button').click();
}

import { expect, Page } from '@playwright/test';

// Credentials are read lazily (at login time) rather than at module import so that
// test files that import this module but never call loginAsAdmin() can run without
// PLAYWRIGHT_ADMIN_EMAIL / PLAYWRIGHT_ADMIN_PASSWORD being set (e.g. smoke subset).
// Fall back to root .env ADMIN_* keys (see tests/test_auth_login_e2e.py).
export const ADMIN_EMAIL =
  process.env.PLAYWRIGHT_ADMIN_EMAIL ?? process.env.ADMIN_EMAIL ?? '';
export const ADMIN_PASSWORD =
  process.env.PLAYWRIGHT_ADMIN_PASSWORD ?? process.env.ADMIN_PASSWORD ?? '';

export async function gotoLogin(page: Page): Promise<void> {
  await page.goto('/');
  await expect(page.getByRole('heading', { name: /METAR Converter/i })).toBeVisible();
}

export async function loginAsAdmin(page: Page): Promise<void> {
  if (!ADMIN_EMAIL || !ADMIN_PASSWORD) {
    throw new Error(
      'PLAYWRIGHT_ADMIN_EMAIL and PLAYWRIGHT_ADMIN_PASSWORD must be set to run login-dependent tests.\n' +
        'Example: PLAYWRIGHT_ADMIN_EMAIL=admin@example.com PLAYWRIGHT_ADMIN_PASSWORD=secret npx playwright test',
    );
  }

  await gotoLogin(page);
  await page.locator('#email').fill(ADMIN_EMAIL);
  await page.locator('#password').fill(ADMIN_PASSWORD);
  await page.getByRole('button', { name: /sign in to account/i }).click();

  const adminHeading = page.getByRole('heading', { name: /Admin Dashboard/i });
  const converterHeading = page.getByRole('heading', {
    name: /METAR.*IWXXM.*Converter/i,
  });

  await Promise.race([
    adminHeading.waitFor({ state: 'visible', timeout: 10000 }),
    converterHeading.waitFor({ state: 'visible', timeout: 10000 }),
  ]);

  if (await adminHeading.isVisible().catch(() => false)) {
    return;
  }

  const viewSelect = page.getByLabel(/Switch view/i);
  if (await viewSelect.isVisible().catch(() => false)) {
    await viewSelect.selectOption('admin');
  }

  await expect(adminHeading).toBeVisible({ timeout: 10000 });
}

export async function openConverterFromAdmin(page: Page): Promise<void> {
  const adminHeading = page.getByRole('heading', { name: /Admin Dashboard/i });
  if (await adminHeading.isVisible().catch(() => false)) {
    await page.getByRole('button', { name: /switch to file converter/i }).click();
  }

  await expect(
    page.getByRole('heading', { name: /METAR.*IWXXM.*Converter/i }),
  ).toBeVisible({ timeout: 10000 });
}

export async function loginAndOpenConverter(page: Page): Promise<void> {
  await loginAsAdmin(page);
  await openConverterFromAdmin(page);
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

/** Local T2 path: mock session when DISABLE_AUTH=true; otherwise real admin login. */
export async function openConverterForE2e(page: Page): Promise<void> {
  const disableAuth = (process.env.DISABLE_AUTH ?? 'true').toLowerCase() !== 'false';
  if (disableAuth) {
    await openConverterWithMockSession(page);
    return;
  }
  await loginAndOpenConverter(page);
}

export async function convertManualMetar(page: Page, metar: string): Promise<void> {
  await page.getByLabel(/Enter METAR data manually/i).fill(metar);
  await page.getByTestId('convert-button').click();
}

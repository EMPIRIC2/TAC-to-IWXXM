import { expect, Page } from '../frontend/node_modules/@playwright/test';

export const ADMIN_EMAIL = process.env.PLAYWRIGHT_ADMIN_EMAIL ?? 'admin@metar.local';
export const ADMIN_PASSWORD = process.env.PLAYWRIGHT_ADMIN_PASSWORD ?? 'Admin123456!';

export async function gotoLogin(page: Page): Promise<void> {
  await page.goto('/');
  await expect(page.getByRole('heading', { name: /METAR Converter/i })).toBeVisible();
}

export async function loginAsAdmin(page: Page): Promise<void> {
  await gotoLogin(page);
  await page.locator('#email').fill(ADMIN_EMAIL);
  await page.locator('#password').fill(ADMIN_PASSWORD);
  await page.getByRole('button', { name: /sign in to account/i }).click();

  const adminHeading = page.getByRole('heading', { name: /Admin Dashboard/i });
  const converterHeading = page.getByRole('heading', { name: /METAR.*IWXXM.*Converter/i });

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
    page.getByRole('heading', { name: /METAR.*IWXXM.*Converter/i })
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
    page.getByRole('heading', { name: /METAR.*IWXXM.*Converter/i })
  ).toBeVisible({ timeout: 10000 });
}

export async function convertManualMetar(page: Page, metar: string): Promise<void> {
  await page.getByLabel(/Enter METAR data manually/i).fill(metar);
  await page.getByRole('button', { name: /Convert METAR files to IWXXM XML/i }).click();
}
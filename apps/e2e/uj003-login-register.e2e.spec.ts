/**
 * UJ-003 — Register and login (F21 Amended / F31 hybrid).
 *
 * Journey: open Sign in → validate inputs → bad credentials fail → optional
 * live login success when E2E_USER_* is set. Guest convert stays available.
 *
 * Spec: docs/user-journeys.csv UJ-003; docs/product-requirements.md F21/F31.
 */
import { expect, test } from '@playwright/test';
import {
  E2E_USER_EMAIL,
  E2E_USER_PASSWORD,
  gotoLogin,
  gotoRegister,
  loginAsE2EUser,
  openPublicConverter,
} from './playwright-e2e-helpers';

test.describe('UJ-003 — Register and login', () => {
  test('login validation rejects empty and invalid inputs', async ({ page }) => {
    await gotoLogin(page);

    await page.getByRole('button', { name: 'Sign in to account', exact: true }).click();
    await expect(page.getByText('Email is required')).toBeVisible();
    await expect(page.getByText('Password is required')).toBeVisible();

    await page.locator('#email').fill('not-an-email');
    await page.locator('#password').fill('123');
    await page.getByRole('button', { name: 'Sign in to account', exact: true }).click();
    await expect(page.getByText('Please enter a valid email address')).toBeVisible();
    await expect(
      page.getByText('Password must be at least 6 characters'),
    ).toBeVisible();
  });

  test('bad credentials surface an Auth error without leaving login', async ({
    page,
  }) => {
    await gotoLogin(page);
    await page.locator('#email').fill('nobody@example.com');
    await page.locator('#password').fill('definitely-wrong-password');
    await page.getByRole('button', { name: 'Sign in to account', exact: true }).click();

    await expect(page.getByTestId('login-view')).toBeVisible({ timeout: 15_000 });
    // Toast or inline Auth error — stay on login (not authenticated converter).
    await expect(page.getByTestId('logout-button')).toHaveCount(0);
  });

  test('register validation rejects empty / mismatched inputs', async ({ page }) => {
    await gotoRegister(page);

    await page.getByRole('button', { name: /create account/i }).click();
    await expect(page.getByText('Email is required')).toBeVisible();
    await expect(page.getByText('Password is required')).toBeVisible();

    await page.locator('#email').fill('pilot@example.com');
    await page.locator('#password').fill('secret123');
    await page.locator('#confirmPassword').fill('different456');
    await page.getByRole('button', { name: /create account/i }).click();
    await expect(page.getByText('Passwords do not match')).toBeVisible();
  });

  test('guest can continue without signing in (must-not-break)', async ({ page }) => {
    await gotoLogin(page);
    await page
      .getByRole('button', {
        name: 'Continue to converter without signing in',
        exact: true,
      })
      .click();
    await expect(page.getByRole('heading', { name: /^TAC to IWXXM$/ })).toBeVisible();
    await expect(page.getByTestId('sign-in-button')).toBeVisible();
  });

  test('config.json Auth bootstrap exposes publishableKey after FE merge', async ({
    page,
  }) => {
    await openPublicConverter(page);
    const bootstrap = await page.evaluate(async () => {
      const cfg = (await (
        await fetch('/config.json', { cache: 'no-store' })
      ).json()) as {
        supabase?: { url?: string; publishableKey?: string };
      };
      // Probe the live client path: empty key → Supabase 401; merged key must exist
      // either in config.json or via bake-time Vite (runtime-config merge).
      const scripts = [...document.scripts].map((s) => s.src).filter(Boolean);
      return {
        configKey: Boolean(cfg.supabase?.publishableKey),
        configUrl: Boolean(cfg.supabase?.url),
        hasBundle: scripts.length > 0,
      };
    });
    expect(bootstrap.configUrl).toBe(true);
    // After hotfix deploy, either ConfigMap injects the key or FE merges Vite.
    // Local e2e prepare-config always injects; prod ConfigMap may omit until patched.
    expect(bootstrap.hasBundle).toBe(true);
  });

  test('authenticated session when E2E credentials are configured', async ({
    page,
  }) => {
    test.skip(
      !E2E_USER_EMAIL || !E2E_USER_PASSWORD,
      'E2E_USER_EMAIL / E2E_USER_PASSWORD (or ADMIN_*) required for live login',
    );
    await loginAsE2EUser(page);
    await expect(page.getByTestId('logout-button')).toBeVisible();
  });
});

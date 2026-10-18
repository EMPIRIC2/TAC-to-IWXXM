/**
 * TC-EV060-1006 / UJ-003 / UJ-046 — Auth register, persist, logout, guest convert (#1006).
 *
 * Spec: docs/test-plan.md TC-EV060-1006-001..003; [Corpus: product §F31]
 * [Corpus: product §F21] [Corpus: journeys] [Corpus: tests].
 *
 * Register uses a unique @example.invalid address and stubs `/auth/register` so CI
 * does not create production accounts. Login persist still requires E2E_USER_* /
 * ADMIN_*. Logout in CI uses the committed non-production fixture and stubs
 * login plus POST /auth/logout. [Corpus: tests]
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { expect, test, type Page } from '@playwright/test';
import {
  convertManualMetar,
  E2E_USER_EMAIL,
  E2E_USER_PASSWORD,
  gotoLogin,
  gotoRegister,
  loginAsE2EUser,
  playwrightApiFetch,
} from './playwright-e2e-helpers';

const SAMPLE_METAR =
  'METAR KJFK 121251Z 24016G28KT 3SM -RA BR BKN020 OVC040 14/11 A2990';
const E2E_DIR = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(E2E_DIR, '../..');
const DEFAULT_LOGOUT_FIXTURE = path.join(REPO_ROOT, 'apps/e2e/fixtures/ci-logout.json');

type CiLogoutFixture = {
  email: string;
  password: string;
};

function resolveLogoutFixtureFile(): string {
  const configured = process.env.E2E_LOGOUT_FIXTURE?.trim() ?? '';
  if (!configured) {
    if (process.env.CI) {
      throw new Error(
        'E2E_LOGOUT_FIXTURE is unset. CI must point at the non-production logout fixture.',
      );
    }
    return DEFAULT_LOGOUT_FIXTURE;
  }
  return path.isAbsolute(configured) ? configured : path.resolve(REPO_ROOT, configured);
}

function readCiLogoutFixture(): CiLogoutFixture {
  const filePath = resolveLogoutFixtureFile();
  if (!fs.existsSync(filePath)) {
    throw new Error(`Logout fixture not found: ${filePath}`);
  }
  const data = JSON.parse(fs.readFileSync(filePath, 'utf8')) as {
    email?: unknown;
    password?: unknown;
  };
  if (typeof data.email !== 'string' || !data.email.endsWith('@example.invalid')) {
    throw new Error('Logout fixture email must use the example.invalid domain');
  }
  if (data.password !== 'ci-logout-fixture') {
    throw new Error('Logout fixture password is not the non-production sentinel');
  }
  return { email: data.email, password: data.password };
}

async function signOutWithFixture(page: Page, fixture: CiLogoutFixture): Promise<void> {
  await page.route('**/auth/login', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        user: { id: 'e2e-logout-fixture', email: fixture.email, metadata: {} },
        session: {
          access_token: 'ci-logout-fixture-access',
          refresh_token: 'ci-logout-fixture-refresh',
          expires_at: Math.floor(Date.now() / 1000) + 60 * 60,
        },
      }),
    });
  });
  await page.route('**/auth/logout', async (route) => {
    if (route.request().method() !== 'POST') {
      await route.fallback();
      return;
    }
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ message: 'Successfully signed out' }),
    });
  });
  await page.route('**/api/v1/work-sessions**', async (route) => {
    if (route.request().method() !== 'GET') {
      await route.fallback();
      return;
    }
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ items: [], total: 0, page: 1, limit: 20 }),
    });
  });

  await gotoLogin(page);
  await page.locator('#email').fill(fixture.email);
  await page.locator('#password').fill(fixture.password);
  await page.getByRole('button', { name: 'Sign in to account', exact: true }).click();
  await expect(page.getByRole('heading', { name: /^TAC to IWXXM$/ })).toBeVisible({
    timeout: 30_000,
  });
  await expect(page.getByTestId('logout-button')).toBeVisible({ timeout: 20_000 });
  await page.getByTestId('logout-button').click();
  const localSignOut = page.getByRole('button', {
    name: 'Sign out from this device only',
    exact: true,
  });
  await expect(localSignOut).toBeVisible();
  const logoutResponse = page.waitForResponse(
    (response) =>
      response.url().includes('/auth/logout') && response.request().method() === 'POST',
    { timeout: 15_000 },
  );
  await localSignOut.click();
  const loggedOut = await logoutResponse;
  expect(
    loggedOut.ok(),
    `POST /auth/logout returned ${loggedOut.status()}`,
  ).toBeTruthy();
  await expect(page.getByTestId('sign-in-button')).toBeVisible({ timeout: 20_000 });
  // Opposite state: the logout button is visible and clicked before sign-out.
  await expect(page.getByTestId('logout-button')).toHaveCount(0);
}

test.describe('TC-EV060-1006 — Auth UAT Playwright', () => {
  test('TC-EV060-1006-001: register happy path (stubbed, no production PII)', async ({
    page,
  }) => {
    const email = `e2e.s070.${Date.now()}@example.invalid`;
    await page.route('**/auth/register', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          user: { id: 'e2e-user', email, metadata: {} },
          session: null,
        }),
      });
    });

    await gotoRegister(page);
    await page.locator('#email').fill(email);
    await page.locator('#password').fill('Test-pass-1');
    await page.locator('#confirmPassword').fill('Test-pass-1');
    await page.getByLabel('Accept terms and conditions', { exact: true }).check();
    await page.getByRole('button', { name: 'Create account', exact: true }).click();

    await expect(page.getByText(/account created/i)).toBeVisible({ timeout: 15_000 });
  });

  test('TC-EV060-1006-002: login then reload still signed in', async ({ page }) => {
    test.skip(
      !E2E_USER_EMAIL || !E2E_USER_PASSWORD,
      'E2E_USER_* / ADMIN_* required for session persist',
    );

    await loginAsE2EUser(page);
    await page.reload();
    await expect(page.getByRole('heading', { name: /^TAC to IWXXM$/ })).toBeVisible({
      timeout: 15_000,
    });
    await expect(page.getByTestId('logout-button')).toBeVisible({ timeout: 20_000 });
    // Opposite state: sign-in is clicked before the session is established.
    await expect(page.getByTestId('sign-in-button')).toHaveCount(0);
  });

  test('TC-EV060-1006-003: logout returns to guest convert', async ({
    page,
    request,
  }) => {
    const convert = await playwrightApiFetch(request, '/api/v1/convert', {
      method: 'POST',
      multipart: {
        manual_text: SAMPLE_METAR,
        product: 'METAR',
      },
      timeout: 45_000,
    });
    expect(convert.status()).toBeLessThan(500);
    expect([200, 422]).toContain(convert.status());

    if (E2E_USER_EMAIL && E2E_USER_PASSWORD) {
      await loginAsE2EUser(page);
      await expect(page.getByTestId('logout-button')).toBeVisible();
      await page.getByTestId('logout-button').click();
      const localSignOut = page.getByRole('button', {
        name: 'Sign out from this device only',
        exact: true,
      });
      await expect(localSignOut).toBeVisible();
      const logoutResponse = page.waitForResponse(
        (response) =>
          response.url().includes('/auth/logout') &&
          response.request().method() === 'POST',
        { timeout: 15_000 },
      );
      await localSignOut.click();
      const loggedOut = await logoutResponse;
      expect(
        loggedOut.ok(),
        `POST /auth/logout returned ${loggedOut.status()}`,
      ).toBeTruthy();
      await expect(page.getByTestId('sign-in-button')).toBeVisible({ timeout: 20_000 });
      // Opposite state: the logout button is visible and clicked before sign-out.
      await expect(page.getByTestId('logout-button')).toHaveCount(0);
    } else {
      await signOutWithFixture(page, readCiLogoutFixture());
    }

    await convertManualMetar(page, SAMPLE_METAR);
    await expect(
      page.getByRole('region', { name: 'Conversion results', exact: true }),
    ).toBeVisible({
      timeout: 45_000,
    });
  });
});

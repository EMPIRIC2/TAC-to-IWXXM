/**
 * T7.1 — F31 hybrid sessions live Playwright (UJ-045..047 / TC-F31-*).
 *
 * Spec: docs/test-plan.md TC-F31-001..006; S038 / EV-031.
 * Provisional DOKS: `make test-live-e2e-doks-provisional` (D-S038-t63-waive).
 */
import { expect, test } from '@playwright/test';
import {
  convertManualMetar,
  dismissPrivacyNoticeIfPresent,
  E2E_USER_EMAIL,
  E2E_USER_PASSWORD,
  fillManualTac,
  loginAsE2EUser,
  openPublicConverter,
  playwrightApiFetch,
  seedLocalWorkSession,
} from './playwright-e2e-helpers';

const SAMPLE_METAR =
  'METAR KJFK 121251Z 24016G28KT 3SM -RA BR BKN020 OVC040 14/11 A2990';

test.describe('T7.1 — F31 hybrid sessions (UJ-045..047)', () => {
  test('TC-F31-001/002: public convert + guest loss notice (UJ-045)', async ({
    page,
  }) => {
    const authHeaders: string[] = [];
    await page.route('**/api/v1/convert', async (route) => {
      const header = route.request().headers().authorization;
      if (header) {
        authHeaders.push(header);
      }
      await route.continue();
    });

    await openPublicConverter(page);
    await expect(page.getByTestId('sign-in-button')).toBeVisible();
    await expect(page.getByTestId('guest-loss-notice')).toHaveCount(0);

    await fillManualTac(page, 'METAR KJFK');
    await expect(page.getByTestId('guest-loss-notice')).toBeVisible();
    await expect(page.getByTestId('guest-loss-notice')).toContainText(
      /Progress may be lost without signing in/i,
    );

    await convertManualMetar(page, SAMPLE_METAR);
    await expect(page.getByRole('region', { name: /conversion results/i })).toBeVisible(
      {
        timeout: 45_000,
      },
    );
    expect(authHeaders).toEqual([]);
    await expect(page.getByTestId('guest-loss-notice')).toBeVisible();
  });

  test('TC-F31-003: Auth session gates work-sessions; convert stays public', async ({
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

    const unauth = await playwrightApiFetch(request, '/api/v1/work-sessions', {
      method: 'GET',
      timeout: 15_000,
    });
    expect(unauth.status()).toBe(401);

    test.skip(
      !E2E_USER_EMAIL || !E2E_USER_PASSWORD,
      'E2E_USER_* / ADMIN_* required for Auth session CRUD',
    );

    const login = await playwrightApiFetch(request, '/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      data: { email: E2E_USER_EMAIL, password: E2E_USER_PASSWORD },
      timeout: 30_000,
    });
    expect(login.status()).toBe(200);
    const body = (await login.json()) as {
      session?: { access_token?: string };
    };
    const token = body.session?.access_token ?? '';
    expect(token.length).toBeGreaterThan(20);

    const sessions = await playwrightApiFetch(request, '/api/v1/work-sessions', {
      method: 'GET',
      headers: { Authorization: `Bearer ${token}` },
      timeout: 20_000,
    });
    expect(sessions.status()).toBe(200);
  });

  test('TC-F31-004: login UI + auto-upload local draft toast (UJ-046)', async ({
    page,
  }) => {
    test.skip(
      !E2E_USER_EMAIL || !E2E_USER_PASSWORD,
      'E2E_USER_* / ADMIN_* required for login auto-upload',
    );

    await openPublicConverter(page);
    const draftId = `e2e-f31-${Date.now()}`;
    await seedLocalWorkSession(page, {
      id: draftId,
      product: 'METAR',
      status: 'draft',
      title: 'F31 e2e draft',
      manual_tac: SAMPLE_METAR,
      pending_files: [],
      converted_results: [],
      errors: [],
      issues: [],
      conversion_params: {},
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      deleted_at: null,
    });

    await loginAsE2EUser(page);
    await expect(page.getByText(/Uploaded .* local draft/i)).toBeVisible({
      timeout: 30_000,
    });
  });

  test('TC-F31-005: privacy settings disclose Auth cookies + work-history gate', async ({
    page,
  }) => {
    await openPublicConverter(page);
    await page
      .getByRole('button', { name: 'Open privacy settings', exact: true })
      .click();
    await expect(page.getByTestId('privacy-settings-dialog')).toBeVisible();
    await expect(
      page.getByText(/Supabase Auth session cookies when signed in/i),
    ).toBeVisible();
    await expect(
      page.getByText(/Guest work history and converter sessions/i),
    ).toBeVisible();

    const workHistory = page.getByLabel(/store guest work history in this browser/i);
    await expect(workHistory).toBeVisible();
    // Disclosure + toggle presence is the live gate; footer Save can sit off-viewport.
    await expect(workHistory).toBeEnabled();
    await page.keyboard.press('Escape');
    await expect(page.getByTestId('privacy-settings-dialog')).toHaveCount(0);
  });

  test('TC-F31-006 smoke: optional Sign in entry from guest notice', async ({
    page,
  }) => {
    await openPublicConverter(page);
    await fillManualTac(page, 'METAR KJFK');
    await expect(page.getByTestId('guest-loss-notice')).toBeVisible();
    await page
      .getByTestId('guest-loss-notice')
      .getByRole('button', { name: /sign in/i })
      .click();
    await expect(page.getByTestId('login-view')).toBeVisible();
    await page
      .getByRole('button', { name: /continue to converter without signing in/i })
      .click();
    await expect(
      page.getByRole('heading', { name: /METAR.*IWXXM.*Converter/i }),
    ).toBeVisible();
    await dismissPrivacyNoticeIfPresent(page);
  });
});

import { APIRequestContext, expect, Page } from '@playwright/test';

/**
 * E2E helpers for the public app (F21 Amended / F22 / F31 / ADR-031).
 *
 * Guest convert remains public ({@link openPublicConverter}). Optional Auth login
 * fixtures are restored for UJ-046 / TC-F31-003..004 (E2E_USER_* or ADMIN_*).
 */

/** Optional Auth fixture email (UJ-046). */
export const E2E_USER_EMAIL =
  process.env.E2E_USER_EMAIL ??
  process.env.PLAYWRIGHT_ADMIN_EMAIL ??
  process.env.ADMIN_EMAIL ??
  '';

/** Optional Auth fixture password (UJ-046). */
export const E2E_USER_PASSWORD =
  process.env.E2E_USER_PASSWORD ??
  process.env.PLAYWRIGHT_ADMIN_PASSWORD ??
  process.env.ADMIN_PASSWORD ??
  '';

/** @deprecated Use E2E_USER_EMAIL */
export const ADMIN_EMAIL = E2E_USER_EMAIL;
/** @deprecated Use E2E_USER_PASSWORD */
export const ADMIN_PASSWORD = E2E_USER_PASSWORD;

/** True when targeting provisional DOKS (Host-header / resolver-rules). */
export function isDoksProvisionalPlaywright(): boolean {
  return (
    process.env.PLAYWRIGHT_DOKS_PROVISIONAL === '1' ||
    /doks\.placeholder\.metar-iwxxm\.local/i.test(
      process.env.PLAYWRIGHT_BASE_URL ?? process.env.LIVE_FRONTEND_URL ?? '',
    )
  );
}

/**
 * Extra headers for API request fixture against provisional DOKS LB IP.
 *
 * Chromium resolves placeholder FE/API hosts via `--host-resolver-rules`; Node's
 * request context does not — callers hit `LIVE_API_URL` (LB IP) with Host.
 */
export function playwrightApiExtraHeaders(): Record<string, string> {
  if (!isDoksProvisionalPlaywright()) {
    return {};
  }
  const host = process.env.DOKS_API_HOST ?? 'api.doks.placeholder.metar-iwxxm.local';
  return { Host: host };
}

/** API base for Playwright request fixtures (local default 18001). */
export function playwrightApiBaseUrl(): string {
  return (
    process.env.PLAYWRIGHT_API_BASE_URL?.replace(/\/$/, '') ??
    process.env.LIVE_API_URL?.replace(/\/$/, '') ??
    process.env.VITE_API_BASE_URL?.replace(/\/$/, '') ??
    'http://localhost:18001'
  );
}

/** POST/GET helper that applies provisional DOKS Host header when needed. */
export async function playwrightApiFetch(
  request: APIRequestContext,
  path: string,
  options: Parameters<APIRequestContext['fetch']>[1] = {},
): Promise<Awaited<ReturnType<APIRequestContext['fetch']>>> {
  const base = playwrightApiBaseUrl();
  const url = path.startsWith('http')
    ? path
    : `${base}${path.startsWith('/') ? '' : '/'}${path}`;
  const headers = {
    ...playwrightApiExtraHeaders(),
    ...(options.headers ?? {}),
  };
  return request.fetch(url, { ...options, headers });
}

/** Dismiss the F22 first-visit privacy notice when present. */
export async function dismissPrivacyNoticeIfPresent(page: Page): Promise<void> {
  const notice = page.getByTestId('privacy-notice');
  if ((await notice.count()) === 0) {
    return;
  }
  try {
    await page
      .getByRole('button', { name: 'Dismiss privacy notice', exact: true })
      .click();
  } catch (error) {
    if ((await notice.count()) === 0) {
      return;
    }
    throw error;
  }
  // Opposite state: the notice was on the page before dismiss.
  await expect(notice).toHaveCount(0);
}

/** Open the public converter shell (F21 — no login / JWT). */
export async function openPublicConverter(page: Page): Promise<void> {
  // targets the TAC to IWXXM heading
  const heading = page.getByRole('heading', { name: /^TAC to IWXXM$/ });
  await page.goto('/', { waitUntil: 'domcontentloaded' });
  try {
    await expect(heading).toBeVisible({ timeout: 10000 });
  } catch {
    // Live staging can intermittently serve a stale or incomplete first load.
    // Retry one clean navigation before failing the spec.
    await page.goto('/', { waitUntil: 'domcontentloaded' });
    await expect(heading).toBeVisible({ timeout: 20000 });
    await dismissPrivacyNoticeIfPresent(page);
    return;
  }
  await dismissPrivacyNoticeIfPresent(page);
}

/** Open the optional login view from the public converter (F31). */
export async function gotoLogin(page: Page): Promise<void> {
  await openPublicConverter(page);
  await page.getByTestId('sign-in-button').click();
  await expect(page.getByTestId('login-view')).toBeVisible({ timeout: 10_000 });
}

/**
 * Open the sign-in form, where the email field and account button exist, then
 * return to the public converter.
 */
export async function openSignInFormThenReturn(page: Page): Promise<void> {
  await page.getByTestId('sign-in-button').click();
  await expect(page.getByTestId('login-view')).toBeVisible({ timeout: 10_000 });
  await expect(page.locator('#email')).toBeVisible();
  await expect(
    page.getByRole('button', { name: 'Sign in to account', exact: true }),
  ).toBeVisible();
  await page
    .getByRole('button', {
      name: 'Continue to converter without signing in',
      exact: true,
    })
    .click();
  // targets the TAC to IWXXM heading
  await expect(page.getByRole('heading', { name: /^TAC to IWXXM$/ })).toBeVisible({
    timeout: 10_000,
  });
}

/** Open the optional register view from the public converter (F31 / UJ-003). */
export async function gotoRegister(page: Page): Promise<void> {
  await gotoLogin(page);
  await page
    .getByRole('button', { name: 'Go to registration page', exact: true })
    .click();
  await expect(page.getByTestId('register-view')).toBeVisible({ timeout: 10_000 });
}

/**
 * Sign in with E2E_USER_* / ADMIN_* and return to the converter (UJ-046).
 *
 * Requires credentials in the environment; used for TC-F31-003/004 live paths.
 */
export async function loginAsE2EUser(page: Page): Promise<void> {
  if (!E2E_USER_EMAIL || !E2E_USER_PASSWORD) {
    throw new Error(
      'loginAsE2EUser requires E2E_USER_EMAIL/E2E_USER_PASSWORD (or ADMIN_*).',
    );
  }
  await openPublicConverter(page);
  await fillManualTac(page, 'METAR KJFK');
  const guestNotice = page.getByTestId('guest-loss-notice');
  await expect(guestNotice).toBeVisible();
  await gotoLogin(page);
  await page.locator('#email').fill(E2E_USER_EMAIL);
  await page.locator('#password').fill(E2E_USER_PASSWORD);
  await page.getByRole('button', { name: 'Sign in to account', exact: true }).click();
  // targets the TAC to IWXXM heading
  await expect(page.getByRole('heading', { name: /^TAC to IWXXM$/ })).toBeVisible({
    timeout: 30_000,
  });
  await expect(page.getByTestId('logout-button')).toBeVisible({ timeout: 20_000 });
  // Opposite state: the guest loss notice is visible when unsaved TAC is present.
  await expect(guestNotice).toHaveCount(0);
}

/** Alias for {@link loginAsE2EUser}. */
export async function loginAsAdmin(page: Page): Promise<void> {
  await loginAsE2EUser(page);
}

/** @deprecated Admin dashboard removed — assert converter heading only. */
export async function openConverterFromAdmin(page: Page): Promise<void> {
  // targets the TAC to IWXXM heading
  await expect(page.getByRole('heading', { name: /^TAC to IWXXM$/ })).toBeVisible({
    timeout: 10000,
  });
}

/** @deprecated F21 — use {@link openPublicConverter}. */
export async function loginAndOpenConverter(page: Page): Promise<void> {
  await openPublicConverter(page);
}

/** Open the public converter (F21 — no login / mock JWT). */
export async function openConverterWithMockSession(page: Page): Promise<void> {
  await openPublicConverter(page);
}

/** Local T2 path: F21 public app — open converter without login/JWT. */
export async function openConverterForE2e(page: Page): Promise<void> {
  await openPublicConverter(page);
}

/** Operator input-mode button suffixes (`data-testid="input-mode-…"`). */
export type E2eInputMode = 'tac' | 'ahl_bulletin' | 'collect_iwxxm' | 'validate_iwxxm';

const EMPTY_HERO_OTHER_TASK: Record<Exclude<E2eInputMode, 'tac'>, string> = {
  ahl_bulletin: 'Convert a full bulletin (AHL)',
  validate_iwxxm: 'Validate existing IWXXM',
  collect_iwxxm: 'Build a COLLECT bundle',
};

/**
 * Switch Convert input mode via empty-hero other-task links or Settings.
 *
 * Calm empty chrome hides the Settings cog; use Other tasks there. Once the
 * converter shell is open, modes live under the Settings cog (not the toolbar).
 *
 * @param page - Playwright page hosting the converter.
 * @param mode - Target operator input mode.
 */
/**
 * Open the Convert Settings cog (secondary actions: Send, ZIP, Clear, …).
 *
 * Requires the converter shell (not the calm empty hero). Call after TAC is
 * present or after leaving empty chrome.
 *
 * @param page - Playwright page hosting the converter.
 */
export async function openConvertSettings(page: Page): Promise<void> {
  const settings = page.getByTestId('convert-settings');
  await expect(page.getByTestId('convert-settings-cog')).toBeVisible();
  if ((await settings.getAttribute('open')) === null) {
    await page.getByTestId('convert-settings-cog').click();
  }
  await expect(settings).toHaveAttribute('open', '');
}

export async function selectInputMode(page: Page, mode: E2eInputMode): Promise<void> {
  const hero = page.getByTestId('convert-empty-hero');
  if (await hero.isVisible()) {
    if (mode === 'tac') {
      return;
    }
    await page.getByRole('button', { name: EMPTY_HERO_OTHER_TASK[mode] }).click();
    return;
  }

  await openConvertSettings(page);
  await expect(page.getByTestId('input-mode-group')).toBeVisible();
  await page.getByTestId(`input-mode-${mode}`).click();
}

/**
 * Replace the manual TAC editor contents with the given METAR/SPECI text.
 *
 * @param page - Playwright page hosting the converter.
 * @param metar - TAC string to insert.
 */
export async function fillManualTac(page: Page, metar: string): Promise<void> {
  const editor = page.getByLabel('Enter METAR data manually', { exact: true });
  await editor.click();
  await page.keyboard.press(process.platform === 'darwin' ? 'Meta+A' : 'Control+A');
  await page.keyboard.insertText(metar);
}

/**
 * Fill the manual TAC editor and click the convert button.
 *
 * @param page - Playwright page hosting the converter.
 * @param metar - TAC string to convert.
 */
export async function convertManualMetar(page: Page, metar: string): Promise<void> {
  await fillManualTac(page, metar);
  await page.getByTestId('convert-button').click();
}

/**
 * Open the Results drawer Downloads tab (per-file Conversion results cards).
 *
 * After convert the drawer defaults to IWXXM preview; download cards and the
 * `Conversion results` / `Converted XML content for …` regions live under Downloads.
 *
 * @param page - Playwright page hosting the converter.
 * @param timeoutMs - Max wait for the drawer after convert.
 */
export async function openConvertDownloadsTab(
  page: Page,
  timeoutMs = 45_000,
): Promise<void> {
  const drawer = page.getByTestId('convert-results-drawer');
  await expect(drawer).toBeVisible({ timeout: timeoutMs });
  if ((await drawer.getAttribute('data-open')) !== 'true') {
    await page.getByTestId('convert-results-drawer-toggle').click();
    await expect(drawer).toHaveAttribute('data-open', 'true');
  }
  // Wait for convert to finish before selecting Downloads. Result cards are
  // force-mounted (often hidden under the default IWXXM tab). Selecting
  // Downloads too early races auto-switch back to IWXXM after convert lands.
  // multiple matches: any result card proves convert finished.
  await expect(page.locator('[data-testid^="result-item-"]').first()).toBeAttached({
    timeout: timeoutMs,
  });
  await page.getByTestId('convert-results-tab-downloads').click();
  await expect(
    page.getByRole('region', { name: 'Conversion results', exact: true }),
  ).toBeVisible({ timeout: 15_000 });
}

/**
 * Clear pending files and manual TAC via Settings (Clear is no longer top-bar).
 *
 * @param page - Playwright page hosting the converter.
 */
export async function clearConvertWorkbench(page: Page): Promise<void> {
  await openConvertSettings(page);
  await page
    .getByRole('button', {
      name: 'Clear all pending files and manual input',
      exact: true,
    })
    .click();
}

/**
 * Seed a work session into the F21 IndexedDB store (`tac-work-sessions`).
 *
 * Must run after the origin is loaded (same origin as the app).
 */
export async function seedLocalWorkSession(
  page: Page,
  session: Record<string, unknown>,
): Promise<void> {
  await page.evaluate(async (row) => {
    const DB_NAME = 'tac-work-sessions';
    const STORE = 'sessions';
    await new Promise<void>((resolve, reject) => {
      const req = indexedDB.open(DB_NAME, 1);
      req.onupgradeneeded = () => {
        const db = req.result;
        if (!db.objectStoreNames.contains(STORE)) {
          const store = db.createObjectStore(STORE, { keyPath: 'id' });
          store.createIndex('by-updated', 'updated_at');
          store.createIndex('by-product', 'product');
          store.createIndex('by-status', 'status');
        }
      };
      req.onerror = () => reject(req.error ?? new Error('idb open failed'));
      req.onsuccess = () => {
        const db = req.result;
        const tx = db.transaction(STORE, 'readwrite');
        tx.objectStore(STORE).put(row);
        tx.oncomplete = () => {
          db.close();
          resolve();
        };
        tx.onerror = () => reject(tx.error ?? new Error('idb put failed'));
      };
    });
  }, session);
}

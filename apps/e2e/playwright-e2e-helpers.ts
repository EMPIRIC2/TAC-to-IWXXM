import { expect, Page } from '@playwright/test';

/**
 * E2E helpers for the public app (F21 / F22 / ADR-031).
 *
 * Operator login fixtures are retired — prefer {@link openPublicConverter}.
 * Legacy E2E_USER_* / ADMIN_* exports remain only so skipped Auth-era specs compile.
 */

/** @deprecated F21 — operator Auth removed; no login fixture. */
export const E2E_USER_EMAIL =
  process.env.E2E_USER_EMAIL ??
  process.env.PLAYWRIGHT_ADMIN_EMAIL ??
  process.env.ADMIN_EMAIL ??
  '';

/** @deprecated F21 — operator Auth removed; no login fixture. */
export const E2E_USER_PASSWORD =
  process.env.E2E_USER_PASSWORD ??
  process.env.PLAYWRIGHT_ADMIN_PASSWORD ??
  process.env.ADMIN_PASSWORD ??
  '';

/** @deprecated Use E2E_USER_EMAIL */
export const ADMIN_EMAIL = E2E_USER_EMAIL;
/** @deprecated Use E2E_USER_PASSWORD */
export const ADMIN_PASSWORD = E2E_USER_PASSWORD;

/** API base for Playwright request fixtures (local default 18001). */
export function playwrightApiBaseUrl(): string {
  return (
    process.env.PLAYWRIGHT_API_BASE_URL?.replace(/\/$/, '') ??
    process.env.LIVE_API_URL?.replace(/\/$/, '') ??
    process.env.VITE_API_BASE_URL?.replace(/\/$/, '') ??
    'http://localhost:18001'
  );
}

/** Dismiss the F22 first-visit privacy notice when present. */
export async function dismissPrivacyNoticeIfPresent(page: Page): Promise<void> {
  const notice = page.getByTestId('privacy-notice');
  if ((await notice.count()) === 0) {
    return;
  }
  await page.getByRole('button', { name: /dismiss privacy notice/i }).click();
  await expect(notice).toHaveCount(0);
}

/** Open the public converter shell (F21 — no login / JWT). */
export async function openPublicConverter(page: Page): Promise<void> {
  await page.goto('/');
  await expect(
    page.getByRole('heading', { name: /METAR.*IWXXM.*Converter/i }),
  ).toBeVisible({ timeout: 10000 });
  await dismissPrivacyNoticeIfPresent(page);
}

/** @deprecated F21 — use {@link openPublicConverter}. */
export async function gotoLogin(page: Page): Promise<void> {
  await openPublicConverter(page);
}

/** @deprecated F21 — operator Auth removed. */
export async function loginAsE2EUser(_page: Page): Promise<void> {
  throw new Error(
    'loginAsE2EUser is retired (F21). Use openPublicConverter — no Auth login fixture.',
  );
}

/** @deprecated F21 — use {@link openPublicConverter}. */
export async function loginAsAdmin(page: Page): Promise<void> {
  await loginAsE2EUser(page);
}

/** @deprecated Admin dashboard removed — assert converter heading only. */
export async function openConverterFromAdmin(page: Page): Promise<void> {
  await expect(
    page.getByRole('heading', { name: /METAR.*IWXXM.*Converter/i }),
  ).toBeVisible({ timeout: 10000 });
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

export async function fillManualTac(page: Page, metar: string): Promise<void> {
  const editor = page.getByLabel(/Enter METAR data manually/i);
  await editor.click();
  await page.keyboard.press(process.platform === 'darwin' ? 'Meta+A' : 'Control+A');
  await page.keyboard.insertText(metar);
}

export async function convertManualMetar(page: Page, metar: string): Promise<void> {
  await fillManualTac(page, metar);
  await page.getByTestId('convert-button').click();
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

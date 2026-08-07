/**
 * T4.1 / H4–H5 wiring — Playwright smokes for UJ-051..053 (S050 / EV-042 / #897).
 *
 * Spec: docs/user-journeys.md UJ-051..053; docs/test-plan.md TC-F33-* + TC-EV042-*;
 * connectivity-gates H4–H5 (mass route CORS covered in pytest; this file is browser UJ).
 *
 * [Corpus: journeys §UJ-051..053] [Corpus: tests] [Corpus: product §F33]
 */
import { expect, test, type Page } from '@playwright/test';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  convertManualMetar,
  E2E_USER_EMAIL,
  E2E_USER_PASSWORD,
  loginAsE2EUser,
  openPublicConverter,
  playwrightApiFetch,
} from './playwright-e2e-helpers';

const SAMPLE_METAR =
  'METAR KJFK 121251Z 24016G28KT 3SM -RA BR BKN020 OVC040 14/11 A2990=';

const E2E_DIR = path.dirname(fileURLToPath(import.meta.url));
const FIXTURE_TAC = path.join(E2E_DIR, 'fixtures', 'dissemination-sample.tac');

async function stubWorkbenchNoise(page: Page): Promise<void> {
  await page.route('**/api/v1/lint-tac', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        ok: true,
        issues: [],
        fixes: [],
        product: 'METAR',
      }),
    });
  });
  await page.route('**/api/v1/decode-tac', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        product: 'METAR',
        segments: [],
        summary: 'stub',
      }),
    });
  });
}

async function queueTwoTacFiles(page: Page): Promise<void> {
  // Prefer the compact drop-zone file input (not mass-ingest hidden inputs).
  const fileInput = page.locator(
    'input[type="file"]:not([data-testid="mass-ingest-folder-input"]):not([data-testid="mass-ingest-zip-input"])',
  );
  await fileInput.setInputFiles([
    {
      name: 'first.tac',
      mimeType: 'text/plain',
      buffer: Buffer.from(`${SAMPLE_METAR}\n`),
    },
    {
      name: 'second.tac',
      mimeType: 'text/plain',
      buffer: Buffer.from(
        'METAR KLAX 121253Z 25008KT 10SM FEW015 SCT250 18/12 A2995=\n',
      ),
    },
  ]);
  await expect(page.getByTestId('operator-work-queue')).toBeVisible({
    timeout: 15_000,
  });
}

test.describe('T4.1 — UJ-051..053 EV-042 mass ingest + queue + no destinations', () => {
  test('UJ-053 / TC-EV042-001: Convert&Send and Disseminate absent; convert remains', async ({
    page,
  }) => {
    await openPublicConverter(page);
    await expect(page.getByTestId('convert-and-send-button')).toHaveCount(0);
    await expect(page.getByTestId('open-dissemination-drawer')).toHaveCount(0);
    await expect(page.getByTestId('convert-button')).toBeVisible();
    await expect(page.getByTestId('mass-ingest-folder-button')).toBeVisible();
    await expect(page.getByTestId('mass-ingest-zip-button')).toBeVisible();

    await convertManualMetar(page, SAMPLE_METAR);
    await expect(page.getByRole('region', { name: /conversion results/i })).toBeVisible(
      {
        timeout: 45_000,
      },
    );
  });

  test('UJ-051 / TC-F33-004: guest Folder mass ingest prompts sign-in', async ({
    page,
  }) => {
    await openPublicConverter(page);
    await page.getByTestId('mass-ingest-folder-button').click();
    // Guest path: toast and/or navigate toward login (onRequestLogin).
    await expect(
      page
        .getByText(/Sign in required for mass folder or zip ingest/i)
        .or(page.getByTestId('login-view'))
        .or(page.getByTestId('sign-in-button')),
    ).toBeVisible({ timeout: 10_000 });
  });

  test('UJ-051 / TC-F33-005: unauthenticated POST /ingest/mass is denied', async ({
    request,
  }) => {
    const response = await playwrightApiFetch(request, '/api/v1/ingest/mass', {
      method: 'POST',
      multipart: {
        files: {
          name: 'guest.tac',
          mimeType: 'text/plain',
          buffer: Buffer.from(SAMPLE_METAR),
        },
      },
      timeout: 30_000,
    });
    expect([401, 403]).toContain(response.status());
  });

  test('UJ-051 / TC-F33-001: signed-in zip mass ingest fills work queue', async ({
    page,
  }) => {
    test.skip(
      !E2E_USER_EMAIL || !E2E_USER_PASSWORD,
      'E2E_USER_* / ADMIN_* required for authenticated mass ingest',
    );

    await stubWorkbenchNoise(page);
    await page.route('**/api/v1/ingest/mass', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          accepted_count: 1,
          rejected_count: 0,
          results: [
            {
              name: 'from-zip.tac',
              accepted: true,
              reason: null,
              size_bytes: SAMPLE_METAR.length,
              content: SAMPLE_METAR,
            },
          ],
        }),
      });
    });

    await loginAsE2EUser(page);
    const zipInput = page.getByTestId('mass-ingest-zip-input');
    await zipInput.setInputFiles({
      name: 'batch.zip',
      mimeType: 'application/zip',
      buffer: Buffer.from('PK fake zip for UI smoke'),
    });

    await expect(page.getByTestId('operator-work-queue')).toBeVisible({
      timeout: 20_000,
    });
    await expect(page.getByTestId('queue-item-0')).toContainText(/from-zip\.tac/i);
  });

  test('UJ-052 / TC-EV042-003: work queue keyboard + batch convert controls', async ({
    page,
  }) => {
    await stubWorkbenchNoise(page);
    await page.route('**/api/v1/convert', async (route) => {
      const postData = route.request().postData() ?? '';
      const nameHint = postData.includes('second') ? 'second.tac' : 'first.tac';
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          successful: 1,
          failed: 0,
          results: [
            {
              name: nameHint,
              content: `<?xml version="1.0"?><iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/2025-2"><iwxxm:observation/></iwxxm:METAR>`,
              tac_input: SAMPLE_METAR,
            },
          ],
        }),
      });
    });

    await openPublicConverter(page);
    await queueTwoTacFiles(page);

    const queue = page.getByTestId('operator-work-queue');
    await queue.focus();
    await page.keyboard.press('ArrowDown');
    await expect(page.getByTestId('queue-item-1')).toHaveAttribute(
      'aria-selected',
      'true',
    );

    await page.getByTestId('queue-select-0').check();
    await page.getByTestId('queue-select-1').check();
    await expect(page.getByTestId('batch-convert-button')).toBeEnabled();
    await expect(page.getByTestId('batch-validate-button')).toBeEnabled();

    await page.getByTestId('batch-convert-button').click();
    await expect(page.getByRole('region', { name: /conversion results/i })).toBeVisible(
      {
        timeout: 45_000,
      },
    );
  });

  test('UJ-052 companion: fixture TAC file still queues via Select Files', async ({
    page,
  }) => {
    await openPublicConverter(page);
    const fileInput = page.locator(
      'input[type="file"]:not([data-testid="mass-ingest-folder-input"]):not([data-testid="mass-ingest-zip-input"])',
    );
    await fileInput.setInputFiles(FIXTURE_TAC);
    await expect(page.getByTestId('operator-work-queue')).toBeVisible({
      timeout: 15_000,
    });
  });
});

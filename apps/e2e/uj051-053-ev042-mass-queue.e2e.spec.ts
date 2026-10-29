/**
 * T4.1 / H4–H5 wiring — Playwright smokes for UJ-051..053 (S050 / EV-042 / #897).
 *
 * Spec: docs/user-journeys.md UJ-051..053; docs/test-plan.md TC-F33-* + TC-EV042-*;
 * connectivity-gates H4–H5 (mass route CORS covered in pytest; this file is browser UJ).
 *
 * UX-2026-10-29-drop-mass-ingest: Convert toolbar no longer shows Mass Ingest chrome;
 * API auth gate remains. Queue journeys use Select files / drop.
 *
 * [Corpus: journeys §UJ-051..053] [Corpus: tests] [Corpus: product §F33] [Corpus: ui-style]
 */
import { expect, test, type Page } from '@playwright/test';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  convertManualMetar,
  openConvertSettings,
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
  await page.getByLabel('Select TAC files to upload', { exact: true }).setInputFiles([
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

test.describe('T4.1 — UJ-051..053 EV-042 mass ingest + queue + restored destinations', () => {
  test('UJ-053 / TC-EV091-001: Convert&Send + Disseminate visible; Mass Ingest absent; Upload to Database absent', async ({
    page,
  }) => {
    await openPublicConverter(page);
    await expect(page.getByTestId('convert-button')).toBeVisible();
    await expect(page.getByTestId('select-files-button')).toBeVisible();
    // Opposite state: Select files / Convert remain; Mass Ingest chrome was removed.
    await expect(page.getByTestId('mass-ingest-actions')).toHaveCount(0);
    // Opposite state: select-files-button is the file entry path, not Mass Ingest Folder.
    await expect(page.getByTestId('mass-ingest-folder-button')).toHaveCount(0);
    // Opposite state: select-files-button is visible; Mass Ingest ZIP is gone.
    await expect(page.getByTestId('mass-ingest-zip-button')).toHaveCount(0);

    await convertManualMetar(page, SAMPLE_METAR);
    await openConvertSettings(page);
    await expect(page.getByTestId('convert-and-send-button')).toBeVisible();
    await expect(page.getByTestId('open-dissemination-drawer')).toBeVisible();
    await expect(
      page.getByRole('region', { name: 'Conversion results', exact: true }),
    ).toBeVisible({
      timeout: 45_000,
    });
    // Opposite state: Disseminate / Convert & Send replace Upload to Database.
    await expect(page.getByTestId('upload-to-database-button')).toHaveCount(0);
  });

  test('UJ-051 / TC-F33-004: Convert chrome has no Mass Ingest Folder control', async ({
    page,
  }) => {
    await openPublicConverter(page);
    // Opposite state: Select files is the only folder/file entry control.
    await expect(page.getByTestId('select-files-button')).toBeVisible();
    await expect(page.getByTestId('mass-ingest-folder-button')).toHaveCount(0);
    // Opposite state: Convert heading and Select files label are present without Mass Ingest copy.
    await expect(page.getByText(/mass ingest/i)).toHaveCount(0);
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
    await expect(
      page.getByRole('region', { name: 'Conversion results', exact: true }),
    ).toBeVisible({
      timeout: 45_000,
    });
  });

  test('UJ-052 companion: fixture TAC file still queues via Select Files', async ({
    page,
  }) => {
    await openPublicConverter(page);
    await page
      .getByLabel('Select TAC files to upload', { exact: true })
      .setInputFiles(FIXTURE_TAC);
    await expect(page.getByTestId('operator-work-queue')).toBeVisible({
      timeout: 15_000,
    });
  });
});

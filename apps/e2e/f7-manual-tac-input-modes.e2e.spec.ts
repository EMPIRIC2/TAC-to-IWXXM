/**
 * TC-F7-007 / UJ-025 — Manual TAC Input modes (ADR-024 / #730 / S016 EV-012).
 *
 * Spec: docs/test-plan.md TC-F7-007; docs/user-journeys.md UJ-025.
 * Hard gates: T1–T6 (S2.2).
 */
import { expect, test, type Page, type Request } from '@playwright/test';
import { gzipSync } from 'node:zlib';
import {
  fillManualTac,
  openConverterForE2e,
  seedLocalWorkSession,
} from './playwright-e2e-helpers';

const METAR_TAC = 'METAR KJFK 121251Z 24016G28KT 3SM -RA BR BKN020 OVC040 14/11 A2990=';

const AHL_BULLETIN = `SAUS31 KZNY 121200
METAR KJFK 121151Z 18008KT 10SM FEW250 22/14 A3012=
METAR KLGA 121151Z 19010KT 10SM SCT040 21/13 A3010=
`;

const COLLECT_XML = `<?xml version="1.0"?>
<collect:MeteorologicalBulletin xmlns:collect="http://def.wmo.int/collect/1.2"
  xmlns:iwxxm="http://icao.int/iwxxm/3.0">
  <iwxxm:METAR/>
</collect:MeteorologicalBulletin>
`;

type Captured = {
  convert: Request[];
  convertBulletin: Request[];
  ingestCollect: Request[];
};

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
        residuals: [],
        summary: 'Stub summary',
      }),
    });
  });
}

async function stubModeApis(page: Page): Promise<Captured> {
  const captured: Captured = {
    convert: [],
    convertBulletin: [],
    ingestCollect: [],
  };

  await stubWorkbenchNoise(page);

  await page.route('**/api/v1/convert-bulletin', async (route) => {
    captured.convertBulletin.push(route.request());
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        bulletin_meta: {
          ahl: 'SAUS31 KZNY 121200',
          report_count: 2,
          tt: 'SA',
          aa: 'US',
          cccc: 'KZNY',
          yygggg: '121200',
          bbb: null,
        },
        results: [
          {
            report_index: 0,
            ok: true,
            tac_input: 'METAR KJFK 121151Z 18008KT 10SM FEW250 22/14 A3012=',
            xml: '<?xml version="1.0"?><iwxxm:METAR>KJFK</iwxxm:METAR>',
            issues: [],
            fixes: [],
          },
          {
            report_index: 1,
            ok: true,
            tac_input: 'METAR KLGA 121151Z 19010KT 10SM SCT040 21/13 A3010=',
            xml: '<?xml version="1.0"?><iwxxm:METAR>KLGA</iwxxm:METAR>',
            issues: [],
            fixes: [],
          },
        ],
      }),
    });
  });

  await page.route('**/api/v1/ingest-collect', async (route) => {
    captured.ingestCollect.push(route.request());
    await route.fulfill({
      status: 501,
      contentType: 'application/json',
      body: JSON.stringify({
        detail: {
          message: 'COLLECT member extract not implemented',
          code: 'not_implemented',
        },
      }),
    });
  });

  await page.route('**/api/v1/convert', async (route) => {
    captured.convert.push(route.request());
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        results: [
          {
            name: 'manual.xml',
            content: '<?xml version="1.0"?><iwxxm:METAR>KJFK</iwxxm:METAR>',
            source: 'manual',
            size_bytes: 48,
          },
        ],
        errors: [],
        issues: [],
        total_processed: 1,
        successful: 1,
        failed: 0,
      }),
    });
  });

  return captured;
}

test.describe('TC-F7-007 / UJ-025: Manual TAC Input modes', () => {
  test('T1: TAC report + Auto-detect convert OK', async ({ page }) => {
    const captured = await stubModeApis(page);
    await openConverterForE2e(page);

    await expect(page.getByTestId('input-mode-group')).toBeVisible();
    await expect(page.getByTestId('input-mode-tac')).toBeVisible();
    await expect(page.getByTestId('product-type-select')).toHaveValue('auto');

    await fillManualTac(page, METAR_TAC);
    await page.getByTestId('convert-button').click();

    await expect(page.getByRole('region', { name: /conversion results/i })).toBeVisible(
      {
        timeout: 10000,
      },
    );
    expect(captured.convert.length).toBeGreaterThanOrEqual(1);
    expect(captured.convertBulletin).toHaveLength(0);
    expect(captured.ingestCollect).toHaveLength(0);
  });

  test('T2: AHL bulletin hits convert-bulletin + summary', async ({ page }) => {
    const captured = await stubModeApis(page);
    await openConverterForE2e(page);

    await page.getByTestId('input-mode-ahl_bulletin').click();
    await expect(page.getByText(/convert-bulletin/i)).toBeVisible();

    await fillManualTac(page, AHL_BULLETIN);
    await page.getByTestId('convert-button').click();

    await expect(page.getByTestId('bulletin-summary')).toBeVisible({ timeout: 10000 });
    await expect(page.getByTestId('bulletin-summary')).toContainText(/2 report/i);
    expect(captured.convertBulletin.length).toBeGreaterThanOrEqual(1);
    expect(captured.convert).toHaveLength(0);
  });

  test('T3: paste AHL in TAC mode auto-switches (required)', async ({ page }) => {
    const captured = await stubModeApis(page);
    await openConverterForE2e(page);

    await expect(page.getByTestId('input-mode-tac')).toBeVisible();
    await fillManualTac(page, AHL_BULLETIN);
    await page.getByTestId('convert-button').click();

    await expect(page.getByTestId('input-mode-ahl_bulletin')).toHaveClass(
      /bg-blue-600/,
      { timeout: 10000 },
    );
    await expect(page.getByText(/Detected AHL bulletin/i).first()).toBeVisible({
      timeout: 5000,
    });
    await expect(page.getByTestId('bulletin-summary')).toBeVisible({ timeout: 10000 });
    expect(captured.convertBulletin.length).toBeGreaterThanOrEqual(1);
    expect(captured.convert).toHaveLength(0);
  });

  test('T4: IWXXM COLLECT → ingest-collect 501 placeholder UX', async ({ page }) => {
    const captured = await stubModeApis(page);
    await openConverterForE2e(page);

    await page.getByTestId('input-mode-collect_iwxxm').click();
    await expect(page.getByText(/ingest-collect/i)).toBeVisible();
    await expect(page.getByText(/501/i)).toBeVisible();

    await fillManualTac(page, COLLECT_XML);
    await page.getByTestId('convert-button').click();

    await expect(page.getByTestId('placeholder-notice')).toBeVisible({
      timeout: 10000,
    });
    await expect(page.getByText(/COLLECT ingest placeholder/i).first()).toBeVisible({
      timeout: 5000,
    });
    expect(captured.ingestCollect.length).toBeGreaterThanOrEqual(1);
    expect(captured.convert).toHaveLength(0);
    expect(captured.convertBulletin).toHaveLength(0);
  });

  test('T5: .gz COLLECT inflates and hits ingest-collect 501', async ({ page }) => {
    const captured = await stubModeApis(page);
    await openConverterForE2e(page);

    const gz = gzipSync(Buffer.from(COLLECT_XML, 'utf8'));
    await page.setInputFiles('input[type="file"]', {
      name: 'metar-collect.xml.gz',
      mimeType: 'application/gzip',
      buffer: gz,
    });

    await expect(page.getByText(/Decompressed/i).first()).toBeVisible({
      timeout: 10000,
    });
    await expect(page.getByText(/Detected IWXXM COLLECT/i).first()).toBeVisible({
      timeout: 10000,
    });
    await expect(page.getByTestId('input-mode-collect_iwxxm')).toHaveClass(
      /bg-blue-600/,
    );

    await page.getByTestId('convert-button').click();
    await expect(page.getByTestId('placeholder-notice')).toBeVisible({
      timeout: 10000,
    });
    expect(captured.ingestCollect.length).toBeGreaterThanOrEqual(1);
  });

  test('T6: finished session disables mode buttons', async ({ page }) => {
    // Guest path uses IndexedDB (not /work-sessions) — seed locally like UJ-004.
    await page.goto('/');
    await seedLocalWorkSession(page, {
      id: 'finished-modes-1',
      user_id: 'local',
      product: 'metar',
      status: 'finished',
      title: 'KJFK finished modes',
      manual_tac: METAR_TAC,
      pending_files: [],
      converted_results: [
        {
          name: 'manual',
          tac_input: METAR_TAC,
          iwxxm_xml: '<iwxxm/>',
        },
      ],
      errors: [],
      issues: [],
      conversion_params: {},
      kv_upload_key: 'kv-1',
      deleted_at: null,
      created_at: '2026-07-20T00:00:00Z',
      updated_at: '2026-07-20T00:00:00Z',
    });

    await page.reload();
    await openConverterForE2e(page);
    await expect(
      page.getByRole('button', { name: /KJFK finished modes/i }),
    ).toBeVisible({
      timeout: 15000,
    });
    await page.getByRole('button', { name: /KJFK finished modes/i }).click();

    await expect(page.getByTestId('input-mode-tac')).toBeDisabled({ timeout: 10000 });
    await expect(page.getByTestId('input-mode-ahl_bulletin')).toBeDisabled();
    await expect(page.getByTestId('input-mode-collect_iwxxm')).toBeDisabled();
  });
});

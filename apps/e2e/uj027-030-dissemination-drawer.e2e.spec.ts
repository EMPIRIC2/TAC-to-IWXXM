/**
 * T6.3 / H6′ — Playwright smokes for UJ-027–030 (F16–F19 dissemination drawer).
 *
 * Spec: docs/test-plan.md TC-F16..F19 + H6′; docs/user-journeys.md UJ-027–030.
 * Live BYOC (TC-F17-002 / TC-F18-002) remains cycle-close only — stubbed here.
 */
import { expect, test, type Page, type Request } from '@playwright/test';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { fillManualTac, openConverterForE2e } from './playwright-e2e-helpers';

const METAR_TAC = 'METAR KJFK 121251Z 24016G28KT 3SM -RA BR BKN020 OVC040 14/11 A2990=';
const IWXXM_XML =
  '<?xml version="1.0"?><iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/2025-2"><iwxxm:observation/></iwxxm:METAR>';

const E2E_DIR = path.dirname(fileURLToPath(import.meta.url));
const FIXTURE_TAC = path.join(E2E_DIR, 'fixtures', 'dissemination-sample.tac');

type DisseminationCapture = {
  preflight: Request[];
  send: Request[];
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

async function stubConvert(page: Page): Promise<void> {
  await page.route('**/api/v1/convert', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        ok: true,
        results: [
          {
            name: 'manual.metar',
            iwxxm_xml: IWXXM_XML,
            tac_input: METAR_TAC,
            convertedContent: IWXXM_XML,
          },
        ],
        errors: [],
        issues: [],
        failed_spans: [],
        total_processed: 1,
        successful: 1,
      }),
    });
  });
}

async function stubDisseminationApis(
  page: Page,
  options?: {
    preflightBody?: Record<string, unknown>;
    sendBody?: Record<string, unknown>;
    preflightStatus?: number;
  },
): Promise<DisseminationCapture> {
  const captured: DisseminationCapture = { preflight: [], send: [] };
  const preflightBody = options?.preflightBody ?? {
    ok: true,
    connectivity_ok: true,
    diffs: [],
    handle: 'e2e-handle-green',
    detail: null,
  };
  const sendBody = options?.sendBody ?? {
    ok: true,
    kv_upload_key: 'kv:e2e:upload:1',
    detail: null,
  };

  await page.route('**/api/v1/dissemination/preflight', async (route) => {
    captured.preflight.push(route.request());
    await route.fulfill({
      status: options?.preflightStatus ?? 200,
      contentType: 'application/json',
      body: JSON.stringify(preflightBody),
    });
  });

  await page.route('**/api/v1/dissemination/send', async (route) => {
    captured.send.push(route.request());
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(sendBody),
    });
  });

  return captured;
}

async function openDisseminationDrawer(page: Page): Promise<void> {
  const openBtn = page.getByTestId('open-dissemination-drawer');
  await expect(openBtn).toBeEnabled({ timeout: 15000 });
  await openBtn.click();
  await expect(page.getByTestId('dissemination-drawer')).toBeVisible();
  await expect(page.getByRole('heading', { name: /dissemination/i })).toBeVisible();
}

async function prepareWorkbench(page: Page): Promise<void> {
  await stubWorkbenchNoise(page);
  await stubConvert(page);
  await openConverterForE2e(page);
  await fillManualTac(page, METAR_TAC);
}

test.describe('T6.3 / UJ-027–030: dissemination drawer H6′ smokes', () => {
  test('UJ-027: multi-DB BYOC — failed Disseminate shows red progress; retry succeeds', async ({
    page,
  }) => {
    await prepareWorkbench(page);

    let preflightCalls = 0;
    const captured: DisseminationCapture = { preflight: [], send: [] };

    await page.route('**/api/v1/dissemination/preflight', async (route) => {
      captured.preflight.push(route.request());
      preflightCalls += 1;
      if (preflightCalls === 1) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            ok: false,
            connectivity_ok: true,
            diffs: [
              {
                kind: 'missing_column',
                table: 'iwxxm_reports',
                column: 'iwxxm_xml',
                detail: 'column missing — run DDL or alter table',
              },
            ],
            handle: null,
            detail: 'schema mismatch',
          }),
        });
        return;
      }
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          ok: true,
          connectivity_ok: true,
          diffs: [],
          handle: 'e2e-pg-handle',
          detail: null,
        }),
      });
    });

    await page.route('**/api/v1/dissemination/send', async (route) => {
      captured.send.push(route.request());
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          ok: true,
          kv_upload_key: 'kv:e2e:pg:1',
          detail: null,
        }),
      });
    });

    await openDisseminationDrawer(page);

    await page.getByTestId('dissemination-sink-chooser').selectOption('postgres');
    const sendBtn = page.getByTestId('dissemination-send-button');
    await expect(sendBtn).toBeDisabled();

    await page
      .getByTestId('dissemination-uri-input')
      .fill('postgresql://u:p@db.example.com:5432/wx');
    await expect(sendBtn).toBeEnabled();

    await sendBtn.click();
    await expect(
      page.locator('[data-testid^="dissemination-progress-row-"]').first(),
    ).toHaveAttribute('data-status', 'failed');
    expect(captured.send.length).toBe(0);

    await page
      .getByTestId('dissemination-uri-input')
      .fill('postgresql://u:p@db.example.com:5432/wx_ok');
    await page.getByTestId('dissemination-ddl-toggle').check();
    await sendBtn.click();

    await expect(page.getByTestId('dissemination-send-success')).toBeVisible();
    await expect(
      page.locator('[data-testid^="dissemination-progress-row-"]').first(),
    ).toHaveAttribute('data-status', 'success');

    expect(captured.preflight.length).toBe(2);
    expect(captured.send.length).toBe(1);
    const firstBody = captured.preflight[0].postDataJSON() as {
      sink_type: string;
      uri: string;
    };
    expect(firstBody.sink_type).toBe('postgres');
    expect(firstBody.uri).toContain('postgresql://');
    const sendBody = captured.send[0].postDataJSON() as {
      handle: string;
      iwxxm_xml?: string;
      tac_text?: string;
    };
    expect(sendBody.handle).toBe('e2e-pg-handle');
    expect(Boolean(sendBody.iwxxm_xml || sendBody.tac_text)).toBe(true);
  });

  test('UJ-027: drag-drop TAC file reaches Disseminate (TC-F16-004)', async ({
    page,
  }) => {
    await stubWorkbenchNoise(page);
    await openConverterForE2e(page);
    const captured = await stubDisseminationApis(page, {
      preflightBody: {
        ok: true,
        connectivity_ok: true,
        diffs: [],
        handle: 'e2e-drop-handle',
      },
      sendBody: {
        ok: true,
        kv_upload_key: 'kv:e2e:drop:1',
      },
    });

    await openDisseminationDrawer(page);

    await page.getByTestId('dissemination-sink-chooser').selectOption('sqlite');
    await page
      .getByTestId('dissemination-uri-input')
      .fill('sqlite:////tmp/e2e-dissemination.db');

    await page.getByTestId('dissemination-file-input').setInputFiles(FIXTURE_TAC);
    await expect(page.getByTestId('dissemination-payload-status')).toContainText(
      /1 candidate/,
    );

    await page.getByTestId('dissemination-send-button').click();
    await expect(page.getByTestId('dissemination-send-success')).toBeVisible();

    const sendBody = captured.send[0].postDataJSON() as { tac_text?: string };
    expect(sendBody.tac_text).toContain('METAR');
  });

  test('UJ-027: multi-select drop + forced fail continues; progress screenshot (TC-F16-005)', async ({
    page,
  }) => {
    await stubWorkbenchNoise(page);
    await openConverterForE2e(page);

    let preflightCalls = 0;
    await page.route('**/api/v1/dissemination/preflight', async (route) => {
      preflightCalls += 1;
      if (preflightCalls === 1) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            ok: false,
            connectivity_ok: false,
            diffs: [],
            detail: 'first fail',
          }),
        });
        return;
      }
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          ok: true,
          connectivity_ok: true,
          diffs: [],
          handle: 'e2e-multi-ok',
        }),
      });
    });
    await page.route('**/api/v1/dissemination/send', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ ok: true, kv_upload_key: 'kv:e2e:multi:1' }),
      });
    });

    await openDisseminationDrawer(page);
    await page.getByTestId('dissemination-sink-chooser').selectOption('sqlite');
    await page
      .getByTestId('dissemination-uri-input')
      .fill('sqlite:////tmp/e2e-multi.db');

    await page.getByTestId('dissemination-file-input').setInputFiles(FIXTURE_TAC);
    // Second drop — create a second file via setInputFiles again with a copy name.
    await page.getByTestId('dissemination-file-input').setInputFiles({
      name: 'second.tac',
      mimeType: 'text/plain',
      buffer: Buffer.from('METAR KJFK 121251Z 24008KT 10SM CLR 18/12 A3012='),
    });

    await expect(page.getByTestId('dissemination-export-selection')).toBeVisible();
    await page.getByTestId('dissemination-select-all').click();
    await page.getByTestId('dissemination-send-button').click();

    await expect(page.getByTestId('dissemination-send-success')).toContainText(
      /1 file/,
    );
    const failRow = page
      .locator('[data-testid^="dissemination-progress-row-"][data-status="failed"]')
      .first();
    await expect(failRow).toBeVisible();
    await expect(failRow.getByTestId(/dissemination-progress-fail-/)).toBeVisible();

    await expect(page.getByTestId('dissemination-progress-list')).toHaveScreenshot(
      'dissemination-progress-multi-partial-fail.png',
      { animations: 'disabled' },
    );
  });

  test('UJ-028: WIS2 sink uses BYOC params (staging path mocked)', async ({ page }) => {
    await prepareWorkbench(page);
    const captured = await stubDisseminationApis(page, {
      preflightBody: {
        ok: true,
        connectivity_ok: true,
        diffs: [],
        handle: 'e2e-wis2-handle',
      },
      sendBody: {
        ok: true,
        kv_upload_key: 'kv:e2e:wis2:1',
      },
    });

    await openDisseminationDrawer(page);
    await page.getByTestId('dissemination-sink-chooser').selectOption('wis2');
    await expect(page.getByTestId('dissemination-byoc-params')).toBeVisible();
    await expect(page.getByTestId('dissemination-uri-input')).toHaveCount(0);
    await expect(page.getByTestId('dissemination-non-db-hint')).toBeVisible();

    await page.getByTestId('dissemination-byoc-params').fill(
      JSON.stringify({
        broker: 'mqtt://wis2box-broker:1883',
        topic: 'origin/a/wis2/test',
        dataset_url: 'http://wis2box-api:80/oapi/collections/discovery/items',
      }),
    );

    await page.getByTestId('dissemination-send-button').click();
    await expect(page.getByTestId('dissemination-send-success')).toBeVisible();

    const body = captured.preflight[0].postDataJSON() as {
      sink_type: string;
      params: Record<string, string>;
    };
    expect(body.sink_type).toBe('wis2');
    expect(body.params.broker).toContain('wis2box');
  });

  test('UJ-029: EDIS sink — BYOC JSON + mocked Disseminate (live BYOC cycle-close)', async ({
    page,
  }) => {
    await prepareWorkbench(page);
    const captured = await stubDisseminationApis(page, {
      preflightBody: {
        ok: true,
        connectivity_ok: true,
        diffs: [],
        handle: 'e2e-edis-handle',
      },
      sendBody: {
        ok: true,
        kv_upload_key: 'kv:e2e:edis:1',
      },
    });

    await openDisseminationDrawer(page);
    await page.getByTestId('dissemination-sink-chooser').selectOption('edis');
    await page.getByTestId('dissemination-byoc-params').fill(
      JSON.stringify({
        host: 'smtp.example.com',
        port: 587,
        username: 'edis-user',
        password: 'secret-not-stored',
      }),
    );

    await page.getByTestId('dissemination-send-button').click();
    await expect(page.getByTestId('dissemination-send-success')).toBeVisible();

    const body = captured.preflight[0].postDataJSON() as { sink_type: string };
    expect(body.sink_type).toBe('edis');
    expect(captured.send[0].postDataJSON()).toMatchObject({
      handle: 'e2e-edis-handle',
    });
  });

  test('UJ-030: AMHS / SWIM / AFS adapters each reach Disseminate success', async ({
    page,
  }) => {
    await prepareWorkbench(page);

    const adapters = ['amhs', 'swim', 'afs'] as const;
    for (const sink of adapters) {
      const captured = await stubDisseminationApis(page, {
        preflightBody: {
          ok: true,
          connectivity_ok: true,
          diffs: [],
          handle: `e2e-${sink}-handle`,
        },
        sendBody: {
          ok: true,
          kv_upload_key: `kv:e2e:${sink}:1`,
        },
      });

      await openDisseminationDrawer(page);
      await page.getByTestId('dissemination-sink-chooser').selectOption(sink);
      await page
        .getByTestId('dissemination-byoc-params')
        .fill(
          JSON.stringify({ endpoint: `https://${sink}.example.test/v1`, token: 't' }),
        );

      await page.getByTestId('dissemination-send-button').click();
      await expect(page.getByTestId('dissemination-send-success')).toBeVisible();

      const body = captured.preflight[0].postDataJSON() as { sink_type: string };
      expect(body.sink_type).toBe(sink);

      await page.getByTestId('dissemination-drawer-close').click();
      await expect(page.getByTestId('dissemination-drawer')).toHaveCount(0);

      await page.unroute('**/api/v1/dissemination/preflight');
      await page.unroute('**/api/v1/dissemination/send');
    }
  });

  test('UJ-027: SSRF/allowlist failure surfaces actionable drawer error (TC-F16-002 smoke)', async ({
    page,
  }) => {
    await prepareWorkbench(page);
    await stubDisseminationApis(page, {
      preflightStatus: 400,
      preflightBody: {
        detail: 'Destination host not on DISSEMINATION_EGRESS_ALLOWLIST',
      },
    });

    await openDisseminationDrawer(page);
    await page
      .getByTestId('dissemination-uri-input')
      .fill('postgresql://u:p@169.254.169.254/meta');
    await page.getByTestId('dissemination-preflight-button').click();

    await expect(page.getByTestId('dissemination-error')).toContainText(
      /allowlist|egress|not on|failed/i,
    );
  });
});

/**
 * F7 UI↔API connection-point integration (S011 / EV-008).
 *
 * Asserts each workbench surface talks to the correct API path with the fields
 * the frontend client sends (product, preview, multipart TAC). Responses are
 * fulfilled with shapes from apps/frontend/src/utils/api.ts so UI wiring is
 * exercised end-to-end without depending on a live convert engine.
 *
 * Spec: docs/test-plan.md TC-F7-001–005; docs/api-contract.md.
 */
import { expect, test, type Page, type Request } from '@playwright/test';
import { openConverterForE2e } from './playwright-e2e-helpers';

const METAR_TAC = 'METAR KJFK 121251Z 24016G28KT 3SM -RA BR BKN020 OVC040 14/11 A2990';
const BAD_TAC = 'METAR XXXX NOT_A_REAL_REPORT GARBAGE=';

type Captured = {
  lint: Request[];
  decode: Request[];
  convert: Request[];
  sessions: Request[];
};

async function wireF7ApiStubs(page: Page): Promise<Captured> {
  const captured: Captured = {
    lint: [],
    decode: [],
    convert: [],
    sessions: [],
  };

  await page.route('**/api/v1/lint-tac', async (route) => {
    captured.lint.push(route.request());
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        ok: false,
        issues: [
          {
            severity: 'error',
            code: 'conn_span',
            message: 'Connection-point lint span',
            start: 0,
            end: 5,
          },
        ],
        fixes: [],
        product: 'METAR',
      }),
    });
  });

  await page.route('**/api/v1/decode-tac', async (route) => {
    captured.decode.push(route.request());
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        product: 'METAR',
        segments: [
          {
            start: 0,
            end: 5,
            code: 'METAR',
            explanation: 'Report type',
          },
        ],
        residuals: [],
      }),
    });
  });

  await page.route('**/api/v1/convert', async (route) => {
    captured.convert.push(route.request());
    const postData = route.request().postData() ?? '';
    const preview = postData.includes('name="preview"') && postData.includes('true');
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        results: preview
          ? [
              {
                name: 'preview.xml',
                content: '<?xml version="1.0"?><iwxxm:METAR/>',
                source: 'manual',
                size_bytes: 40,
              },
            ]
          : [],
        errors: preview ? [] : ['parse failed'],
        issues: [],
        total_processed: 1,
        successful: preview ? 1 : 0,
        failed: preview ? 0 : 1,
        ok: preview ? false : undefined,
        failed_spans: preview
          ? [
              {
                start: 6,
                end: 10,
                code: 'parse_failed',
                message: 'Station group invalid',
              },
            ]
          : [],
      }),
    });
  });

  await page.route('**/api/v1/work-sessions**', async (route) => {
    captured.sessions.push(route.request());
    const method = route.request().method();
    const url = route.request().url();

    if (method === 'GET' && !/\/work-sessions\/[^/?]+/.test(url)) {
      const productFilter = new URL(url).searchParams.get('product');
      const items =
        productFilter === 'metar,speci'
          ? [
              {
                id: 'sess-metar',
                user_id: 'user-1',
                product: 'metar',
                status: 'draft',
                title: 'KJFK',
                manual_tac: METAR_TAC,
                pending_files: [],
                converted_results: [],
                errors: [],
                issues: [],
                conversion_params: {},
                kv_upload_key: null,
                deleted_at: null,
                created_at: '2026-07-14T00:00:00Z',
                updated_at: '2026-07-14T00:00:00Z',
              },
            ]
          : [
              {
                id: 'sess-taf',
                user_id: 'user-1',
                product: 'taf',
                status: 'draft',
                title: 'TAF',
                manual_tac: 'TAF KJFK 121730Z 1218/1324 18010KT=',
                pending_files: [],
                converted_results: [],
                errors: [],
                issues: [],
                conversion_params: {},
                kv_upload_key: null,
                deleted_at: null,
                created_at: '2026-07-14T00:00:00Z',
                updated_at: '2026-07-14T00:00:00Z',
              },
            ];
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items,
          total: items.length,
          page: 1,
          limit: 20,
        }),
      });
      return;
    }

    if (method === 'POST') {
      await route.fulfill({
        status: 201,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'sess-new',
          user_id: 'user-1',
          product: 'metar',
          status: 'draft',
          title: 'KJFK',
          manual_tac: METAR_TAC,
          pending_files: [],
          converted_results: [],
          errors: [],
          issues: [],
          conversion_params: {},
          kv_upload_key: null,
          deleted_at: null,
          created_at: '2026-07-14T00:00:00Z',
          updated_at: '2026-07-14T00:00:00Z',
        }),
      });
      return;
    }

    if (method === 'PATCH') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'sess-new',
          user_id: 'user-1',
          product: 'metar',
          status: 'draft',
          title: 'KJFK',
          manual_tac: METAR_TAC,
          pending_files: [],
          converted_results: [],
          errors: [],
          issues: [],
          conversion_params: {},
          kv_upload_key: null,
          deleted_at: null,
          created_at: '2026-07-14T00:00:00Z',
          updated_at: '2026-07-14T00:00:01Z',
        }),
      });
      return;
    }

    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ ok: true }),
    });
  });

  return captured;
}

async function postDataIncludes(
  request: Request,
  field: string,
  value?: string,
): Promise<boolean> {
  const data = request.postData() ?? '';
  if (!data.includes(`name="${field}"`)) {
    return false;
  }
  if (value === undefined) {
    return true;
  }
  return data.includes(value);
}

test.describe('F7 UI↔API connection points', () => {
  test('lint-tac + decode-tac fired with product after editor input', async ({
    page,
  }) => {
    const captured = await wireF7ApiStubs(page);
    await openConverterForE2e(page);

    await page.getByLabel(/Expand parameters/i).click();
    await page.locator('#param-product').selectOption('METAR');

    const editor = page.getByLabel(/Enter METAR data manually/i);
    await editor.click();
    await editor.fill(METAR_TAC);

    await expect.poll(() => captured.lint.length, { timeout: 5000 }).toBeGreaterThan(0);
    await expect
      .poll(() => captured.decode.length, { timeout: 5000 })
      .toBeGreaterThan(0);

    const lintReq = captured.lint.at(-1)!;
    const decodeReq = captured.decode.at(-1)!;
    expect(lintReq.method()).toBe('POST');
    expect(decodeReq.method()).toBe('POST');
    expect(lintReq.url()).toContain('/api/v1/lint-tac');
    expect(decodeReq.url()).toContain('/api/v1/decode-tac');
    expect(await postDataIncludes(lintReq, 'manual_text')).toBe(true);
    expect(await postDataIncludes(decodeReq, 'manual_text')).toBe(true);
    expect(await postDataIncludes(decodeReq, 'product', 'METAR')).toBe(true);

    await expect(page.getByTestId('decode-panel')).toBeVisible();
    await expect(page.getByTestId('tac-editor')).toHaveAttribute(
      'data-issue-span-count',
      '1',
    );
  });

  test('soft-preview convert sends preview=true and shows Failed-TAC cue', async ({
    page,
  }) => {
    const captured = await wireF7ApiStubs(page);
    await openConverterForE2e(page);

    await page.getByTestId('soft-preview-toggle').check();

    const editor = page.getByLabel(/Enter METAR data manually/i);
    await editor.fill(BAD_TAC);
    await page.getByTestId('convert-button').click();

    await expect
      .poll(() => captured.convert.length, { timeout: 10000 })
      .toBeGreaterThan(0);
    const convertReq = captured.convert.at(-1)!;
    expect(convertReq.url()).toContain('/api/v1/convert');
    expect(await postDataIncludes(convertReq, 'preview', 'true')).toBe(true);
    await expect(page.getByTestId('failed-tac-cue')).toBeVisible({
      timeout: 10000,
    });
  });

  test('work-sessions connection posts/patches with product field', async ({
    page,
  }) => {
    const captured = await wireF7ApiStubs(page);
    await openConverterForE2e(page);

    const editor = page.getByLabel(/Enter METAR data manually/i);
    await editor.fill(METAR_TAC);

    await expect
      .poll(
        () =>
          captured.sessions.filter((r) => ['POST', 'PATCH'].includes(r.method()))
            .length,
        { timeout: 10000 },
      )
      .toBeGreaterThan(0);

    const write = captured.sessions.find((r) =>
      ['POST', 'PATCH'].includes(r.method()),
    )!;
    expect(write.url()).toContain('/api/v1/work-sessions');
    const body = write.postData() ?? '';
    // JSON body from workSessionApi
    expect(body).toMatch(/"product"\s*:\s*"(metar|METAR)"/i);
  });
});

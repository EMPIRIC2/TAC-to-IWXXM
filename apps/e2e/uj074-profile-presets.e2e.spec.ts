/**
 * H4–H5 / T2 — Playwright smokes for UJ-074 semantic presets + dissemination templates
 * (EV-1051 / #1051 closeout).
 *
 * Spec: docs/test-plan.md TC-EV1051-005..006; docs/user-journeys.md UJ-074.
 * Auth is seeded via localStorage + stubbed profile/dissemination APIs (no live JWT).
 * Live H4–H5 against stage FE is deferred until this closeout lands on stage.
 */
import { expect, test, type Page, type Request } from '@playwright/test';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  dismissPrivacyNoticeIfPresent,
  openPublicConverter,
} from './playwright-e2e-helpers';

const MOCK_TOKEN = 'e2e-mock-presets-jwt';
const PRESET_ID = 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa';
const TEMPLATE_ID = 'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb';
const USER_ID = '33333333-3333-4333-8333-333333333333';
const METAR_TAC = 'METAR KJFK 121251Z 24016G28KT 3SM -RA BR BKN020 OVC040 14/11 A2990=';
const IWXXM_XML =
  '<?xml version="1.0"?><iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/2025-2"><iwxxm:observation/></iwxxm:METAR>';
const E2E_DIR = path.dirname(fileURLToPath(import.meta.url));
const FIXTURE_TAC = path.join(E2E_DIR, 'fixtures', 'dissemination-sample.tac');

type Capture = {
  presetsPost: Request[];
  convert: Request[];
  preflight: Request[];
};

async function seedMockAuth(page: Page): Promise<void> {
  await page.addInitScript((token) => {
    const expiresAt = String(Math.floor(Date.now() / 1000) + 3600);
    localStorage.setItem('access_token', token);
    localStorage.setItem('refresh_token', 'e2e-mock-refresh');
    localStorage.setItem('expires_at', expiresAt);
  }, MOCK_TOKEN);
}

async function stubWorkbenchNoise(page: Page): Promise<void> {
  await page.route('**/api/v1/work-sessions**', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ items: [], total: 0, page: 1, limit: 20 }),
    });
  });
  await page.route('**/api/v1/lint-tac', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ ok: true, issues: [], fixes: [], product: 'METAR' }),
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
  await page.route('**/api/v1/lint-issue-catalog**', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ issues: [] }),
    });
  });
}

async function stubEv1051Apis(page: Page): Promise<Capture> {
  const captured: Capture = { presetsPost: [], convert: [], preflight: [] };
  let presets: Array<Record<string, unknown>> = [];
  let templates: Array<Record<string, unknown>> = [
    {
      id: TEMPLATE_ID,
      user_id: USER_ID,
      slug: 'shared-sqlite',
      name: 'Shared SQLite',
      sinkType: 'sqlite',
      product: 'metar',
      ddl: false,
      params: { table: 'reports' },
      shared: true,
      created_at: '2026-09-09T00:00:00Z',
      updated_at: '2026-09-09T00:00:00Z',
    },
  ];

  await page.route('**/api/v1/profiles/catalog**', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        schema_version: 1,
        profiles: [
          {
            id: 'ICAO_2025',
            kind: 'semantic',
            status: 'implemented',
            products: ['METAR', 'SPECI', 'TAF'],
            emit_key: 'annex3',
            deltas_vs_icao: ['Baseline ICAO/WMO line.'],
            iwxxm_line: 'IWXXM 2025-2 core',
            rule_pack_count: 0,
            overlay_count: 0,
            vendor_pins: { iwxxm: 'WMO IWXXM 2025-2' },
            implementation: {
              input: 'tac2iwxxm/profiles/annex3',
              conversion: 'annex3 emit plugin',
            },
          },
          {
            id: 'CA_ECCC',
            kind: 'semantic',
            status: 'pilot',
            products: ['METAR', 'SPECI', 'TAF'],
            emit_key: 'ca_eccc',
            deltas_vs_icao: ['Pins the MSC operational IWXXM line.'],
            iwxxm_line: 'IWXXM 3.0.0 (MSC operational)',
            rule_pack_count: 0,
            overlay_count: 0,
            vendor_pins: { iwxxm: 'MSC 3.0.0' },
            implementation: {
              input: 'tac2iwxxm/profiles/ca_eccc',
              conversion: 'ca_eccc emit plugin',
            },
          },
        ],
      }),
    });
  });

  await page.route('**/api/v1/profiles/rule-packs**', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ items: [] }),
    });
  });

  await page.route('**/api/v1/profiles/overlays**', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ items: [] }),
    });
  });

  await page.route('**/api/v1/profiles/presets**', async (route) => {
    const req = route.request();
    if (req.method() === 'GET') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: presets }),
      });
      return;
    }
    if (req.method() === 'POST') {
      captured.presetsPost.push(req);
      const body = (req.postDataJSON() ?? {}) as Record<string, unknown>;
      const created = {
        id: PRESET_ID,
        user_id: USER_ID,
        slug: body.slug ?? 'e2e-preset',
        name: body.name ?? 'E2E Preset',
        semanticProfile: body.semantic_profile ?? body.semanticProfile ?? 'CA_ECCC',
        iwxxmVersion: body.iwxxm_version ?? body.iwxxmVersion ?? '3.0.0',
        extensions: body.extensions ?? [],
        reportVariant: body.report_variant ?? body.reportVariant ?? 'LWIS',
        overlayId: body.overlay_id ?? body.overlayId ?? null,
        shared: Boolean(body.shared ?? true),
        created_at: '2026-09-09T00:00:00Z',
        updated_at: '2026-09-09T00:00:00Z',
      };
      presets = [created];
      await route.fulfill({
        status: 201,
        contentType: 'application/json',
        body: JSON.stringify(created),
      });
      return;
    }
    await route.fallback();
  });

  await page.route('**/api/v1/profiles/templates**', async (route) => {
    const req = route.request();
    if (req.method() === 'GET') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: templates }),
      });
      return;
    }
    if (req.method() === 'POST') {
      const body = (req.postDataJSON() ?? {}) as Record<string, unknown>;
      const created = {
        id: TEMPLATE_ID,
        user_id: USER_ID,
        slug: body.slug ?? 'shared-sqlite',
        name: body.name ?? 'Shared SQLite',
        sinkType: body.sink_type ?? body.sinkType ?? 'sqlite',
        product: body.product ?? 'metar',
        ddl: Boolean(body.ddl ?? false),
        params: body.params ?? { table: 'reports' },
        shared: Boolean(body.shared ?? true),
        created_at: '2026-09-09T00:00:00Z',
        updated_at: '2026-09-09T00:00:00Z',
      };
      templates = [created];
      await route.fulfill({
        status: 201,
        contentType: 'application/json',
        body: JSON.stringify(created),
      });
      return;
    }
    await route.fallback();
  });

  await page.route('**/api/v1/convert', async (route) => {
    captured.convert.push(route.request());
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
            content: IWXXM_XML,
            convertedContent: IWXXM_XML,
          },
        ],
        errors: [],
        issues: [],
        failed_spans: [],
        total_processed: 1,
        successful: 1,
        metadata: {
          preset_id: PRESET_ID,
          semantic_profile: 'ca_eccc',
        },
      }),
    });
  });

  await page.route('**/api/v1/dissemination/preflight', async (route) => {
    captured.preflight.push(route.request());
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        ok: true,
        connectivity_ok: true,
        diffs: [],
        detail: null,
      }),
    });
  });

  return captured;
}

async function openProfiles(page: Page): Promise<void> {
  await openPublicConverter(page);
  await page.getByTestId('shell-nav-profiles').click();
  await expect(page.getByTestId('conversion-profiles-page')).toBeVisible();
}

function expectBearer(req: Request): void {
  expect(req.headers().authorization).toBe(`Bearer ${MOCK_TOKEN}`);
}

test.describe('UJ-074: semantic presets + dissemination templates (EV-1051)', () => {
  test('TC-EV1051: create shared preset, apply on convert, load template + one-shot preflight', async ({
    page,
  }) => {
    await seedMockAuth(page);
    await stubWorkbenchNoise(page);
    const captured = await stubEv1051Apis(page);

    await openProfiles(page);
    await expect(page.getByTestId('conversion-profiles-presets')).toBeVisible();

    await page.getByTestId('conversion-profiles-preset-slug').fill('e2e-preset');
    await page.getByTestId('conversion-profiles-preset-name').fill('E2E Shared Preset');
    await page.getByTestId('conversion-profiles-preset-profile').fill('CA_ECCC');
    await page.getByTestId('conversion-profiles-preset-iwxxm-version').fill('3.0.0');
    await page.getByTestId('conversion-profiles-preset-report-variant').fill('LWIS');
    const shared = page.getByTestId('conversion-profiles-preset-shared');
    if (!(await shared.isChecked())) {
      await shared.check();
    }
    await page.getByTestId('conversion-profiles-preset-save').click();
    await expect.poll(() => captured.presetsPost.length).toBe(1);
    expectBearer(captured.presetsPost[0]!);
    const presetBody = captured.presetsPost[0]!.postDataJSON() as {
      slug?: string;
      shared?: boolean;
      semanticProfile?: string;
    };
    expect(presetBody.slug).toBe('e2e-preset');
    expect(presetBody.shared).toBe(true);
    expect(presetBody.semanticProfile).toBe('CA_ECCC');

    await page.getByTestId('shell-nav-converter').click();
    await expect(
      page.getByRole('heading', { name: /METAR.*IWXXM.*Converter/i }),
    ).toBeVisible();
    await dismissPrivacyNoticeIfPresent(page);

    await expect(page.getByTestId('semantic-preset-select')).toBeVisible({
      timeout: 15_000,
    });
    await page.getByTestId('semantic-preset-select').selectOption(PRESET_ID);
    await expect(page.getByTestId('semantic-preset-select')).toHaveValue(PRESET_ID);

    const editor = page.getByTestId('tac-editor');
    await editor.click();
    await page.keyboard.press(process.platform === 'darwin' ? 'Meta+A' : 'Control+A');
    await page.keyboard.insertText(METAR_TAC);
    await page.getByTestId('convert-button').click();
    await expect.poll(() => captured.convert.length).toBeGreaterThan(0);

    const convertReq = captured.convert[0]!;
    expectBearer(convertReq);
    const form = convertReq.postDataBuffer()?.toString('utf8') ?? '';
    expect(form).toMatch(new RegExp(`name="preset_id"\\r?\\n\\r?\\n${PRESET_ID}`));
    await expect(page.getByText(/Successfully converted 1 file/i)).toBeVisible({
      timeout: 15_000,
    });

    const openBtn = page.getByTestId('open-dissemination-drawer');
    await expect(openBtn).toBeEnabled({ timeout: 15_000 });
    await openBtn.click();
    await expect(page.getByTestId('dissemination-drawer')).toBeVisible();
    await expect(page.getByTestId('dissemination-template-select')).toBeVisible();
    await page.getByTestId('dissemination-template-select').selectOption(TEMPLATE_ID);
    await expect(page.getByTestId('dissemination-template-select')).toHaveValue(
      TEMPLATE_ID,
    );

    await page
      .getByTestId('dissemination-uri-input')
      .fill('sqlite:////tmp/e2e-uj074.db');
    await page.getByTestId('dissemination-file-input').setInputFiles(FIXTURE_TAC);
    await expect(page.getByTestId('dissemination-payload-status')).toContainText(
      /1 candidate/i,
    );
    await expect(page.getByTestId('dissemination-preflight-button')).toBeEnabled();
    await page.getByTestId('dissemination-preflight-button').click();
    await expect.poll(() => captured.preflight.length).toBeGreaterThan(0);
    const preflightBody = captured.preflight[0]!.postDataJSON() as {
      dissemination_template_id?: string;
      uri?: string;
    };
    expect(preflightBody.dissemination_template_id).toBe(TEMPLATE_ID);
    expect(preflightBody.uri).toMatch(/^sqlite:/);
  });
});

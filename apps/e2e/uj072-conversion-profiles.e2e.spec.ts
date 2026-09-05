/**
 * H4–H5 / T2 — Playwright smokes for UJ-072 ConversionProfile editor (EV-933 / #933).
 *
 * Spec: docs/test-plan.md TC-EV933-006; docs/user-journeys.md UJ-072.
 * Auth is seeded via localStorage + stubbed profile APIs so CI does not require live JWT.
 * Live H4–H5 against stage FE is deferred until this PR lands on stage (T3.2).
 */
import { expect, test, type Page, type Request } from '@playwright/test';
import {
  dismissPrivacyNoticeIfPresent,
  openPublicConverter,
} from './playwright-e2e-helpers';

const MOCK_TOKEN = 'e2e-mock-profiles-jwt';
const OVERLAY_ID = '11111111-1111-4111-8111-111111111111';
const METAR_TAC = 'METAR KJFK 121251Z 24016G28KT 3SM -RA BR BKN020 OVC040 14/11 A2990=';
const IWXXM_XML =
  '<?xml version="1.0"?><iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/2025-2"><iwxxm:observation/></iwxxm:METAR>';

type ProfilesCapture = {
  catalog: Request[];
  rulePacksGet: Request[];
  rulePacksPost: Request[];
  overlaysGet: Request[];
  overlaysPost: Request[];
  convert: Request[];
};

type StubProfilesOptions = {
  rulePacks?: ReadonlyArray<Record<string, unknown>>;
  overlays?: ReadonlyArray<Record<string, unknown>>;
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
  await page.route('**/api/v1/lint-issue-catalog**', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ issues: [] }),
    });
  });
}

async function stubProfilesApis(
  page: Page,
  options: StubProfilesOptions = {},
): Promise<ProfilesCapture> {
  const captured: ProfilesCapture = {
    catalog: [],
    rulePacksGet: [],
    rulePacksPost: [],
    overlaysGet: [],
    overlaysPost: [],
    convert: [],
  };
  const rulePacks = options.rulePacks ?? [];
  const overlays = options.overlays ?? [
    {
      id: OVERLAY_ID,
      user_id: '33333333-3333-4333-8333-333333333333',
      slug: 'e2e-overlay',
      baseProfileId: 'ICAO_2025',
      body: {},
      signature: 'a'.repeat(64),
      shared: false,
      created_at: '2026-09-04T00:00:00Z',
      updated_at: '2026-09-04T00:00:00Z',
    },
  ];

  await page.route('**/api/v1/profiles/catalog**', async (route) => {
    captured.catalog.push(route.request());
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
            deltas_vs_icao: [
              'Baseline ICAO/WMO line used for cross-profile comparison.',
            ],
            iwxxm_line: 'IWXXM 2025-2 core',
            rule_pack_count: rulePacks.length,
            overlay_count: overlays.length,
            vendor_pins: { iwxxm: 'WMO IWXXM 2025-2' },
            implementation: {
              input: 'tac2iwxxm/profiles/annex3',
              conversion: 'annex3 emit plugin',
              exchange: 'GLOBAL_AFS default',
            },
          },
          {
            id: 'US_FAA_NWS',
            kind: 'semantic',
            status: 'implemented',
            products: ['METAR'],
            emit_key: 'iwxxm_us',
            deltas_vs_icao: [
              'Retains selected RMK content in output.',
              'Adds FAA/NWS national extension coverage.',
            ],
            iwxxm_line: 'IWXXM-US 3.0.0',
            rule_pack_count: rulePacks.filter((item) => item.profile === 'US_FAA_NWS')
              .length,
            overlay_count: overlays.filter(
              (item) => item.baseProfileId === 'US_FAA_NWS',
            ).length,
            vendor_pins: { iwxxm: 'iwxxm-us 3.0.0' },
            implementation: {
              input: 'tac2iwxxm/profiles/iwxxm_us',
              conversion: 'iwxxm_us emit plugin',
            },
          },
          {
            id: 'CA_ECCC',
            kind: 'semantic',
            status: 'pilot',
            products: ['METAR', 'SPECI', 'TAF', 'AIRMET'],
            emit_key: 'ca_eccc',
            deltas_vs_icao: ['Pins the MSC operational IWXXM line.'],
            iwxxm_line: 'IWXXM 3.0.0 (MSC operational)',
            rule_pack_count: rulePacks.filter((item) => item.profile === 'CA_ECCC')
              .length,
            overlay_count: overlays.filter((item) => item.baseProfileId === 'CA_ECCC')
              .length,
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
    const req = route.request();
    if (req.method() === 'GET') {
      captured.rulePacksGet.push(req);
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: rulePacks }),
      });
      return;
    }
    if (req.method() === 'POST') {
      captured.rulePacksPost.push(req);
      const body = (req.postDataJSON() ?? {}) as Record<string, unknown>;
      await route.fulfill({
        status: 201,
        contentType: 'application/json',
        body: JSON.stringify({
          id: '22222222-2222-4222-8222-222222222222',
          user_id: '33333333-3333-4333-8333-333333333333',
          slug: body.slug ?? 'e2e-pack',
          profile: body.profile ?? 'ICAO_2025',
          product: body.product ?? 'METAR',
          stage: body.stage ?? 'lint',
          severity: body.severity ?? 'warning',
          when: body.when ?? '',
          message: body.message ?? '',
          standardReference: body.standardReference ?? '',
          created_at: '2026-09-04T00:00:00Z',
          updated_at: '2026-09-04T00:00:00Z',
        }),
      });
      return;
    }
    await route.fallback();
  });

  await page.route('**/api/v1/profiles/overlays**', async (route) => {
    const req = route.request();
    if (req.method() === 'GET') {
      captured.overlaysGet.push(req);
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: overlays }),
      });
      return;
    }
    if (req.method() === 'POST') {
      captured.overlaysPost.push(req);
      const body = (req.postDataJSON() ?? {}) as Record<string, unknown>;
      await route.fulfill({
        status: 201,
        contentType: 'application/json',
        body: JSON.stringify({
          id: OVERLAY_ID,
          user_id: '33333333-3333-4333-8333-333333333333',
          slug: body.slug ?? 'e2e-overlay',
          baseProfileId: body.baseProfileId ?? 'ICAO_2025',
          body: body.body ?? {},
          signature: 'b'.repeat(64),
          shared: false,
          created_at: '2026-09-04T00:00:00Z',
          updated_at: '2026-09-04T00:00:00Z',
        }),
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
          },
        ],
        errors: [],
        issues: [],
        failed_spans: [],
        total_processed: 1,
        successful: 1,
        metadata: {
          overlay_id: OVERLAY_ID,
          overlay_base_profile: 'ICAO_2025',
        },
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

test.describe('UJ-072: ConversionProfile editor (EV-933 / TC-EV933-006)', () => {
  test('guest: Conversion profiles prompts for sign-in', async ({ page }) => {
    await openProfiles(page);
    await expect(page.getByTestId('conversion-profiles-sign-in')).toBeVisible();
    await expect(page.getByTestId('conversion-profiles-page')).toContainText(
      /Sign in to open the conversion profiles editor/i,
    );
    await expect(page.getByTestId('conversion-profiles-inspector')).toHaveCount(0);
  });

  test('TC-EV933-006: inspect catalog, save pack + overlay, convert with overlay_id', async ({
    page,
  }) => {
    await seedMockAuth(page);
    await stubWorkbenchNoise(page);
    const captured = await stubProfilesApis(page);

    await openProfiles(page);

    await expect(page.getByTestId('conversion-profiles-inspector')).toBeVisible();
    await expect(
      page.getByTestId('conversion-profiles-inspector-detail'),
    ).toBeVisible();
    await expect(page.getByTestId('conversion-profiles-select')).toHaveValue(
      'ICAO_2025',
    );
    expect(captured.catalog.length).toBeGreaterThan(0);
    expectBearer(captured.catalog[0]!);

    await page.getByTestId('conversion-profiles-select').selectOption('US_FAA_NWS');
    await expect(page.getByTestId('conversion-profiles-select')).toHaveValue(
      'US_FAA_NWS',
    );

    await page.getByTestId('conversion-profiles-pack-slug').fill('e2e-pack');
    await page.getByTestId('conversion-profiles-pack-profile').fill('ICAO_2025');
    await page.getByTestId('conversion-profiles-pack-product').fill('METAR');
    await page.getByTestId('conversion-profiles-pack-stage').fill('lint');
    await page.getByTestId('conversion-profiles-pack-severity').fill('warning');
    await page.getByTestId('conversion-profiles-pack-message').fill('soft lint');
    await page.getByTestId('conversion-profiles-pack-save').click();
    await expect.poll(() => captured.rulePacksPost.length).toBe(1);
    expectBearer(captured.rulePacksPost[0]!);
    const packBody = captured.rulePacksPost[0]!.postDataJSON() as {
      slug?: string;
      profile?: string;
    };
    expect(packBody.slug).toBe('e2e-pack');
    expect(packBody.profile).toBe('ICAO_2025');

    await page.getByTestId('conversion-profiles-overlay-slug').fill('e2e-overlay');
    await page.getByTestId('conversion-profiles-overlay-base').fill('ICAO_2025');
    await page.getByTestId('conversion-profiles-overlay-body').fill('{"lint":true}');
    await page.getByTestId('conversion-profiles-overlay-save').click();
    await expect.poll(() => captured.overlaysPost.length).toBe(1);
    expectBearer(captured.overlaysPost[0]!);

    await page.getByTestId('shell-nav-converter').click();
    await expect(
      page.getByRole('heading', { name: /METAR.*IWXXM.*Converter/i }),
    ).toBeVisible();
    await dismissPrivacyNoticeIfPresent(page);

    const profile = page.getByTestId('profile-type-select');
    await expect(profile).toBeVisible();
    await expect(page.getByTestId('exchange-profile-select')).toBeVisible();
    await expect(page.getByTestId('signed-overlay-select')).toBeVisible();
    await page.getByTestId('signed-overlay-select').selectOption(OVERLAY_ID);

    const editor = page.getByTestId('tac-editor');
    await editor.click();
    await page.keyboard.press(process.platform === 'darwin' ? 'Meta+A' : 'Control+A');
    await page.keyboard.insertText(METAR_TAC);
    await page.getByTestId('convert-button').click();
    await expect.poll(() => captured.convert.length).toBeGreaterThan(0);

    const convertReq = captured.convert[0]!;
    expectBearer(convertReq);
    const form = convertReq.postDataBuffer()?.toString('utf8') ?? '';
    expect(form).toMatch(
      /name="overlay_id"\r?\n\r?\n11111111-1111-4111-8111-111111111111/,
    );
  });

  test('TC-EV933-006 regression: #1024 pickers + dissemination drawer still work', async ({
    page,
  }) => {
    await seedMockAuth(page);
    await stubWorkbenchNoise(page);
    await stubProfilesApis(page);

    await openPublicConverter(page);
    await expect(page.getByTestId('profile-type-select')).toBeVisible();
    await expect(page.getByTestId('exchange-profile-select')).toBeVisible();
    await page.getByTestId('profile-type-select').selectOption('AU_BOM');
    await page.getByTestId('exchange-profile-select').selectOption('APAC_ROBEX');
    await expect(page.getByTestId('profile-type-select')).toHaveValue('AU_BOM');
    await expect(page.getByTestId('exchange-profile-select')).toHaveValue('APAC_ROBEX');

    const openBtn = page.getByTestId('open-dissemination-drawer');
    await expect(openBtn).toBeEnabled({ timeout: 15_000 });
    await openBtn.click();
    await expect(page.getByTestId('dissemination-drawer')).toBeVisible();
    await expect(page.getByTestId('dissemination-exchange-profile')).toBeVisible();
  });

  test('TC-EV1120-010/012/014/017: summary, compare, blocks, and starter sync', async ({
    page,
  }) => {
    await seedMockAuth(page);
    await stubWorkbenchNoise(page);
    await stubProfilesApis(page, { rulePacks: [], overlays: [] });

    await openProfiles(page);

    await expect(page.getByTestId('conversion-profiles-summary')).toBeVisible();
    await expect(page.getByTestId('conversion-profiles-summary-primary')).toContainText(
      /ICAO_2025/i,
    );
    await page
      .getByTestId('conversion-profiles-compare-select')
      .selectOption('US_FAA_NWS');
    await expect(page.getByTestId('conversion-profiles-summary-compare')).toContainText(
      /US_FAA_NWS/i,
    );
    await expect(page.getByText(/Different from US_FAA_NWS/i).first()).toBeVisible();

    await page.getByTestId('conversion-profiles-block-output-validation').click();
    await expect(page.getByTestId('conversion-profiles-block-detail')).toContainText(
      /WMO IWXXM 2025-2/i,
    );
    await expect(
      page.getByTestId('conversion-profiles-block-jump-packs'),
    ).toHaveAttribute('href', '#conversion-profiles-packs');

    await page.getByTestId('conversion-profiles-select').selectOption('US_FAA_NWS');
    await expect(page.getByTestId('conversion-profiles-pack-profile')).toHaveValue(
      'US_FAA_NWS',
    );
    await expect(page.getByTestId('conversion-profiles-overlay-base')).toHaveValue(
      'US_FAA_NWS',
    );
    await page.getByTestId('conversion-profiles-pack-slug').fill('custom-pack');
    await page.getByTestId('conversion-profiles-select').selectOption('CA_ECCC');
    await expect(page.getByTestId('conversion-profiles-pack-slug')).toHaveValue(
      'custom-pack',
    );
    await expect(page.getByTestId('conversion-profiles-pack-profile')).toHaveValue(
      'US_FAA_NWS',
    );
  });

  test('TC-EV1120-011/013/015: workbench twin and profile-aware example refresh', async ({
    page,
  }) => {
    await seedMockAuth(page);
    await stubWorkbenchNoise(page);
    await stubProfilesApis(page);

    await openPublicConverter(page);
    await dismissPrivacyNoticeIfPresent(page);

    await expect(page.getByTestId('workbench-profile-summary')).toBeVisible();
    await expect(page.getByTestId('workbench-profile-summary')).toContainText(
      /ICAO_2025/i,
    );

    await page.getByTestId('profile-type-select').selectOption('US_FAA_NWS');
    await expect(page.getByTestId('workbench-profile-summary')).toContainText(
      /US_FAA_NWS/i,
    );
    await page.getByTestId('examples-select').click();
    await expect(
      page.getByRole('option', {
        name: /METAR WMO A3-1 \(annex3\).*Reused for United States \(FAA\/NWS\)/i,
      }),
    ).toBeVisible();
    await expect(
      page.getByRole('option', { name: /TC SIGMET WMO A6-2-TC/i }),
    ).toHaveCount(0);
  });
});

/**
 * EV-bridge T2 / H4–H5 — UJ-072g five Libraries + Mapping bridge + hard cut.
 *
 * Spec: docs/test-plan.md TC-EVBRIDGE-005..007, 010; docs/user-journeys.md UJ-072g.
 * [Corpus: product §F7.w] [Corpus: journeys] [Corpus: tests] [Corpus: adr/ADR-043]
 */
import { expect, test, type Page } from '@playwright/test';
import {
  dismissPrivacyNoticeIfPresent,
  openPublicConverter,
} from './playwright-e2e-helpers';

const MOCK_TOKEN = 'e2e-mock-bridge-jwt';
const METAR_TAC = 'METAR KJFK 121251Z 24016G28KT 3SM -RA BR BKN020 OVC040 14/11 A2990=';

async function seedMockAuth(page: Page): Promise<void> {
  await page.addInitScript((token) => {
    const expiresAt = String(Math.floor(Date.now() / 1000) + 3600);
    localStorage.setItem('access_token', token);
    localStorage.setItem('refresh_token', 'e2e-mock-refresh');
    localStorage.setItem('expires_at', expiresAt);
  }, MOCK_TOKEN);
}

async function stubLibraryNoise(page: Page): Promise<void> {
  await page.route('**/api/v1/library-assets**', async (route) => {
    const url = new URL(route.request().url());
    const kind = url.searchParams.get('kind') || 'conversion';
    const line = 'ICAO_2025';
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        items: [
          {
            id: `LIB.${kind.toUpperCase()}.${line}`,
            kind,
            name: `${kind} · ${line}`,
            access: 'first_party',
            engine_profile_id: line,
            attached_national_line: line,
            body:
              kind === 'dissemination'
                ? {
                    transforms: [
                      { id: 'envelope', type: 'envelope' },
                      { id: 'checksum', type: 'checksum' },
                    ],
                  }
                : kind === 'decoding'
                  ? {
                      seed: 'decode_tac',
                      entries: [{ token: 'TS', explanation: 'thunderstorm' }],
                    }
                  : { rules: [] },
          },
          {
            id: `LIB.${kind.toUpperCase()}.US_FAA_NWS`,
            kind,
            name: `${kind} · US_FAA_NWS`,
            access: 'first_party',
            engine_profile_id: 'US_FAA_NWS',
            attached_national_line: 'US_FAA_NWS',
            body: {},
          },
        ],
      }),
    });
  });
  await page.route('**/api/v1/conversion-templates**', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        items: [
          {
            id: 'CV.WIND',
            name: 'Wind group',
            access: 'first_party',
            iwxxm_block: 'iwxxm:WindObservation',
            slots: [],
            sample: '18012G20KT',
          },
        ],
      }),
    });
  });
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
        summary: 'Stub',
      }),
    });
  });
}

test.describe('EV-bridge — UJ-072g Libraries + hard cut', () => {
  test('TC-EVBRIDGE-007: five Convert library pickers + Beta; hard-cut FormData', async ({
    page,
  }) => {
    let postedConversionLibrary: string | null = null;
    let postedSemantic: string | null = null;
    await page.route('**/api/v1/convert', async (route) => {
      const body = route.request().postDataBuffer();
      if (body) {
        const text = body.toString('utf8');
        postedConversionLibrary =
          /name="conversion_library_id"\r?\n\r?\n([^\r\n]+)/.exec(text)?.[1] ?? null;
        postedSemantic =
          /name="semantic_profile"\r?\n\r?\n([^\r\n]+)/.exec(text)?.[1] ?? null;
      }
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          results: [
            {
              name: 'manual',
              content: '<iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/2025-2"/>',
              original_content: METAR_TAC,
            },
          ],
          errors: [],
          total_processed: 1,
          successful: 1,
          failed: 0,
        }),
      });
    });

    await openPublicConverter(page);
    await page.getByLabel(/Expand parameters/i).click();
    await expect(page.getByTestId('library-pickers-bar')).toBeVisible();
    await expect(page.getByTestId('conversion-library-select')).toBeVisible();
    await expect(page.getByTestId('tac-validation-library-select')).toBeVisible();
    await expect(page.getByTestId('iwxxm-validation-library-select')).toBeVisible();
    await expect(page.getByTestId('dissemination-library-select')).toBeVisible();
    await expect(page.getByTestId('decoding-library-select')).toBeVisible();
    await expect(page.getByTestId('profile-type-select')).toHaveCount(0);
    await expect(page.getByTestId('exchange-profile-select')).toHaveCount(0);
    await expect(
      page.getByTestId('library-pickers-bar').getByTestId('beta-badge'),
    ).toBeVisible();

    await page
      .getByTestId('conversion-library-select')
      .selectOption('LIB.CONVERSION.US_FAA_NWS');

    const editor = page.getByTestId('tac-editor');
    await editor.click();
    await page.keyboard.press(process.platform === 'darwin' ? 'Meta+A' : 'Control+A');
    await page.keyboard.insertText(METAR_TAC);
    await page.getByTestId('convert-button').click();
    await expect(page.getByRole('region', { name: /conversion results/i })).toBeVisible(
      {
        timeout: 30_000,
      },
    );
    expect(postedConversionLibrary).toBe('LIB.CONVERSION.US_FAA_NWS');
    expect(postedSemantic).toBeNull();
  });

  test('TC-EVBRIDGE-005/006/010: Profile Libraries tabs + Mapping bridge Beta', async ({
    page,
  }) => {
    await seedMockAuth(page);
    await stubLibraryNoise(page);
    await page.goto('/profiles');
    await dismissPrivacyNoticeIfPresent(page);

    await expect(page.getByTestId('conversion-profiles-page')).toBeVisible({
      timeout: 30_000,
    });
    const libraries = page.getByTestId('profile-builder-libraries');
    await expect(libraries).toBeVisible();
    await expect(libraries.getByTestId('beta-badge')).toBeVisible();
    await expect(page.getByTestId('profile-library-tab-conversion')).toBeVisible();
    await expect(page.getByTestId('profile-library-tab-tac-validation')).toBeVisible();
    await expect(
      page.getByTestId('profile-library-tab-iwxxm-validation'),
    ).toBeVisible();
    await expect(page.getByTestId('profile-library-tab-dissemination')).toBeVisible();
    await expect(page.getByTestId('profile-library-tab-decoding')).toBeVisible();

    await page.getByTestId('profile-library-tab-dissemination').click();
    await expect(page.getByTestId('library-assets-panel-dissemination')).toBeVisible();
    await expect(page.getByTestId('dissemination-transforms-list')).toBeVisible();

    await page.getByTestId('profile-library-tab-decoding').click();
    await expect(page.getByTestId('library-assets-panel-decoding')).toBeVisible();
    await expect(page.getByTestId('decoding-entries-list')).toBeVisible();

    await page.getByTestId('profile-library-tab-conversion').click();
    await expect(page.getByTestId('conversion-templates-panel')).toBeVisible();
    await expect(page.getByTestId('mapping-bridge')).toBeVisible();
    await expect(
      page.getByTestId('mapping-bridge').getByTestId('beta-badge'),
    ).toBeVisible();
  });
});

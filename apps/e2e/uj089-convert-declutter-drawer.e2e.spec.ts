/**
 * UJ-089 — Convert declutter results drawer + Settings cog (H4–H5).
 *
 * Spec: docs/user-journeys.md UJ-089; docs/test-plan.md TC-UX-DECLUTTER-*.
 * [Corpus: product §F7] [Corpus: journeys §UJ-089] [Corpus: tests]
 */
import { expect, test, type Page } from '@playwright/test';
import { convertManualMetar, openConverterForE2e } from './playwright-e2e-helpers';

const METAR_TAC = 'METAR KJFK 121251Z 24016G28KT 3SM -RA BR BKN020 OVC040 14/11 A2990=';

async function stubConvertApis(page: Page): Promise<void> {
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
        summary: 'METAR',
      }),
    });
  });
  await page.route('**/api/v1/convert', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        results: [
          {
            name: 'manual_input.txt',
            content: '<iwxxm:METAR>mock-success</iwxxm:METAR>',
            tac_input: METAR_TAC,
            source: 'manual_input',
            size_bytes: 39,
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
}

test.describe('UJ-089 — Convert results drawer declutter', () => {
  test('drawer tabs, Settings cog, no Compare versions after convert', async ({
    page,
  }) => {
    await stubConvertApis(page);
    await openConverterForE2e(page);

    await convertManualMetar(page, METAR_TAC);

    const drawer = page.getByTestId('convert-results-drawer');
    await expect(drawer).toBeVisible({ timeout: 15_000 });
    await expect(drawer).toHaveAttribute('data-open', 'true');
    await expect(page.getByTestId('convert-results-tab-iwxxm')).toBeVisible();
    await expect(page.getByTestId('convert-results-tab-console')).toBeVisible();
    await expect(page.getByTestId('convert-results-tab-decoder')).toBeVisible();
    await expect(page.getByTestId('convert-results-tab-map')).toBeVisible();
    await expect(page.getByTestId('convert-results-tab-downloads')).toBeVisible();

    await page.getByTestId('convert-results-tab-downloads').click();
    await expect(page.getByTestId('convert-downloads-panel')).toBeVisible();

    await expect(page.getByTestId('convert-settings-cog')).toHaveAttribute(
      'aria-label',
      'Settings',
    );
    await expect(page.getByLabel(/Compare versions/i)).toHaveCount(0);
  });
});

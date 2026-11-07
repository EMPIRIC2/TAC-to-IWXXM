/**
 * UJ-088 — Calmer Convert empty → Help checklist + CTA choreography (H4–H5).
 *
 * Spec: docs/user-journeys.md UJ-088; docs/test-plan.md TC-UX-CALM-*; F7 deepen.
 * [Corpus: product §F7] [Corpus: journeys §UJ-088] [Corpus: tests]
 * UX-2026-11-07: empty state uses bordered converter chrome (no marketing hero).
 */
import { expect, test, type Page } from '@playwright/test';
import {
  convertManualMetar,
  openConvertDownloadsTab,
  openPublicConverter,
} from './playwright-e2e-helpers';

const METAR_TAC = 'METAR KJFK 121251Z 24016G28KT 3SM -RA BR BKN020 OVC040 14/11 A2990=';

async function stubCalmConvertApis(page: Page): Promise<void> {
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
        segments: [
          {
            start: 0,
            end: 5,
            code: 'METAR',
            explanation: 'Report type',
          },
        ],
        residuals: [],
        summary: 'METAR at KJFK',
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

test.describe('UJ-088 — Calmer Convert + Help checklist', () => {
  test('converter chrome, Help checklist, convert → Download + results drawer', async ({
    page,
  }) => {
    await stubCalmConvertApis(page);
    await openPublicConverter(page);

    // Opposite state: convert-empty-hero can match if the marketing hero returns.
    await expect(page.getByTestId('convert-empty-hero')).toHaveCount(0);
    await expect(page.getByTestId('convert-shell')).toBeVisible({
      timeout: 15_000,
    });
    await expect(page.getByTestId('product-type-select')).toBeVisible();
    await expect(page.getByTestId('convert-help-open')).toBeVisible();

    // G4 — profile Change opens drawer; Apply dismisses (TC-UX-CALM-005 H4–H5).
    await page.getByTestId('convert-settings-cog').click();
    await page.getByTestId('convert-profile-change-live').click();
    await expect(page.getByTestId('convert-profile-drawer')).toBeVisible();
    await page.getByTestId('convert-profile-apply').click();
    // Opposite state: drawer visible before Apply.
    await expect(page.getByTestId('convert-profile-drawer')).toHaveCount(0);

    await page.getByTestId('convert-help-open').click();
    await expect(page.getByTestId('convert-help-checklist')).toBeVisible();
    await expect(page.getByTestId('operator-help-link')).toBeVisible();
    await page.keyboard.press('Escape');
    // Opposite state: checklist visible before Escape.
    await expect(page.getByTestId('convert-help-checklist')).toHaveCount(0);

    await page.getByTestId('convert-help-open').click();
    await expect(page.getByTestId('convert-help-checklist')).toBeVisible();
    await page.keyboard.press('Escape');
    // Opposite state: checklist visible before the second Escape.
    await expect(page.getByTestId('convert-help-checklist')).toHaveCount(0);

    await expect(page.getByTestId('convert-button')).toBeVisible();

    await convertManualMetar(page, METAR_TAC);
    await openConvertDownloadsTab(page, 15_000);
    // Opposite state: empty hero remains absent after convert.
    await expect(page.getByTestId('convert-empty-hero')).toHaveCount(0);
    await expect(page.getByTestId('convert-results-drawer')).toBeVisible();
    await expect(page.getByTestId('convert-results-tab-iwxxm')).toBeVisible();
    await expect(
      page.getByRole('button', { name: 'Download latest', exact: true }),
    ).toBeVisible();
    // G2 — TC-UX-CALM-006: TAC locked until Edit.
    await expect(page.getByTestId('convert-tac-readonly')).toBeVisible();
    await expect(page.getByTestId('convert-tac-edit')).toBeVisible();
    await page.getByTestId('convert-tac-edit').click();
    await expect(page.getByTestId('convert-tac-editable')).toBeVisible();
  });
});

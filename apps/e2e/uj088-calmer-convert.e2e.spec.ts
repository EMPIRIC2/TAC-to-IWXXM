/**
 * UJ-088 — Calmer Convert empty → Help checklist + CTA choreography (H4–H5).
 *
 * Spec: docs/user-journeys.md UJ-088; docs/test-plan.md TC-UX-CALM-*; F7 deepen.
 * [Corpus: product §F7] [Corpus: journeys §UJ-088] [Corpus: tests]
 */
import { expect, test, type Page } from '@playwright/test';
import { convertManualMetar, openConverterForE2e } from './playwright-e2e-helpers';

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
  test('empty hero, Help checklist, convert → Download + validity strip', async ({
    page,
  }) => {
    await stubCalmConvertApis(page);
    await openConverterForE2e(page);

    await expect(page.getByTestId('convert-empty-hero')).toBeVisible({
      timeout: 15_000,
    });
    await expect(page.getByTestId('convert-example-chips')).toBeVisible();
    await expect(page.getByTestId('convert-help-open')).toBeVisible();

    await page.getByTestId('convert-help-open').click();
    await expect(page.getByTestId('convert-help-checklist')).toBeVisible();
    await expect(page.getByTestId('operator-help-link')).toBeVisible();
    await page.keyboard.press('Escape');
    // Opposite state: the checklist dialog is visible before Escape.
    await expect(page.getByTestId('convert-help-checklist')).toHaveCount(0);

    await page.getByTestId('convert-help-open').click();
    await expect(page.getByTestId('convert-help-checklist')).toBeVisible();
    await page.keyboard.press('Escape');
    // Opposite state: the checklist dialog is visible before the second Escape.
    await expect(page.getByTestId('convert-help-checklist')).toHaveCount(0);

    await convertManualMetar(page, METAR_TAC);

    await expect(
      page.getByRole('region', { name: 'Conversion results', exact: true }),
    ).toBeVisible({ timeout: 15_000 });
    // Opposite state: the empty hero is visible before convert fills TAC.
    await expect(page.getByTestId('convert-empty-hero')).toHaveCount(0);
    await expect(page.getByTestId('convert-validity-strip')).toBeVisible();
    await expect(
      page.getByRole('button', { name: 'Download IWXXM', exact: true }),
    ).toBeVisible();
    await expect(page.getByTestId('convert-tac-edit')).toBeVisible();
  });
});

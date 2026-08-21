/**
 * UJ-057 / TC-EV057-903-006 — Accumulate conversions → Download ZIP.
 *
 * Local T2 smoke. Live H4–H5 remains stage 13 after staging deploy.
 * Spec: docs/user-journeys.md UJ-057; docs/test-plan.md TC-EV057-903-*.
 */
import { expect, test } from '@playwright/test';
import {
  convertManualMetar,
  dismissPrivacyNoticeIfPresent,
  openPublicConverter,
} from './playwright-e2e-helpers';

const TAC_A = 'METAR KJFK 011200Z 18012KT 10SM FEW030 15/07 A3005=';
const TAC_B = 'METAR KLAX 011300Z 25008KT 10SM SCT040 20/12 A2990=';

test.describe('UJ-057: Accumulate conversions → Download ZIP (TC-EV057-903)', () => {
  test('two converts accumulate; Download ZIP enabled; Clear empties', async ({
    page,
  }) => {
    await openPublicConverter(page);
    await dismissPrivacyNoticeIfPresent(page);

    const product = page.locator('#param-product');
    if (!(await product.isVisible().catch(() => false))) {
      await page
        .getByLabel(/Expand parameters/i)
        .click()
        .catch(() => undefined);
    }
    await page.locator('#param-product').selectOption('METAR');

    await convertManualMetar(page, TAC_A);
    await expect(page.getByRole('region', { name: /conversion results/i })).toBeVisible(
      {
        timeout: 30_000,
      },
    );
    await expect(page.getByTestId('download-zip-button')).toHaveAccessibleName(
      /download all 1 converted files as zip/i,
    );

    await convertManualMetar(page, TAC_B);
    await expect(page.getByTestId('download-zip-button')).toHaveAccessibleName(
      /download all 2 converted files as zip/i,
      { timeout: 30_000 },
    );

    const downloadPromise = page.waitForEvent('download');
    await page.getByTestId('download-zip-button').click();
    const download = await downloadPromise;
    expect(download.suggestedFilename()).toMatch(/^METARKJF_\d{14}\.zip$/);

    await page.getByTestId('clear-queue-button').click();
    await expect(page.getByRole('region', { name: /conversion results/i })).toHaveCount(
      0,
    );
  });
});

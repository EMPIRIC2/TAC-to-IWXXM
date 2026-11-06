/**
 * UJ-079: a SIGMET that names SRQ converts through the public lookup.
 */
import { expect, test } from '@playwright/test';
import {
  convertManualMetar,
  fillManualTac,
  openConvertIwxxmTab,
  openConvertSettings,
  openConverterForE2e,
} from './playwright-e2e-helpers';

const SRQ_TAC =
  'YUDD SIGMET 6 VALID 101200/101600 YUSO-\n' +
  'YUDD SHANLON FIR/UIR SEV ICE FCST FROM SRQ MOV NE 30KT NC=';

test.describe('UJ-079 reference lookup', () => {
  test('SIGMET SRQ converts to a coordinate from the public source', async ({
    page,
  }) => {
    await openConverterForE2e(page);
    // Product / library live in Settings; seed TAC so the shell is open.
    await fillManualTac(page, 'SIGMET');
    await openConvertSettings(page);
    await expect(page.getByTestId('convert-setup')).toBeVisible();
    await page.locator('#param-product').selectOption('SIGMET');
    await page.getByTestId('convert-advanced-engines').locator('summary').click();
    await page
      .getByTestId('conversion-library-select')
      .selectOption('LIB.CONVERSION.US_FAA_NWS');
    await page.getByLabel('Expand parameters', { exact: true }).click();
    await page.locator('#param-iwxxm-version').selectOption('2025-2');

    await convertManualMetar(page, SRQ_TAC);

    await openConvertIwxxmTab(page, 30_000);
    await expect(page.getByTestId('iwxxm-preview-xml')).toContainText('27.3978');
  });
});

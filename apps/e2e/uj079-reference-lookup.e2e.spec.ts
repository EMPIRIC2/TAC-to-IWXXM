/**
 * UJ-079: a SIGMET that names SRQ converts through the public lookup.
 */
import { expect, test } from '@playwright/test';
import { convertManualMetar, openConverterForE2e } from './playwright-e2e-helpers';

const SRQ_TAC =
  'YUDD SIGMET 6 VALID 101200/101600 YUSO-\n' +
  'YUDD SHANLON FIR/UIR SEV ICE FCST FROM SRQ MOV NE 30KT NC=';

test.describe('UJ-079 reference lookup', () => {
  test('SIGMET SRQ converts to a coordinate from the public source', async ({
    page,
  }) => {
    await openConverterForE2e(page);
    await page.getByLabel(/Expand parameters/i).click();
    await page.locator('#param-product').selectOption('SIGMET');
    await page
      .getByTestId('conversion-library-select')
      .selectOption('LIB.CONVERSION.US_FAA_NWS');
    await page.locator('#param-iwxxm-version').selectOption('2025-2');

    await convertManualMetar(page, SRQ_TAC);

    const xmlOutput = page.locator('pre').filter({ hasText: /iwxxm/i }).first();
    await expect(xmlOutput).toBeVisible({ timeout: 30000 });
    await expect(xmlOutput).toContainText('27.3978');
  });
});

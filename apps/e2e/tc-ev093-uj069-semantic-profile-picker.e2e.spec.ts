/**
 * EV-bridge T3 / H4–H5 — Convert library pickers (replaces EV-093 semantic/exchange chrome).
 *
 * Spec: docs/test-plan.md TC-EVBRIDGE-007; docs/user-journeys.md UJ-072g / UJ-069 deepen.
 * [Corpus: product §F7.w] [Corpus: journeys] [Corpus: tests]
 */
import { expect, test } from '@playwright/test';
import { openPublicConverter } from './playwright-e2e-helpers';

const AHL_WELL_FORMED = `SAUS31 KZNY 121200
METAR KJFK 121151Z 18008KT 10SM FEW250 22/14 A3012=
`;

test.describe('EV-bridge — Convert library pickers (AHL)', () => {
  test('TC-EVBRIDGE-007: Conversion + Dissemination library ids on AHL convert', async ({
    page,
  }) => {
    let postedConversion: string | null = null;
    let postedDissem: string | null = null;
    let postedSemantic: string | null = null;
    await page.route('**/api/v1/convert-bulletin', async (route) => {
      const body = route.request().postDataBuffer();
      if (body) {
        const text = body.toString('utf8');
        postedConversion =
          /name="conversion_library_id"\r?\n\r?\n([^\r\n]+)/.exec(text)?.[1] ?? null;
        postedDissem =
          /name="dissemination_library_id"\r?\n\r?\n([^\r\n]+)/.exec(text)?.[1] ?? null;
        postedSemantic =
          /name="semantic_profile"\r?\n\r?\n([^\r\n]+)/.exec(text)?.[1] ?? null;
      }
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          bulletin_meta: {
            ahl: 'SAUS31 KZNY 121200',
            report_count: 1,
            cccc: 'KZNY',
            yygggg: '121200',
          },
          exchange_profile: 'GLOBAL_AFS',
          results: [
            {
              report_index: 0,
              ok: true,
              tac_input: 'METAR KJFK 121151Z 18008KT 10SM FEW250 22/14 A3012=',
              xml: '<collect:MeteorologicalBulletin xmlns:collect="http://icao.int/iwxxm/collect/2025-2"/>',
              issues: [],
              fixes: [],
            },
          ],
        }),
      });
    });

    await openPublicConverter(page);
    await page.getByLabel(/Expand parameters/i).click();
    await expect(page.getByTestId('library-pickers-bar')).toBeVisible();
    await expect(page.getByTestId('profile-type-select')).toHaveCount(0);
    await expect(page.getByTestId('exchange-profile-select')).toHaveCount(0);

    await page
      .getByTestId('conversion-library-select')
      .selectOption('LIB.CONVERSION.US_FAA_NWS');
    await page
      .getByTestId('dissemination-library-select')
      .selectOption('LIB.DISSEMINATION.US_FAA_NWS');

    await page.getByTestId('input-mode-ahl_bulletin').click();
    const editor = page.getByTestId('tac-editor');
    await editor.click();
    await page.keyboard.press(process.platform === 'darwin' ? 'Meta+A' : 'Control+A');
    await page.keyboard.insertText(AHL_WELL_FORMED);
    await page.getByTestId('convert-button').click();
    await expect(page.getByText(/bulletin:/i)).toBeVisible({ timeout: 60_000 });
    expect(postedConversion).toBe('LIB.CONVERSION.US_FAA_NWS');
    expect(postedDissem).toBe('LIB.DISSEMINATION.US_FAA_NWS');
    expect(postedSemantic).toBeNull();
  });
});

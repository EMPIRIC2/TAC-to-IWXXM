/**
 * EV-093 T3 / H4–H5 — UJ-069 semantic + exchange profile light pickers (#1024).
 *
 * Spec: docs/test-plan.md TC-EV093-006; docs/user-journeys.md UJ-069.
 * [Corpus: product §F7] [Corpus: product §F36] [Corpus: journeys] [Corpus: tests]
 */
import { expect, test } from '@playwright/test';
import { openPublicConverter } from './playwright-e2e-helpers';

const AHL_WELL_FORMED = `SAUS31 KZNY 121200
METAR KJFK 121151Z 18008KT 10SM FEW250 22/14 A3012=
`;

test.describe('EV-093 — UJ-069 semantic + exchange profile pickers', () => {
  test('TC-EV093-006: canonical Profile + Exchange on AHL convert', async ({
    page,
  }) => {
    let postedSemantic: string | null = null;
    let postedExchange: string | null = null;
    await page.route('**/api/v1/convert-bulletin', async (route) => {
      const body = route.request().postDataBuffer();
      if (body) {
        const text = body.toString('utf8');
        postedSemantic =
          /name="semantic_profile"\r?\n\r?\n([^\r\n]+)/.exec(text)?.[1] ?? null;
        postedExchange =
          /name="exchange_profile"\r?\n\r?\n([^\r\n]+)/.exec(text)?.[1] ?? null;
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
          exchange_profile: postedExchange || 'APAC_ROBEX',
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
    const profile = page.getByTestId('profile-type-select');
    await expect(profile).toBeVisible();
    await expect(page.getByTestId('product-profile-bar-summary')).toBeVisible();
    await page.getByTestId('product-profile-trust-details').locator('summary').click();
    await expect(page.getByTestId('semantic-profile-help')).toBeVisible();
    await profile.selectOption('AU_BOM');
    const exchange = page.getByTestId('exchange-profile-select');
    await expect(exchange).toBeVisible();
    await exchange.selectOption('APAC_ROBEX');
    await page.getByTestId('input-mode-ahl_bulletin').click();
    const editor = page.getByTestId('tac-editor');
    await editor.click();
    await page.keyboard.press(process.platform === 'darwin' ? 'Meta+A' : 'Control+A');
    await page.keyboard.insertText(AHL_WELL_FORMED);
    await page.getByTestId('convert-button').click();
    await expect(page.getByText(/bulletin:/i)).toBeVisible({ timeout: 60_000 });
    expect(postedSemantic).toBe('AU_BOM');
    expect(postedExchange).toBe('APAC_ROBEX');
  });
});

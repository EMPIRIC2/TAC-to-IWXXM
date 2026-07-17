/**
 * T3.7 / TC-F9-002 + TC-F10-001/002 — UJ-020/021 live decode + preview UX (S013 / EV-009).
 */
import { expect, test } from '@playwright/test';
import { openConverterForE2e } from './playwright-e2e-helpers';

const METAR_NO_EQ = 'METAR KJFK 121251Z 18004KT 10SM FEW250 24/18 A3011';
const SUMMARY =
  'Report type (routine meteorological aerodrome report); station KJFK; from 180° at 4 kt; Temperature 24 °C, dewpoint 18 °C.';

async function stubF9F10Apis(page: import('@playwright/test').Page): Promise<void> {
  await page.route('**/api/v1/lint-tac', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        ok: true,
        issues: [
          {
            severity: 'info',
            code: 'MISSING_TERMINATOR',
            message: "Reports in bulletins end with '=' — add it before publishing",
            start: Math.max(0, METAR_NO_EQ.length - 1),
            end: METAR_NO_EQ.length,
          },
        ],
        fixes: [
          {
            code: 'add_terminator',
            message: "Add '='",
            replacement: `${METAR_NO_EQ}=`,
          },
        ],
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
            explanation: 'Report type (routine meteorological aerodrome report)',
          },
          {
            start: 6,
            end: 10,
            code: 'KJFK',
            explanation: 'ICAO station location indicator',
          },
        ],
        residuals: [],
        summary: SUMMARY,
      }),
    });
  });

  await page.route('**/api/v1/convert', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        ok: true,
        results: [
          {
            name: 'manual.metar',
            iwxxm_xml:
              '<?xml version="1.0"?><iwxxm:METAR><iwxxm:observation/></iwxxm:METAR>',
            tac_input: METAR_NO_EQ,
          },
        ],
        errors: [],
        issues: [],
        failed_spans: [],
        total_processed: 1,
        successful: 1,
      }),
    });
  });
}

test.describe('T3.7 / UJ-020 + UJ-021: live decode summary + preview UX', () => {
  test('UJ-020: typing updates Plain language summary without refresh', async ({
    page,
  }) => {
    await stubF9F10Apis(page);
    await openConverterForE2e(page);

    const editor = page.getByLabel(/Enter METAR data manually/i);
    await editor.click();
    await editor.fill(METAR_NO_EQ);

    await expect(page.getByTestId('decode-plain-language')).toBeVisible({
      timeout: 5000,
    });
    await expect(page.getByTestId('decode-plain-language')).toContainText(
      /KJFK|180°|24 °C/i,
    );
  });

  test('UJ-021: preview pane mounts; Add = quick fix appends terminator', async ({
    page,
  }) => {
    await stubF9F10Apis(page);
    await openConverterForE2e(page);

    await expect(page.getByTestId('iwxxm-preview-pane')).toBeVisible();
    await expect(page.getByTestId('iwxxm-preview-empty')).toBeVisible();

    const editor = page.getByLabel(/Enter METAR data manually/i);
    await editor.click();
    await editor.fill(METAR_NO_EQ);

    await page.getByTestId('workbench-console-toggle').click();
    const addEq = page.getByTestId('console-action-add_terminator');
    await expect(addEq).toBeVisible({ timeout: 5000 });
    await addEq.click();

    await expect
      .poll(
        async () => {
          const text = await page.locator('.cm-content').innerText();
          return text.replace(/\n/g, '').trim().endsWith('=');
        },
        { timeout: 5000 },
      )
      .toBe(true);
  });
});

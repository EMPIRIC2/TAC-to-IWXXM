/**
 * T4.4 / TC-F7-001 + TC-F7-004 — F7 live workbench smoke (UJ-013 / UJ-017).
 *
 * Spec: docs/test-plan.md TC-F7-001, TC-F7-004; execution-plan T4.4.
 */
import { expect, test } from '@playwright/test';
import { openConverterForE2e } from './playwright-e2e-helpers';

const METAR_TAC = 'METAR KJFK 121251Z 24016G28KT 3SM -RA BR BKN020 OVC040 14/11 A2990';

async function stubLiveAssistApis(page: import('@playwright/test').Page): Promise<{
  lintCalls: number[];
  decodeCalls: number[];
}> {
  const lintCalls: number[] = [];
  const decodeCalls: number[] = [];

  await page.route('**/api/v1/lint-tac', async (route) => {
    lintCalls.push(Date.now());
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        ok: false,
        issues: [
          {
            severity: 'error',
            code: 'demo_span',
            message: 'Demo lint span',
            start: 0,
            end: 5,
          },
        ],
        fixes: [],
        product: 'METAR',
      }),
    });
  });

  await page.route('**/api/v1/decode-tac', async (route) => {
    decodeCalls.push(Date.now());
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
      }),
    });
  });

  return { lintCalls, decodeCalls };
}

test.describe('T4.4 / TC-F7-001 + TC-F7-004: live workbench', () => {
  test('TC-F7-001: workbench shell mounts editor, products, console, live IWXXM off', async ({
    page,
  }) => {
    await stubLiveAssistApis(page);
    await openConverterForE2e(page);

    await expect(page.getByTestId('tac-editor')).toBeVisible();
    await expect(page.getByTestId('decode-panel')).toBeVisible();
    await expect(page.getByTestId('workbench-console')).toBeVisible();
    await expect(page.getByTestId('live-iwxxm-toggle')).not.toBeChecked();

    await page.getByLabel(/Expand parameters/i).click();
    const product = page.locator('#param-product');
    await expect(product).toBeVisible();
    for (const value of [
      'auto',
      'METAR',
      'SPECI',
      'TAF',
      'SIGMET',
      'AIRMET',
      'TCA',
      'VAA',
    ]) {
      await expect(product.locator(`option[value="${value}"]`)).toHaveCount(1);
    }
  });

  test('TC-F7-004: typing triggers lint/decode; rapid edits coalesce; spans attributed', async ({
    page,
  }) => {
    const { lintCalls, decodeCalls } = await stubLiveAssistApis(page);
    await openConverterForE2e(page);

    const editor = page.getByLabel(/Enter METAR data manually/i);
    await editor.click();
    await editor.fill('M');
    await editor.fill('ME');
    await editor.fill(METAR_TAC);

    await expect
      .poll(() => lintCalls.length, { timeout: 5000 })
      .toBeGreaterThanOrEqual(1);
    await expect
      .poll(() => decodeCalls.length, { timeout: 5000 })
      .toBeGreaterThanOrEqual(1);

    // Rapid edits should not 1:1 match keystrokes (debounce coalescing).
    expect(lintCalls.length).toBeLessThan(3);

    await expect(page.getByTestId('tac-editor')).toHaveAttribute(
      'data-issue-span-count',
      '1',
    );

    await page.getByTestId('workbench-console-toggle').click();
    await expect(page.getByTestId('workbench-console-lines')).toContainText(
      /lint-tac|issue/i,
    );
  });
});

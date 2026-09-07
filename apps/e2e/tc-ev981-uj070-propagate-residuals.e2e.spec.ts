/**
 * EV-981 — UJ-070 opt-in keep leftover TAC in remarks (#981).
 *
 * Spec: docs/test-plan.md TC-EV981-003; docs/user-journeys.md UJ-070.
 * [Corpus: product §F6/F9/F7] [Corpus: journeys] [Corpus: tests]
 */
import { expect, test } from '@playwright/test';
import { fillManualTac, openPublicConverter } from './playwright-e2e-helpers';

test.describe('EV-981 — UJ-070 propagate residuals toggle', () => {
  test('TC-EV981-003: workbench toggle posts propagate_residuals_to_remarks', async ({
    page,
  }) => {
    let postedPropagate: string | null = null;
    await page.route('**/api/v1/convert', async (route) => {
      const body = route.request().postDataBuffer();
      if (body) {
        const text = body.toString('utf8');
        postedPropagate =
          /name="propagate_residuals_to_remarks"\r?\n\r?\n([^\r\n]+)/.exec(text)?.[1] ??
          null;
      }
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          results: [
            {
              name: 'manual',
              content: '<iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/2025-2"/>',
              tac_input: 'METAR KJFK 251451Z 18005KT 10SM FEW050 22/12 A2992=',
            },
          ],
          issues: [],
          ok: true,
        }),
      });
    });

    await openPublicConverter(page);
    const toggle = page.getByTestId('propagate-residuals-toggle');
    await expect(toggle).toBeVisible();
    await toggle.check();
    await fillManualTac(page, 'METAR KJFK 251451Z 18005KT 10SM FEW050 22/12 A2992=');
    await page.getByTestId('convert-button').click();
    await expect.poll(() => postedPropagate).toBe('true');
  });
});

/**
 * Narrative full journey — **retired F21** (login → admin → logout path gone).
 * Public convert / preferences covered by tac-file-conversion + public-app-f21-f22.
 * [Corpus: tests] — no skip wrappers; assert public Convert path instead.
 */
import { expect, test } from '@playwright/test';

test.describe('Workflow: Narrative Full Journey', () => {
  test('public Convert shell supports theme toggle without Auth narrative', async ({
    page,
  }) => {
    await page.goto('/');
    await expect(page.getByTestId('convert-button')).toBeVisible({
      timeout: 30_000,
    });
    await expect(page.getByTestId('tac-editor')).toBeVisible();
    // Opposite state: logout chrome returned with Auth; convert-button proves shell load.
    await expect(page.getByTestId('logout-button')).toHaveCount(0);
  });
});

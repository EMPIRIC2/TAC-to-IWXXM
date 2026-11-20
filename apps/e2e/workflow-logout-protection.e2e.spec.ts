/**
 * Logout protection workflow — **retired F21** (no Auth / logout chrome).
 * [Corpus: tests] — no skip wrappers; assert logout controls are absent.
 */
import { expect, test } from '@playwright/test';

test.describe('Workflow: Logout Protection', () => {
  test('operator logout chrome is absent on the public Convert shell', async ({
    page,
  }) => {
    await page.goto('/');
    await expect(page.getByTestId('convert-button')).toBeVisible({
      timeout: 30_000,
    });
    // Opposite state: logout chrome returned with Auth; convert-button proves shell load.
    await expect(page.getByTestId('logout-button')).toHaveCount(0);
  });
});

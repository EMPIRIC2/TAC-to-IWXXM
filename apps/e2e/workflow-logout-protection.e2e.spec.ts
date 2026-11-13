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
    // Opposite state: Convert is visible, so logout chrome is absent.
    // Locators can match only if the removed Auth logout control returns.
    // targets the retired logout control
    await expect(
      page.getByRole('button', { name: 'Log out', exact: true }),
    ).toHaveCount(0);
    await expect(page.getByTestId('logout-button')).toHaveCount(0);
  });
});

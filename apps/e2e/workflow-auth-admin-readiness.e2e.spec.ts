/**
 * Auth readiness workflow — **retired F21** (operator Auth removed).
 * Coverage moved to auth.e2e.spec.ts / public-app-f21-f22.e2e.spec.ts (TC-F21-auth-gone).
 * [Corpus: tests] — no skip wrappers; assert public Convert shell instead.
 */
import { expect, test } from '@playwright/test';

test.describe('Workflow: Auth readiness', () => {
  test('public Convert shell loads without admin dashboard chrome', async ({
    page,
  }) => {
    await page.goto('/');
    await expect(page.getByTestId('convert-button')).toBeVisible({
      timeout: 30_000,
    });
    // Opposite state: Convert is visible, so admin dashboard chrome is absent.
    // Locators can match only if the removed admin surface returns.
    await expect(
      page.getByRole('heading', { name: 'Admin Dashboard', exact: true }),
    ).toHaveCount(0);
    await expect(page.getByTestId('admin-nav')).toHaveCount(0);
  });
});

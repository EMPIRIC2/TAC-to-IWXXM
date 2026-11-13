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
    // Opposite state: admin dashboard heading can match if Auth admin chrome returns.
    // targets the retired Admin Dashboard heading
    await expect(page.getByRole('heading', { name: /admin dashboard/i })).toHaveCount(
      0,
    );
    // Opposite state: admin-nav can match if the admin shell nav returns.
    await expect(page.getByTestId('admin-nav')).toHaveCount(0);
  });
});

/**
 * TC-F7-006 / UJ-019 — admin product surface removed (S011 / ADR-021).
 */
import { expect, test } from '@playwright/test';

test.describe('Admin routes removed', () => {
  test('converter has no admin dashboard heading or view option', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByRole('heading', { name: /Admin Dashboard/i })).toHaveCount(
      0,
    );
    await expect(page.getByLabel(/Switch view/i)).toHaveCount(0);
  });
});

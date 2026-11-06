/**
 * TC-F7-006 / UJ-019 — admin product surface removed (S011 / ADR-021).
 */
import { expect, test } from '@playwright/test';

test.describe('Admin routes removed', () => {
  test('converter has no admin dashboard heading or view option', async ({ page }) => {
    await page.goto('/');
    // targets the TAC to IWXXM heading
    await expect(page.getByRole('heading', { name: /^TAC to IWXXM$/ })).toBeVisible({
      timeout: 10_000,
    });
    // Opposite state: the converter heading is visible, so these admin controls are absent.
    await expect(
      page.getByRole('heading', { name: 'Admin Dashboard', exact: true }),
    ).toHaveCount(0);
    await expect(page.getByLabel('Switch view', { exact: true })).toHaveCount(0);
  });
});

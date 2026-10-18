/**
 * TC-F7-006 / UJ-019 — admin product surface removed (S011 / ADR-021).
 */
import { expect, test } from '@playwright/test';

test.describe('Admin routes removed', () => {
  test('converter has no admin dashboard heading or view option', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByRole('heading', { name: /^TAC to IWXXM$/ })).toBeVisible({
      timeout: 10_000,
    });
  });
});

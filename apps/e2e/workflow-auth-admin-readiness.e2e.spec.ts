/**
 * Auth readiness without admin dashboard (S011 / ADR-021).
 */
import { expect, test } from '@playwright/test';
import {
  E2E_USER_EMAIL,
  E2E_USER_PASSWORD,
  loginAsE2EUser,
} from './playwright-e2e-helpers';

test.describe('Workflow: Auth readiness', () => {
  test('startup and login reach converter (no admin dashboard)', async ({ page }) => {
    test.skip(
      !E2E_USER_EMAIL || !E2E_USER_PASSWORD,
      'Requires E2E_USER_EMAIL and E2E_USER_PASSWORD (or legacy PLAYWRIGHT_* aliases)',
    );

    await page.goto('/');
    await expect(page.getByRole('heading', { name: /METAR Converter/i })).toBeVisible();
    await expect(page.locator('#email')).toBeVisible();
    await expect(page.locator('#password')).toBeVisible();

    await loginAsE2EUser(page);

    await expect(page.getByRole('heading', { name: /Admin Dashboard/i })).toHaveCount(
      0,
    );
    await expect(
      page.getByRole('heading', { name: /METAR.*IWXXM.*Converter/i }),
    ).toBeVisible();
  });
});

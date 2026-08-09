/**
 * UJ-054 / TC-EV047-011 — operator Help entry opens the one-pager (EV-047).
 */
import { expect, test } from '@playwright/test';

test.describe('UJ-054 operator Help', () => {
  test('Help link targets the operator one-pager', async ({ page }) => {
    await page.goto('/');
    const help = page.getByTestId('operator-help-link');
    await expect(help).toBeVisible();
    await expect(help).toHaveAttribute('href', /docs\/guides\/operator-one-pager\.md/);
    await expect(help).toHaveAttribute('target', '_blank');
  });
});

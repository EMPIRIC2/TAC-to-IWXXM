/**
 * Mobile workbench chrome — no horizontal overflow at ~375px.
 *
 * Regression for EV-staging-adv-ux-reprobe (header Help/Preferences/Theme/Sign in).
 */

import { expect, test } from '@playwright/test';

test.describe('Workbench viewport chrome', () => {
  test('375px guest home does not horizontally overflow', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto('/');
    await page.waitForLoadState('domcontentloaded');
    // Seed local draft so guest loss banner appears (layout stress).
    const box = page.getByRole('textbox', { name: /Enter METAR|TAC/i }).first();
    if (await box.isVisible().catch(() => false)) {
      await box.fill('METAR YUDO 221630Z 24004MPS 0600=');
      await page.waitForTimeout(500);
    }
    const header = page.getByTestId('workbench-header-actions');
    await expect(header).toBeVisible();
    const overflowX = await page.evaluate(() => {
      const doc = document.documentElement;
      return Math.max(doc.scrollWidth, document.body.scrollWidth) - doc.clientWidth;
    });
    expect(overflowX).toBeLessThanOrEqual(1);
  });
});

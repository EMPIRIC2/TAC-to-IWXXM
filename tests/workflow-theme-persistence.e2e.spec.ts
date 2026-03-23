import { expect, test } from '@playwright/test';
import {
  ADMIN_EMAIL,
  ADMIN_PASSWORD,
  loginAndOpenConverter,
} from './playwright-e2e-helpers';

test.describe('Workflow: Theme Behavior And Persistence', () => {
  test('theme toggle works in converter, persists across reload, and remains consistent in admin view', async ({ page }) => {
    test.skip(
      !ADMIN_EMAIL || !ADMIN_PASSWORD,
      'Requires PLAYWRIGHT_ADMIN_EMAIL and PLAYWRIGHT_ADMIN_PASSWORD'
    );

    await loginAndOpenConverter(page);

    const themeSwitch = page.getByRole('switch', { name: /Switch to .* mode/i });
    await expect(themeSwitch).toBeVisible();

    const initialState = await themeSwitch.getAttribute('aria-checked');
    await themeSwitch.click();

    await expect
      .poll(async () => themeSwitch.getAttribute('aria-checked'))
      .not.toBe(initialState);

    const toggledState = await themeSwitch.getAttribute('aria-checked');

    await page.reload();

    const reloadedThemeSwitch = page.getByRole('switch', { name: /Switch to .* mode/i });
    await expect(reloadedThemeSwitch).toBeVisible();
    await expect(reloadedThemeSwitch).toHaveAttribute('aria-checked', toggledState || 'false');

    const viewSelect = page.getByLabel(/Switch view/i);
    await viewSelect.selectOption('admin');
    await expect(page.getByRole('heading', { name: /Admin Dashboard/i })).toBeVisible();

    const adminThemeSwitch = page.getByRole('switch', { name: /Switch to .* mode/i });
    await expect(adminThemeSwitch).toHaveAttribute('aria-checked', toggledState || 'false');
  });
});

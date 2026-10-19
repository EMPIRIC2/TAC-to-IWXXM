/**
 * Theme persistence on the public converter (F21 — no Auth).
 */
import { expect, test } from '@playwright/test';
import { openPublicConverter } from './playwright-e2e-helpers';

test.describe('Workflow: Theme Behavior And Persistence', () => {
  test('theme toggle works in converter and persists across reload', async ({
    page,
  }) => {
    await openPublicConverter(page);

    // Theme switch name is "Switch to light mode" or "Switch to dark mode".
    const themeSwitch = page.getByRole('switch', {
      // targets the theme mode switch
      name: /^Switch to (light|dark) mode$/,
    });
    await expect(themeSwitch).toBeVisible();

    const initialState = await themeSwitch.getAttribute('aria-checked');
    await themeSwitch.click();

    await expect
      .poll(async () => themeSwitch.getAttribute('aria-checked'))
      .not.toBe(initialState);

    const toggledState = await themeSwitch.getAttribute('aria-checked');

    await page.reload();
    await openPublicConverter(page);

    // Same theme switch after reload; the name still depends on the saved theme.
    const afterReload = page.getByRole('switch', {
      // targets the theme mode switch
      name: /^Switch to (light|dark) mode$/,
    });
    await expect(afterReload).toHaveAttribute('aria-checked', toggledState ?? '');
  });
});

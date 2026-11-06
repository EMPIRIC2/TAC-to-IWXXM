/**
 * Public shell stays behind the quality disclaimer until the operator continues.
 */
import { expect, test } from '@playwright/test';

test.describe('Site terms gate', () => {
  test('blocks the converter until the disclaimer is accepted', async ({ page }) => {
    await page.addInitScript(() => {
      if (sessionStorage.getItem('e2e-keep-site-terms') === '1') {
        return;
      }
      localStorage.removeItem('tac_privacy_preferences');
    });

    await page.goto('/');
    await expect(page.getByTestId('site-terms-gate')).toBeVisible();
    await expect(page.getByTestId('site-terms-continue')).toBeDisabled();
    // Opposite state: the converter heading is visible after the disclaimer is accepted.
    // targets the TAC to IWXXM heading
    await expect(page.getByRole('heading', { name: /^TAC to IWXXM$/ })).toHaveCount(0);

    await page.getByTestId('site-terms-ack').check();
    await page.getByTestId('site-terms-continue').click();
    // targets the TAC to IWXXM heading
    await expect(page.getByRole('heading', { name: /^TAC to IWXXM$/ })).toBeVisible();

    await page.evaluate(() => sessionStorage.setItem('e2e-keep-site-terms', '1'));
    await page.reload();
    // Opposite state: the disclaimer gate is visible before it is accepted.
    await expect(page.getByTestId('site-terms-gate')).toHaveCount(0);
    // targets the TAC to IWXXM heading
    await expect(page.getByRole('heading', { name: /^TAC to IWXXM$/ })).toBeVisible();
  });
});

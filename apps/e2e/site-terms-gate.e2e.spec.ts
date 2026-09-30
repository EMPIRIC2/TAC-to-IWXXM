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
    await expect(
      page.getByRole('heading', { name: /METAR.*IWXXM.*Converter/i }),
    ).toHaveCount(0);

    await page.getByTestId('site-terms-ack').check();
    await page.getByTestId('site-terms-continue').click();
    await expect(
      page.getByRole('heading', { name: /METAR.*IWXXM.*Converter/i }),
    ).toBeVisible();

    await page.evaluate(() => sessionStorage.setItem('e2e-keep-site-terms', '1'));
    await page.reload();
    await expect(page.getByTestId('site-terms-gate')).toHaveCount(0);
    await expect(
      page.getByRole('heading', { name: /METAR.*IWXXM.*Converter/i }),
    ).toBeVisible();
  });
});

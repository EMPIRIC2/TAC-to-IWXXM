/**
 * UX-2026-11-07-convert-chrome-polish — convert chrome polish (H4–H5).
 *
 * [Corpus: ui-style] [Corpus: journeys] [Corpus: tests]
 */
import { expect, test } from '@playwright/test';
import { openPublicConverter } from './playwright-e2e-helpers';

test.describe('UX-2026-11-07 convert chrome polish', () => {
  test('empty state uses converter chrome; product + settings layout; no console panels', async ({
    page,
  }) => {
    await openPublicConverter(page);

    // Opposite state: convert-empty-hero can match if the marketing hero returns.
    await expect(page.getByTestId('convert-empty-hero')).toHaveCount(0);
    await expect(page.getByTestId('convert-shell')).toBeVisible({ timeout: 15_000 });
    await expect(page.getByTestId('convert-chrome-toolbar')).toBeVisible();

    const toolbar = page.getByTestId('convert-chrome-toolbar');
    await expect(toolbar.getByTestId('product-type-select')).toBeVisible();
    await expect(toolbar.getByTestId('convert-settings-cog')).toBeVisible();

    const productBox = await toolbar.getByTestId('product-type-select').boundingBox();
    const cogBox = await toolbar.getByTestId('convert-settings-cog').boundingBox();
    expect(productBox && cogBox).toBeTruthy();
    if (productBox && cogBox) {
      expect(cogBox.x).toBeGreaterThan(productBox.x);
    }

    await expect(page.getByTestId('operator-footer')).toBeVisible();
    await page.getByTestId('operator-footer-collapse').click();
    // Opposite state: footer visible before collapse.
    await expect(page.getByTestId('operator-footer')).toHaveCount(0);
    await expect(page.getByTestId('operator-footer-reveal')).toBeVisible();
    await page.getByTestId('operator-footer-reveal').click();
    await expect(page.getByTestId('operator-footer')).toBeVisible();
  });
});

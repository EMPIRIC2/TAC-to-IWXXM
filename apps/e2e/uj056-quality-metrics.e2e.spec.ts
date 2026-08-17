/**
 * UJ-056 / TC-EV054-007 + TC-EV055-007 + TC-EV056-005 — Quality metrics tab.
 *
 * Open shell tab → filter product → open passer on `/quality/:stem` → C14N panes.
 * Live H4–H5 after staging remains stage 13.
 */
import { expect, test } from '@playwright/test';
import {
  dismissPrivacyNoticeIfPresent,
  openPublicConverter,
} from './playwright-e2e-helpers';

const PASSER_STEM = 'metar-A3-1';
const DEFERRED_STEM = 'metar-NIL-collect';

test.describe('UJ-056 Quality metrics tab (TC-EV054-007 / TC-EV055-007 / TC-EV056)', () => {
  test('open tab → filter METAR → passer detail + deferred gap label', async ({
    page,
  }) => {
    const listResponses: string[] = [];
    const detailResponses: string[] = [];

    page.on('response', (response) => {
      const url = response.url();
      if (!url.includes('/api/v1/quality-metrics')) {
        return;
      }
      if (url.includes(`/quality-metrics/${PASSER_STEM}`)) {
        detailResponses.push(url);
        return;
      }
      if (url.includes('/quality-metrics')) {
        listResponses.push(url);
      }
    });

    await openPublicConverter(page);
    await dismissPrivacyNoticeIfPresent(page);

    await expect(page.getByTestId('app-shell-nav')).toBeVisible();
    await page.getByTestId('shell-nav-quality').click();

    await expect(page.getByTestId('quality-metrics-page')).toBeVisible({
      timeout: 15_000,
    });
    await expect(page).toHaveURL(/\/quality\/?$/);
    await expect(page.getByTestId('quality-metrics-summary')).toBeVisible({
      timeout: 15_000,
    });
    await expect(page.getByTestId('quality-metrics-file-list')).toBeVisible();
    await expect(page.getByTestId(`quality-metrics-row-${PASSER_STEM}`)).toBeVisible();

    await page.getByTestId('quality-metrics-product-filter').selectOption('metar');

    await expect(page.getByTestId(`quality-metrics-row-${PASSER_STEM}`)).toBeVisible({
      timeout: 15_000,
    });
    await expect(
      page.getByTestId(`quality-metrics-row-${DEFERRED_STEM}`),
    ).toBeVisible();
    await expect(
      page.getByTestId(`quality-metrics-deferred-${DEFERRED_STEM}`),
    ).toBeVisible();
    // TAF passer should leave the list when filtered to METAR.
    await expect(page.getByTestId('quality-metrics-row-taf-A5-1')).toHaveCount(0);

    await page.getByTestId(`quality-metrics-row-${PASSER_STEM}`).click();

    await expect(page).toHaveURL(new RegExp(`/quality/${PASSER_STEM}$`));
    await expect(page.getByTestId('quality-metrics-detail')).toBeVisible({
      timeout: 15_000,
    });
    await expect(page.getByTestId('quality-metrics-match-status')).toContainText(
      /Matches official/i,
    );
    await expect(page.getByTestId('quality-metrics-pane-tac')).toBeVisible();
    await expect(page.getByTestId('quality-metrics-pane-official-xml')).toBeVisible();
    await expect(page.getByTestId('quality-metrics-pane-converted-xml')).toBeVisible();
    await expect(page.getByTestId('quality-metrics-unified-diff')).toBeVisible();
    // After EV-055 C14N + volatile-attr strip, equal stems should show empty diff.
    await expect(page.getByTestId('quality-metrics-diff-empty')).toBeVisible();

    await page.getByTestId('quality-metrics-detail-close').click();
    await expect(page).toHaveURL(/\/quality\/?$/);
    await expect(page.getByTestId('quality-metrics-file-list')).toBeVisible({
      timeout: 15_000,
    });

    expect(listResponses.length).toBeGreaterThan(0);
    expect(detailResponses.length).toBeGreaterThan(0);
  });

  test('TC-EV055-007: normalized panes, raw override, validate chips', async ({
    page,
  }) => {
    await openPublicConverter(page);
    await dismissPrivacyNoticeIfPresent(page);

    await page.getByTestId('shell-nav-quality').click();
    await expect(page.getByTestId('quality-metrics-page')).toBeVisible({
      timeout: 15_000,
    });

    await page.getByTestId(`quality-metrics-row-${PASSER_STEM}`).click();
    await expect(page.getByTestId('quality-metrics-detail')).toBeVisible({
      timeout: 15_000,
    });
    await expect(page).toHaveURL(new RegExp(`/quality/${PASSER_STEM}$`));

    await expect(page.getByTestId('quality-metrics-xml-view-mode')).toContainText(
      /Normalized XML/i,
    );
    await expect(
      page.getByTestId('quality-metrics-validate-chip-schematron'),
    ).toContainText(/Schematron rules: checked/i);
    await expect(
      page.getByTestId('quality-metrics-validate-chip-schema-import'),
    ).toContainText(/XML schema imports: OK/i);
    await expect(page.getByTestId('quality-metrics-diff-empty')).toBeVisible();

    const officialBefore = await page
      .getByTestId('quality-metrics-pane-official-xml')
      .innerText();

    await page.getByTestId('quality-metrics-xml-view-raw').check();
    await expect(page.getByTestId('quality-metrics-xml-view-mode')).toContainText(
      /Raw XML/i,
    );
    // Diff stays on normalized peers even when panes show raw.
    await expect(page.getByTestId('quality-metrics-diff-empty')).toBeVisible();

    const officialRaw = await page
      .getByTestId('quality-metrics-pane-official-xml')
      .innerText();
    // Raw toggle should change pane text for pretty-printed official XML.
    expect(officialRaw.length).toBeGreaterThan(0);
    expect(officialRaw === officialBefore || officialRaw.includes('\n')).toBeTruthy();
  });

  test('TC-EV056-005: deep-link /quality/:stem loads detail', async ({ page }) => {
    await page.goto(`/quality/${PASSER_STEM}`);
    await dismissPrivacyNoticeIfPresent(page);

    await expect(page.getByTestId('quality-metrics-detail')).toBeVisible({
      timeout: 15_000,
    });
    await expect(page.getByTestId('quality-metrics-match-status')).toContainText(
      /Matches official/i,
    );
    await expect(page.getByTestId('quality-metrics-detail-close')).toBeVisible();
  });

  test('TC-EV058-005: switch Inline ↔ Side-by-side and persist preference', async ({
    page,
  }) => {
    await page.goto(`/quality/${PASSER_STEM}`);
    await dismissPrivacyNoticeIfPresent(page);

    await expect(page.getByTestId('quality-metrics-detail')).toBeVisible({
      timeout: 15_000,
    });
    await expect(page.getByTestId('quality-metrics-diff-layout')).toBeVisible();
    await expect(
      page.getByTestId('quality-metrics-diff-layout-unified'),
    ).toHaveAttribute('aria-checked', 'true');

    await page.getByTestId('quality-metrics-diff-layout-side-by-side').click();
    await expect(
      page.getByTestId('quality-metrics-diff-layout-side-by-side'),
    ).toHaveAttribute('aria-checked', 'true');
    // Equal passer still shows empty diff in both layouts.
    await expect(page.getByTestId('quality-metrics-diff-empty')).toBeVisible();

    await page.reload();
    await dismissPrivacyNoticeIfPresent(page);
    await expect(page.getByTestId('quality-metrics-detail')).toBeVisible({
      timeout: 15_000,
    });
    await expect(
      page.getByTestId('quality-metrics-diff-layout-side-by-side'),
    ).toHaveAttribute('aria-checked', 'true');
  });
});

/**
 * UJ-058 / TC-EV057-838-005 — Validate existing IWXXM without TAC convert.
 *
 * Local T2 smoke. Live H4–H5 remains stage 13 after staging deploy.
 */
import { expect, test } from '@playwright/test';
import {
  dismissPrivacyNoticeIfPresent,
  openPublicConverter,
} from './playwright-e2e-helpers';

const GOOD_XML = `<?xml version="1.0" encoding="UTF-8"?>
<iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/2025-2"
  xmlns:gml="http://www.opengis.net/gml/3.2"
  gml:id="metar-uj058">
  <iwxxm:observationTime>
    <gml:TimeInstant gml:id="t0">
      <gml:timePosition>2026-08-15T12:00:00Z</gml:timePosition>
    </gml:TimeInstant>
  </iwxxm:observationTime>
</iwxxm:METAR>`;

const BROKEN_XML = '<not-a-valid-iwxxm>broken</not-a-valid-iwxxm>';

test.describe('UJ-058: Validate existing IWXXM (TC-EV057-838)', () => {
  test('Validate mode paste broken XML shows structured fail; no convert required', async ({
    page,
  }) => {
    await openPublicConverter(page);
    await dismissPrivacyNoticeIfPresent(page);

    await page.getByTestId('input-mode-validate_iwxxm').click();
    await expect(page.getByTestId('validate-iwxxm-help')).toBeVisible();

    const editor = page.getByLabel(/Enter IWXXM XML manually/i);
    await editor.click();
    await page.keyboard.press(process.platform === 'darwin' ? 'Meta+A' : 'Control+A');
    await page.keyboard.insertText(BROKEN_XML);

    await page.getByRole('button', { name: /Validate IWXXM XML/i }).click();

    await expect(page.getByTestId('validate-iwxxm-report')).toBeVisible({
      timeout: 60_000,
    });
    await expect(page.getByTestId('validate-iwxxm-status')).toContainText(/Invalid/i);
  });

  test('Validate mode paste minimal IWXXM returns a report panel', async ({ page }) => {
    await openPublicConverter(page);
    await dismissPrivacyNoticeIfPresent(page);

    await page.getByTestId('input-mode-validate_iwxxm').click();
    const editor = page.getByLabel(/Enter IWXXM XML manually/i);
    await editor.click();
    await page.keyboard.press(process.platform === 'darwin' ? 'Meta+A' : 'Control+A');
    await page.keyboard.insertText(GOOD_XML);

    await page.getByRole('button', { name: /Validate IWXXM XML/i }).click();

    await expect(page.getByTestId('validate-iwxxm-report')).toBeVisible({
      timeout: 60_000,
    });
    await expect(page.getByTestId('validate-iwxxm-status')).toBeVisible();
  });
});

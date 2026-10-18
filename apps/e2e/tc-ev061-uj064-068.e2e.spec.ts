/**
 * EV-061 T2 local Playwright — UJ-064..068 (#1010–#1014).
 *
 * Spec: docs/test-plan.md TC-EV061-1010..1014; docs/user-journeys.md UJ-064..068.
 * [Corpus: product §F7] [Corpus: product §F2] [Corpus: product §F6] [Corpus: product §F9]
 * [Corpus: product §F10] [Corpus: product §F15] [Corpus: journeys] [Corpus: tests] [Corpus: api]
 *
 * Live H4–H5 remains 12/13. UJ-DEV-009 (#1015) is CI-only (see 09-qa / promote-gate tests).
 */
import { expect, test, type APIRequestContext } from '@playwright/test';
import {
  fillManualTac,
  openPublicConverter,
  playwrightApiFetch,
} from './playwright-e2e-helpers';

const AHL_WELL_FORMED = `SAUS31 KZNY 121200
METAR KJFK 121151Z 18008KT 10SM FEW250 22/14 A3012=
METAR KLGA 121151Z 18008KT 10SM SCT040 21/13 A3010=
`;

const AHL_MALFORMED = `QQUS31 KZNY 121200
METAR KJFK 121151Z 18008KT 10SM FEW250 22/14 A3012=
`;

/**
 * IWXXM METAR with aerodrome, wind, and temperature.
 * Must produce decode segments on every validate run. Zero segments fail this spec.
 * The document still starts with an XML declaration so a raw dump fails the row check.
 */
const DECODE_ROWS_IWXXM = `<?xml version="1.0" encoding="UTF-8"?>
<iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/2025-2"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns:gml="http://www.opengis.net/gml/3.2"
    xmlns:aixm="http://www.aixm.aero/schema/5.1.1"
    gml:id="metar.basic.kjfk"
    reportStatus="NORMAL"
    permissibleUsage="OPERATIONAL"
    automatedStation="false">
  <iwxxm:issueTime>
    <gml:TimeInstant gml:id="t.issue">
      <gml:timePosition>2023-06-23T17:51:00Z</gml:timePosition>
    </gml:TimeInstant>
  </iwxxm:issueTime>
  <iwxxm:aerodrome>
    <aixm:AirportHeliport gml:id="ad.kjfk">
      <aixm:timeSlice>
        <aixm:AirportHeliportTimeSlice gml:id="ad.ts.kjfk">
          <gml:validTime/>
          <aixm:interpretation>SNAPSHOT</aixm:interpretation>
          <aixm:designator>KJFK</aixm:designator>
          <aixm:locationIndicatorICAO>KJFK</aixm:locationIndicatorICAO>
        </aixm:AirportHeliportTimeSlice>
      </aixm:timeSlice>
    </aixm:AirportHeliport>
  </iwxxm:aerodrome>
  <iwxxm:observationTime>
    <gml:TimeInstant gml:id="t.obs">
      <gml:timePosition>2023-06-23T17:51:00Z</gml:timePosition>
    </gml:TimeInstant>
  </iwxxm:observationTime>
  <iwxxm:observation>
    <iwxxm:MeteorologicalAerodromeObservation gml:id="obs.1" cloudAndVisibilityOK="false">
      <iwxxm:airTemperature uom="Cel">15.0</iwxxm:airTemperature>
      <iwxxm:dewpointTemperature uom="Cel">7.0</iwxxm:dewpointTemperature>
      <iwxxm:qnh uom="hPa">1017.6</iwxxm:qnh>
      <iwxxm:surfaceWind>
        <iwxxm:AerodromeSurfaceWind variableWindDirection="false">
          <iwxxm:meanWindDirection uom="deg">180</iwxxm:meanWindDirection>
          <iwxxm:meanWindSpeed uom="[kn_i]">12</iwxxm:meanWindSpeed>
        </iwxxm:AerodromeSurfaceWind>
      </iwxxm:surfaceWind>
      <iwxxm:visibility>
        <iwxxm:AerodromeHorizontalVisibility>
          <iwxxm:prevailingVisibility uom="m">10000</iwxxm:prevailingVisibility>
          <iwxxm:prevailingVisibilityOperator>ABOVE</iwxxm:prevailingVisibilityOperator>
        </iwxxm:AerodromeHorizontalVisibility>
      </iwxxm:visibility>
    </iwxxm:MeteorologicalAerodromeObservation>
  </iwxxm:observation>
</iwxxm:METAR>`;

async function convertBulletin(
  request: APIRequestContext,
  text: string,
): Promise<{ status: number; body: Record<string, unknown> }> {
  const response = await playwrightApiFetch(request, '/api/v1/convert-bulletin', {
    method: 'POST',
    multipart: { manual_text: text, product: 'METAR' },
    timeout: 60_000,
  });
  return {
    status: response.status(),
    body: (await response.json()) as Record<string, unknown>,
  };
}

test.describe('EV-061 T2 — UJ-064 Validate IWXXM decode', () => {
  test('UJ-064: validate mode shows report and required decode rows', async ({
    page,
  }) => {
    await openPublicConverter(page);
    await page.getByTestId('input-mode-validate_iwxxm').click();
    await expect(page.getByTestId('validate-iwxxm-help')).toBeVisible();
    const editor = page.getByLabel(/Enter IWXXM XML manually/i);
    await editor.click();
    await page.keyboard.press(process.platform === 'darwin' ? 'Meta+A' : 'Control+A');
    await page.keyboard.insertText(DECODE_ROWS_IWXXM);
    await page.getByRole('button', { name: /validate iwxxm xml/i }).click();
    await expect(page.getByTestId('validate-iwxxm-report')).toBeVisible({
      timeout: 60_000,
    });
    const segments = page.getByTestId('decode-segments');
    await expect(segments).toBeVisible();
    await expect(segments).not.toContainText('<?xml');
  });
});

test.describe('EV-061 T2 — UJ-065 AHL decode + convert', () => {
  test('UJ-065: AHL convert shows bulletin summary', async ({ page }) => {
    await openPublicConverter(page);
    await page.getByTestId('input-mode-ahl_bulletin').click();
    await fillManualTac(page, AHL_WELL_FORMED);
    await page.getByTestId('convert-button').click();
    await expect(page.getByTestId('bulletin-summary')).toBeVisible({ timeout: 60_000 });
    await expect(page.getByTestId('bulletin-summary')).toContainText(/2 report/i);
  });

  test('UJ-065: convert-bulletin malformed AHL → INVALID_AHL', async ({ request }) => {
    const { status, body } = await convertBulletin(request, AHL_MALFORMED);
    expect([400, 422]).toContain(status);
    const detail = body.detail as { code?: string } | string | undefined;
    const code =
      typeof detail === 'object' && detail !== null ? detail.code : undefined;
    expect(code ?? JSON.stringify(body)).toMatch(/INVALID_AHL/);
  });
});

test.describe('EV-061 T2 — UJ-066 / UJ-067 converter bars', () => {
  test('UJ-066/067: product-profile + params bars visible at 1280px', async ({
    page,
  }) => {
    await page.setViewportSize({ width: 1280, height: 800 });
    await openPublicConverter(page);
    const productBar = page.getByTestId('product-profile-bar');
    const paramsBar = page.getByTestId('conversion-params-bar');
    await expect(productBar).toBeVisible();
    await expect(paramsBar).toBeVisible();
    await expect(page.getByTestId('product-type-select')).toBeVisible();
    await expect(page.getByTestId('library-pickers-bar')).toBeVisible();
    await expect(page.getByTestId('conversion-library-select')).toBeVisible();
    await expect(page.getByTestId('profile-type-select')).toHaveCount(0);
    // Product bar is wrap-capable at ≥1024. Params bar stays nowrap.
    await expect(productBar).toHaveCSS('flex-wrap', 'wrap');
    await expect(paramsBar).toHaveCSS('flex-wrap', 'nowrap');
  });

  test('UJ-066: bars may wrap below 1024px', async ({ page }) => {
    await page.setViewportSize({ width: 800, height: 800 });
    await openPublicConverter(page);
    await expect(page.getByTestId('product-profile-bar')).toBeVisible();
    await expect(page.getByTestId('conversion-params-bar')).toBeVisible();
  });
});

test.describe('EV-061 T2 — UJ-068 Lint & validation catalog', () => {
  test('UJ-068: catalog tab lists codes with working source links', async ({
    page,
  }) => {
    await openPublicConverter(page);
    await page.getByTestId('shell-nav-catalog').click();
    await expect(page.getByTestId('lint-validation-catalog-page')).toBeVisible({
      timeout: 30_000,
    });
    const list = page.getByTestId('lint-validation-catalog-list');
    await expect(list).toBeVisible({ timeout: 45_000 });
    const links = list.getByRole('link');
    await expect(links.first()).toBeVisible({ timeout: 30_000 });
    const href = await links.first().getAttribute('href');
    expect(href).toMatch(/^https?:\/\//);
    expect(href).not.toMatch(/codes\.wmo\.int\/49-2/);
    // Operator copy must not leak planning ids (EV-048).
    const pageText = await page.getByTestId('lint-validation-catalog-page').innerText();
    expect(pageText).not.toMatch(/\[Corpus:|EV-061|UJ-068|ADR-|TC-EV061/);
  });
});

/**
 * EV-060 T2 local Playwright — UJ-059..063 (#1001–#1005).
 *
 * Spec: docs/test-plan.md TC-EV060-1001..1005; docs/user-journeys.md UJ-059..063.
 * [Corpus: product §F7] [Corpus: product §F6] [Corpus: product §F2] [Corpus: product §F29]
 * [Corpus: journeys] [Corpus: tests] [Corpus: api].
 *
 * Live H4–H5 remains 12/13. Auth register/login is tc-ev060-1006-auth.e2e.spec.ts.
 */
import { expect, test, type APIRequestContext, type Request } from '@playwright/test';
import {
  convertManualMetar,
  fillManualTac,
  openPublicConverter,
  playwrightApiFetch,
} from './playwright-e2e-helpers';

const AHL_WELL_FORMED = `SAUS31 KZNY 121200
METAR KJFK 121151Z 18008KT 10SM FEW250 22/14 A3012=
METAR KLGA 121151Z 19010KT 10SM SCT040 21/13 A3010=
`;

const AHL_MALFORMED = `QQUS31 KZNY 121200
METAR KJFK 121151Z 18008KT 10SM FEW250 22/14 A3012=
`;

const METAR_TAC = 'METAR KJFK 121251Z 24016G28KT 3SM -RA BR BKN020 OVC040 14/11 A2990=';

const MINIMAL_IWXXM = `<?xml version="1.0" encoding="UTF-8"?>
<iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/2025-2"
  xmlns:gml="http://www.opengis.net/gml/3.2"
  gml:id="metar-uj060">
  <iwxxm:observationTime>
    <gml:TimeInstant gml:id="t0">
      <gml:timePosition>2026-08-18T12:00:00Z</gml:timePosition>
    </gml:TimeInstant>
  </iwxxm:observationTime>
</iwxxm:METAR>`;

function postBody(req: Request): string {
  return req.postData() ?? '';
}

async function lintTac(
  request: APIRequestContext,
  text: string,
  product: string,
): Promise<{ status: number; body: Record<string, unknown> }> {
  const response = await playwrightApiFetch(request, '/api/v1/lint-tac', {
    method: 'POST',
    multipart: { manual_text: text, product },
    timeout: 45_000,
  });
  return {
    status: response.status(),
    body: (await response.json()) as Record<string, unknown>,
  };
}

test.describe('EV-060 T2 — UJ-059 AHL bulletin', () => {
  test('UJ-059: AHL mode convert shows bulletin summary', async ({ page }) => {
    await openPublicConverter(page);
    await page.getByTestId('input-mode-ahl_bulletin').click();
    await fillManualTac(page, AHL_WELL_FORMED);
    await page.getByTestId('convert-button').click();
    await expect(page.getByTestId('bulletin-summary')).toBeVisible({ timeout: 60_000 });
    await expect(page.getByTestId('bulletin-summary')).toContainText(/2 report/i);
  });

  test('UJ-059: lint-tac well-formed AHL is not heading-flood (TC-EV060-1001-001)', async ({
    request,
  }) => {
    const { status, body } = await lintTac(request, AHL_WELL_FORMED, 'METAR');
    expect(status).toBe(200);
    const issues = (body.issues as Array<{ code?: string }>) ?? [];
    const codes = issues.map((issue) => issue.code);
    expect(codes).not.toContain('MISSING_PRODUCT_KEYWORD');
    expect(codes).not.toContain('MULTI_REPORT_BULLETIN');
  });

  test('UJ-059: lint-tac malformed AHL is one INVALID_AHL (TC-EV060-1001-002)', async ({
    request,
  }) => {
    const { status, body } = await lintTac(request, AHL_MALFORMED, 'METAR');
    expect(status).toBe(200);
    expect(body.ok).toBe(false);
    const issues =
      (body.issues as Array<{ code?: string; location?: string; severity?: string }>) ??
      [];
    const bulletin = issues.filter(
      (issue) => issue.location === 'bulletin' && issue.severity === 'error',
    );
    expect(bulletin).toHaveLength(1);
    expect(bulletin[0]?.code).toBe('INVALID_AHL');
  });
});

test.describe('EV-060 T2 — UJ-060 IWXXM product pass-through', () => {
  test('UJ-060: product IWXXM help + Lint & validate; F7.s Validate mode remains', async ({
    page,
  }) => {
    await openPublicConverter(page);
    await page.getByTestId('product-type-select').selectOption('IWXXM');
    await expect(page.getByTestId('iwxxm-product-help')).toBeVisible();
    await expect(page.getByTestId('iwxxm-product-help')).toContainText(/pass-through/i);
    await expect(page.getByTestId('convert-button')).toHaveAccessibleName(
      /Lint and validate IWXXM XML/i,
    );
    await expect(page.getByTestId('convert-button')).toHaveText(/Lint & validate/i);
    await expect(page.getByTestId('input-mode-validate_iwxxm')).toBeEnabled();
    await page.getByTestId('input-mode-validate_iwxxm').click();
    await expect(page.getByTestId('validate-iwxxm-help')).toBeVisible();
  });

  test('UJ-060: TAC text under product=iwxxm is NOT_XML (TC-EV060-1003-002)', async ({
    request,
  }) => {
    const { status, body } = await lintTac(request, METAR_TAC, 'iwxxm');
    expect(status).toBe(200);
    expect(body.ok).toBe(false);
    const codes = ((body.issues as Array<{ code?: string }>) ?? []).map(
      (issue) => issue.code,
    );
    expect(codes).toContain('NOT_XML');
    expect(codes).not.toContain('MISSING_PRODUCT_KEYWORD');
  });

  test('UJ-060: XML under product=iwxxm lints without TAC convert (TC-EV060-1003-001)', async ({
    request,
  }) => {
    const { status, body } = await lintTac(request, MINIMAL_IWXXM, 'iwxxm');
    expect(status).toBe(200);
    const codes = ((body.issues as Array<{ code?: string }>) ?? []).map(
      (issue) => issue.code,
    );
    expect(codes).not.toContain('MISSING_PRODUCT_KEYWORD');
    expect(codes).not.toContain('NOT_XML');
  });
});

test.describe('EV-060 T2 — UJ-061 profile at converter top', () => {
  test('UJ-061: labeled Profile at top is sent on convert (TC-EV060-1002)', async ({
    page,
  }) => {
    await openPublicConverter(page);
    const profile = page.getByTestId('profile-type-select');
    await expect(profile).toBeVisible();
    await expect(profile).toHaveAccessibleName(/^profile$/i);
    await profile.selectOption('iwxxm_us');

    const convertReq = page.waitForRequest(
      (req) => req.url().includes('/api/v1/convert') && req.method() === 'POST',
      { timeout: 60_000 },
    );
    await convertManualMetar(page, METAR_TAC);
    const captured = await convertReq;
    expect(postBody(captured)).toContain('iwxxm_us');
    await expect(page.getByRole('region', { name: /conversion results/i })).toBeVisible(
      {
        timeout: 60_000,
      },
    );
  });
});

test.describe('EV-060 T2 — UJ-062 bulletin fields', () => {
  test('UJ-062: Bulletin ID + Issuing Center sent on convert (TC-EV060-1005-001)', async ({
    page,
  }) => {
    await openPublicConverter(page);
    const bulletinId = page.getByTestId('bulletin-id-input');
    const issuingCenter = page.getByTestId('issuing-center-input');
    await expect(bulletinId).toBeVisible();
    await expect(issuingCenter).toBeVisible();
    await expect(bulletinId).toHaveAccessibleName(/bulletin id/i);
    await expect(issuingCenter).toHaveAccessibleName(/issuing center/i);
    await bulletinId.fill('SAAA00');
    await issuingCenter.fill('KWBC');

    const convertReq = page.waitForRequest(
      (req) => req.url().includes('/api/v1/convert') && req.method() === 'POST',
      { timeout: 60_000 },
    );
    await convertManualMetar(page, METAR_TAC);
    const captured = await convertReq;
    const body = postBody(captured);
    expect(body).toContain('SAAA00');
    expect(body).toContain('KWBC');
    await expect(page.getByRole('region', { name: /conversion results/i })).toBeVisible(
      {
        timeout: 60_000,
      },
    );
  });

  test('UJ-062: invalid Issuing Center is a field error (TC-EV060-1005-003)', async ({
    page,
  }) => {
    await openPublicConverter(page);
    await page.getByTestId('issuing-center-input').fill('KW1C');
    await fillManualTac(page, METAR_TAC);
    await page.getByTestId('convert-button').click();
    await expect(page.getByTestId('issuing-center-field-error')).toBeVisible();
    await expect(page.getByTestId('issuing-center-field-error')).toContainText(
      /4-letter ICAO/i,
    );
  });
});

test.describe('EV-060 T2 — UJ-063 log_level', () => {
  test('UJ-063: log-level control is sent on convert (TC-EV060-1004)', async ({
    page,
  }) => {
    await openPublicConverter(page);
    await page.getByLabel(/Expand parameters/i).click();
    const logLevel = page.locator('#param-log-level');
    await expect(logLevel).toBeVisible();
    await logLevel.selectOption('DEBUG');

    const convertReq = page.waitForRequest(
      (req) => req.url().includes('/api/v1/convert') && req.method() === 'POST',
      { timeout: 60_000 },
    );
    await convertManualMetar(page, METAR_TAC);
    const captured = await convertReq;
    expect(postBody(captured)).toMatch(/DEBUG/i);
  });

  test('UJ-063: convert API accepts DEBUG and ERROR log_level', async ({ request }) => {
    for (const logLevel of ['DEBUG', 'ERROR']) {
      const response = await playwrightApiFetch(request, '/api/v1/convert', {
        method: 'POST',
        multipart: {
          manual_text: METAR_TAC,
          product: 'METAR',
          log_level: logLevel,
        },
        timeout: 60_000,
      });
      expect(response.status(), `log_level=${logLevel}`).toBeLessThan(500);
      expect([200, 422]).toContain(response.status());
    }
  });
});

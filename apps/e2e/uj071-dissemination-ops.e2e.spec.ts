/**
 * H6′ — Playwright smokes for UJ-071 Dissemination ops (EV-936 / #936).
 *
 * Spec: docs/test-plan.md TC-F16-OPS-005; docs/user-journeys.md UJ-071.
 * Drawer regression remains `uj027-030-dissemination-drawer.e2e.spec.ts` (TC-F16-OPS-006).
 *
 * Auth is seeded via localStorage + stubbed ops APIs so CI does not require live JWT.
 */
import { expect, test, type Page, type Request } from '@playwright/test';
import {
  dismissPrivacyNoticeIfPresent,
  openPublicConverter,
} from './playwright-e2e-helpers';

const MOCK_TOKEN = 'e2e-mock-ops-jwt';

type OpsCapture = {
  health: Request[];
  audit: Request[];
  planPut: Request[];
  planExecute: Request[];
  mappingPut: Request[];
};

async function seedMockAuth(page: Page): Promise<void> {
  await page.addInitScript((token) => {
    const expiresAt = String(Math.floor(Date.now() / 1000) + 3600);
    localStorage.setItem('access_token', token);
    localStorage.setItem('refresh_token', 'e2e-mock-refresh');
    localStorage.setItem('expires_at', expiresAt);
  }, MOCK_TOKEN);
}

async function stubWorkbenchNoise(page: Page): Promise<void> {
  await page.route('**/api/v1/work-sessions**', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ items: [], total: 0, page: 1, limit: 20 }),
    });
  });
  await page.route('**/api/v1/lint-tac', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        ok: true,
        issues: [],
        fixes: [],
        product: 'METAR',
      }),
    });
  });
  await page.route('**/api/v1/decode-tac', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        product: 'METAR',
        segments: [],
        residuals: [],
        summary: 'Stub summary',
      }),
    });
  });
}

async function stubOpsApis(page: Page): Promise<OpsCapture> {
  const captured: OpsCapture = {
    health: [],
    audit: [],
    planPut: [],
    planExecute: [],
    mappingPut: [],
  };

  await page.route('**/api/v1/dissemination/gateways/health**', async (route) => {
    captured.health.push(route.request());
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        items: [
          {
            ok: true,
            gateway: 'file',
            connectivity_ok: true,
            detail: 'local filesystem ready',
          },
          {
            ok: false,
            gateway: 'wis2',
            connectivity_ok: false,
            detail: 'staging probe only',
          },
        ],
      }),
    });
  });

  await page.route('**/api/v1/dissemination/audit**', async (route) => {
    captured.audit.push(route.request());
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        items: [
          {
            id: 'audit-e2e-1',
            user_id: 'u-e2e',
            message_id: 'ops-sample',
            station: 'KJFK',
            profile: 'ICAO_2025',
            iwxxm_version: '2025-2',
            product: 'metar',
            status: 'DELIVERED',
            gateway: 'file',
            detail: 'delivered to local sink',
            destinations: { file: 'ok' },
            created_at: '2026-09-03T00:00:00Z',
          },
        ],
        total: 1,
        page: 1,
        limit: 20,
      }),
    });
  });

  await page.route('**/api/v1/dissemination/plans/**', async (route) => {
    const req = route.request();
    const method = req.method();
    if (method === 'PUT') {
      captured.planPut.push(req);
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'plan-e2e-1',
          user_id: 'u-e2e',
          slug: 'nightly',
          validity_policy: 'warn-ok',
          destination_refs: ['file', 'wis2'],
          transforms: [],
          created_at: '2026-09-03T00:00:00Z',
          updated_at: '2026-09-03T00:00:00Z',
        }),
      });
      return;
    }
    if (method === 'POST' && req.url().includes('/execute')) {
      captured.planExecute.push(req);
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          plan_id: 'plan-e2e-1',
          receipts: [{ status: 'SKIPPED', gateway: 'file', detail: 'dry-run' }],
        }),
      });
      return;
    }
    await route.continue();
  });

  await page.route('**/api/v1/dissemination/mappings/**', async (route) => {
    if (route.request().method() !== 'PUT') {
      await route.continue();
      return;
    }
    captured.mappingPut.push(route.request());
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        id: 'map-e2e-1',
        user_id: 'u-e2e',
        name: 'station-map',
        mode: 'sink',
        config: {
          message: 'message',
          station: 'station',
          timestamp: 'timestamp',
          externalId: 'external_id',
        },
        created_at: '2026-09-03T00:00:00Z',
        updated_at: '2026-09-03T00:00:00Z',
      }),
    });
  });

  return captured;
}

async function openDisseminationOps(page: Page): Promise<void> {
  await openPublicConverter(page);
  await page.getByTestId('shell-nav-dissemination-ops').click();
  await expect(page.getByTestId('dissemination-ops-page')).toBeVisible();
}

function expectBearer(req: Request): void {
  expect(req.headers().authorization).toBe(`Bearer ${MOCK_TOKEN}`);
}

test.describe('UJ-071: Dissemination ops H6′ (EV-936)', () => {
  test('guest: Dissemination ops prompts for sign-in', async ({ page }) => {
    await openDisseminationOps(page);
    await expect(page.getByTestId('dissemination-ops-sign-in')).toBeVisible();
    await expect(page.getByTestId('dissemination-ops-page')).toContainText(
      /Sign in to view dissemination plans/i,
    );
    await expect(page.getByTestId('dissemination-ops-health')).toHaveCount(0);
  });

  test('TC-F16-OPS-005: authed ops — health, plan, dry-run, mapping, audit (no secrets)', async ({
    page,
  }) => {
    await seedMockAuth(page);
    await stubWorkbenchNoise(page);
    const captured = await stubOpsApis(page);

    await openDisseminationOps(page);

    await expect(page.getByTestId('dissemination-ops-health')).toBeVisible();
    await expect(page.getByTestId('gateway-health-file')).toContainText(/OK/i);
    await expect(page.getByTestId('gateway-health-wis2')).toContainText(/Not OK/i);
    await expect(page.getByTestId('audit-row-audit-e2e-1')).toContainText('DELIVERED');
    await expect(page.getByTestId('audit-row-audit-e2e-1')).toContainText('KJFK');

    const auditText = await page.getByTestId('dissemination-ops-audit').innerText();
    expect(auditText).not.toMatch(/postgresql:\/\//i);
    expect(auditText).not.toMatch(/password|secret|amqp:\/\//i);

    expect(captured.health.length).toBeGreaterThan(0);
    expect(captured.audit.length).toBeGreaterThan(0);
    expectBearer(captured.health[0]!);
    expectBearer(captured.audit[0]!);

    await page.getByTestId('plan-slug-input').fill('nightly');
    await page.getByTestId('plan-policy-select').selectOption('warn-ok');
    await page.getByTestId('plan-dests-input').fill('file, wis2');
    await page.getByTestId('plan-save').click();
    await expect(page.getByTestId('plan-saved-id')).toContainText('plan-e2e-1');
    expect(captured.planPut.length).toBe(1);
    expectBearer(captured.planPut[0]!);
    const planBody = captured.planPut[0]!.postDataJSON() as {
      slug: string;
      validity_policy: string;
      destination_refs: string[];
    };
    expect(planBody.slug).toBe('nightly');
    expect(planBody.validity_policy).toBe('warn-ok');
    expect(planBody.destination_refs).toEqual(['file', 'wis2']);

    await page.getByTestId('plan-dry-run').click();
    await expect(page.getByTestId('plan-execute-note')).toContainText(/Dry-run/i);
    expect(captured.planExecute.length).toBe(1);
    expectBearer(captured.planExecute[0]!);
    const execBody = captured.planExecute[0]!.postDataJSON() as {
      dry_run?: boolean;
    };
    expect(execBody.dry_run).toBe(true);

    await page.getByTestId('mapping-name-input').fill('station-map');
    await page.getByTestId('mapping-mode-select').selectOption('sink');
    await page.getByTestId('mapping-save').click();
    await expect(page.getByTestId('mapping-saved-id')).toContainText('map-e2e-1');
    expect(captured.mappingPut.length).toBe(1);
    expectBearer(captured.mappingPut[0]!);
  });

  test('UJ-071 complements Convert: shell returns to converter after ops', async ({
    page,
  }) => {
    await seedMockAuth(page);
    await stubWorkbenchNoise(page);
    await stubOpsApis(page);
    await openDisseminationOps(page);
    await expect(page.getByTestId('dissemination-ops-page')).toBeVisible();

    await page.getByTestId('shell-nav-converter').click();
    await expect(
      page.getByRole('heading', { name: /METAR.*IWXXM.*Converter/i }),
    ).toBeVisible();
    await dismissPrivacyNoticeIfPresent(page);
    await expect(page.getByTestId('open-dissemination-drawer')).toBeVisible();
  });
});

/**
 * EV-039 / TC-F16-LIVE-001..004 — live local Compose multi-DB upload (UJ-027).
 *
 * Separate from mocked H6′ `uj027-030-dissemination-drawer.e2e.spec.ts` (AC3).
 * Run only via `make test-e2e-f16-live-sql` (`F16_LIVE_SQL=1`); skipped otherwise so
 * default `playwright test` / CI smoke stay green.
 *
 * T2.1: red stubs (fail until T2.2 implements live UI flow + T2.3 write asserts).
 * Do **not** `page.route` `/api/v1/dissemination/preflight` or `/send`.
 *
 * [Corpus: product §F16] [Corpus: tests] TC-F16-LIVE [Corpus: journeys §UJ-027]
 * [Corpus: tech-spec] mock-byoc
 */

import { expect, test } from '@playwright/test';

/** Dedicated live suite only — see Makefile `test-e2e-f16-live-sql`. */
const liveEnabled = process.env.F16_LIVE_SQL === '1';

/**
 * CI may skip SQL Server when the image/ODBC is heavy (AC7 / S05.L1).
 * Local close still requires LIVE-003 green.
 */
const skipSqlServer =
  process.env.F16_LIVE_SQL_SERVER === '0' || process.env.F16_SKIP_SQLSERVER === '1';

test.describe('TC-F16-LIVE: live local SQL dissemination (UJ-027 / EV-039)', () => {
  test.beforeEach(() => {
    test.skip(!liveEnabled, 'Set F16_LIVE_SQL=1 (make test-e2e-f16-live-sql)');
  });

  test('TC-F16-LIVE-001: Live local Postgres upload', async ({ page: _page }) => {
    // Preconditions (T2.2): compose byoc-postgres healthy; allowlist + CORS per tech-spec.
    // After UI success: T2.3 async-driver write assert against postgres_compose URI.
    expect(
      false,
      'EV-039 T2.2/T2.3: live Postgres preflight→send (no route mocks) + write assert',
    ).toBe(true);
  });

  test('TC-F16-LIVE-002: Live local MySQL upload', async ({ page: _page }) => {
    expect(
      false,
      'EV-039 T2.2/T2.3: live MySQL preflight→send (no route mocks) + write assert',
    ).toBe(true);
  });

  test('TC-F16-LIVE-003: Live local SQL Server upload', async ({ page: _page }) => {
    test.skip(
      skipSqlServer,
      'F16_LIVE_SQL_SERVER=0 / F16_SKIP_SQLSERVER=1 — SQL Server opt-out (CI)',
    );
    expect(
      false,
      'EV-039 T2.2/T2.3: live SQL Server preflight→send (no route mocks) + write assert',
    ).toBe(true);
  });

  test('TC-F16-LIVE-004: Live local SQLite upload + teardown audit', async ({
    page: _page,
  }) => {
    // Disposable SQLite file URI; assert write; remove temp .db (AC5/AC6 / T2.4).
    expect(
      false,
      'EV-039 T2.2/T2.3/T2.4: live SQLite preflight→send + write assert + temp teardown',
    ).toBe(true);
  });
});

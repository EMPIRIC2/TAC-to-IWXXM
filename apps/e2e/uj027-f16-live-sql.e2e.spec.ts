/**
 * EV-039 / TC-F16-LIVE-001..004 — live local Compose multi-DB upload (UJ-027).
 *
 * Separate from mocked H6' `uj027-030-dissemination-drawer.e2e.spec.ts` (AC3).
 * Run only via `make test-e2e-f16-live-sql` (`F16_LIVE_SQL=1`).
 *
 * No `page.route` for `/api/v1/dissemination/*` — real preflight/send against
 * local API + Compose DBs. Write assert via Python async drivers (T2.3).
 *
 * [Corpus: product §F16] [Corpus: tests] TC-F16-LIVE [Corpus: journeys §UJ-027]
 * [Corpus: tech-spec] mock-byoc
 */

import { expect, test, type Page } from '@playwright/test';
import { execFile } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { promisify } from 'node:util';
import { openConverterForE2e, playwrightApiBaseUrl } from './playwright-e2e-helpers';

const execFileAsync = promisify(execFile);

const liveEnabled = process.env.F16_LIVE_SQL === '1';
const skipSqlServer =
  process.env.F16_LIVE_SQL_SERVER === '0' || process.env.F16_SKIP_SQLSERVER === '1';

const E2E_DIR = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(E2E_DIR, '../..');
const FIXTURES = path.join(
  REPO_ROOT,
  'docs/sessions/S019-dissemination-upload/fixtures/mock-byoc-destinations.json',
);

const MINIMAL_IWXXM =
  '<?xml version="1.0"?><iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/2025-2"><iwxxm:observation/></iwxxm:METAR>';

type SinkType = 'postgres' | 'mysql' | 'sqlserver' | 'sqlite';

type MockByocFixtures = {
  postgres_compose: { uri: string };
  mysql_compose: { uri: string };
  sqlserver_compose: { uri: string };
};

function loadComposeUris(): MockByocFixtures {
  return JSON.parse(fs.readFileSync(FIXTURES, 'utf8')) as MockByocFixtures;
}

async function assertApiHealthy(): Promise<void> {
  const base = playwrightApiBaseUrl();
  const res = await fetch(`${base}/health`);
  expect(res.ok, `API health ${base}/health → ${res.status}`).toBe(true);
}

async function openDisseminationDrawer(page: Page): Promise<void> {
  const openBtn = page.getByTestId('open-dissemination-drawer');
  await expect(openBtn).toBeEnabled({ timeout: 15000 });
  await openBtn.click();
  await expect(page.getByTestId('dissemination-drawer')).toBeVisible();
}

/**
 * Capture kv_upload_key from the live send response (observe only — no route mock).
 */
function attachUploadKeyCapture(page: Page): { getKey: () => string | null } {
  let key: string | null = null;
  page.on('response', async (response) => {
    if (!response.url().includes('/api/v1/dissemination/send')) return;
    if (!response.ok()) return;
    try {
      const body = (await response.json()) as { kv_upload_key?: string };
      if (body.kv_upload_key) key = body.kv_upload_key;
    } catch {
      // ignore non-JSON
    }
  });
  return { getKey: () => key };
}

async function assertLiveDbWrite(opts: {
  sinkType: SinkType;
  uri: string;
  uploadKey?: string | null;
}): Promise<void> {
  const args = [
    'run',
    'python',
    '-m',
    'dissemination.live_write_assert',
    '--sink-type',
    opts.sinkType,
    '--uri',
    opts.uri,
    '--min-rows',
    '1',
  ];
  if (opts.uploadKey) {
    args.push('--upload-key', opts.uploadKey);
  }
  try {
    const { stdout } = await execFileAsync('uv', args, {
      cwd: REPO_ROOT,
      env: process.env,
      timeout: 60_000,
    });
    const parsed = JSON.parse(stdout.trim()) as { ok: boolean; count: number };
    expect(parsed.ok).toBe(true);
    expect(parsed.count).toBeGreaterThanOrEqual(1);
  } catch (err) {
    const detail =
      err && typeof err === 'object' && 'stderr' in err
        ? String((err as { stderr: Buffer | string }).stderr)
        : String(err);
    throw new Error(`live write assert failed: ${detail}`);
  }
}

async function liveDisseminate(
  page: Page,
  opts: { sinkType: SinkType; uri: string },
): Promise<string | null> {
  const capture = attachUploadKeyCapture(page);
  await openConverterForE2e(page);
  await openDisseminationDrawer(page);

  await page.getByTestId('dissemination-sink-chooser').selectOption(opts.sinkType);
  await page.getByTestId('dissemination-uri-input').fill(opts.uri);
  const ddl = page.getByTestId('dissemination-ddl-toggle');
  if (!(await ddl.isChecked())) {
    await ddl.check();
  }

  await page.getByTestId('dissemination-file-input').setInputFiles({
    name: 'live-metar.xml',
    mimeType: 'application/xml',
    buffer: Buffer.from(MINIMAL_IWXXM, 'utf8'),
  });
  await expect(page.getByTestId('dissemination-payload-status')).toContainText(
    /1 candidate/,
  );

  await page.getByTestId('dissemination-send-button').click();
  await expect(page.getByTestId('dissemination-send-success')).toBeVisible({
    timeout: 60_000,
  });
  await expect(
    page.locator('[data-testid^="dissemination-progress-row-"]').first(),
  ).toHaveAttribute('data-status', 'success', { timeout: 60_000 });

  // Allow response handler to settle
  await expect.poll(() => capture.getKey(), { timeout: 10_000 }).not.toBeNull();
  return capture.getKey();
}

test.describe('TC-F16-LIVE: live local SQL dissemination (UJ-027 / EV-039)', () => {
  test.beforeEach(async () => {
    test.skip(!liveEnabled, 'Set F16_LIVE_SQL=1 (make test-e2e-f16-live-sql)');
    await assertApiHealthy();
  });

  test('TC-F16-LIVE-001: Live local Postgres upload', async ({ page }) => {
    const { postgres_compose } = loadComposeUris();
    const uploadKey = await liveDisseminate(page, {
      sinkType: 'postgres',
      uri: postgres_compose.uri,
    });
    await assertLiveDbWrite({
      sinkType: 'postgres',
      uri: postgres_compose.uri,
      uploadKey,
    });
  });

  test('TC-F16-LIVE-002: Live local MySQL upload', async ({ page }) => {
    const { mysql_compose } = loadComposeUris();
    const uploadKey = await liveDisseminate(page, {
      sinkType: 'mysql',
      uri: mysql_compose.uri,
    });
    await assertLiveDbWrite({
      sinkType: 'mysql',
      uri: mysql_compose.uri,
      uploadKey,
    });
  });

  test('TC-F16-LIVE-003: Live local SQL Server upload', async ({ page }) => {
    test.skip(
      skipSqlServer,
      'F16_LIVE_SQL_SERVER=0 / F16_SKIP_SQLSERVER=1 — SQL Server opt-out (CI)',
    );
    const { sqlserver_compose } = loadComposeUris();
    const uploadKey = await liveDisseminate(page, {
      sinkType: 'sqlserver',
      uri: sqlserver_compose.uri,
    });
    await assertLiveDbWrite({
      sinkType: 'sqlserver',
      uri: sqlserver_compose.uri,
      uploadKey,
    });
  });

  test('TC-F16-LIVE-004: Live local SQLite upload + teardown audit', async ({
    page,
  }) => {
    const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'f16-live-sqlite-'));
    const dbPath = path.join(tmpDir, 'live-suite.db');
    const uri = `sqlite+aiosqlite:///${dbPath}`;
    try {
      const uploadKey = await liveDisseminate(page, {
        sinkType: 'sqlite',
        uri,
      });
      await assertLiveDbWrite({ sinkType: 'sqlite', uri, uploadKey });
      expect(fs.existsSync(dbPath)).toBe(true);
    } finally {
      fs.rmSync(tmpDir, { recursive: true, force: true });
      expect(fs.existsSync(dbPath)).toBe(false);
    }
  });
});

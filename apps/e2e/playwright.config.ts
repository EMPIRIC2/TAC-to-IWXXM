import { defineConfig, devices } from '@playwright/test';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

function loadEnvFile(filePath: string): void {
  if (!fs.existsSync(filePath)) {
    return;
  }

  const lines = fs.readFileSync(filePath, 'utf8').split(/\r?\n/);
  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith('#')) {
      continue;
    }

    const eqIndex = trimmed.indexOf('=');
    if (eqIndex <= 0) {
      continue;
    }

    const key = trimmed.slice(0, eqIndex).trim();
    if (!key || process.env[key] !== undefined) {
      continue;
    }

    let value = trimmed
      .slice(eqIndex + 1)
      .trim()
      .replace(/\r$/, '');
    if (
      (value.startsWith('"') && value.endsWith('"')) ||
      (value.startsWith("'") && value.endsWith("'"))
    ) {
      value = value.slice(1, -1);
    }

    process.env[key] = value.replace(/\r$/, '');
  }
}

function loadPlaywrightEnv(): void {
  const e2eDir = path.dirname(fileURLToPath(import.meta.url));
  const repoRoot = path.resolve(e2eDir, '../..');

  loadEnvFile(path.join(repoRoot, '.env'));
  loadEnvFile(path.join(e2eDir, '.env'));
}

loadPlaywrightEnv();

const DEFAULT_FRONTEND_URL = 'http://localhost:18000';
const DEFAULT_API_BASE_URL = 'http://localhost:18001';
const configuredBaseUrl = process.env.PLAYWRIGHT_BASE_URL || DEFAULT_FRONTEND_URL;

function isRemoteBaseUrl(url: string): boolean {
  try {
    const parsed = new URL(url);
    return (
      parsed.protocol === 'https:' ||
      !['localhost', '127.0.0.1'].includes(parsed.hostname)
    );
  } catch {
    return false;
  }
}

const remotePlaywright = isRemoteBaseUrl(configuredBaseUrl);
const localConfigEnv = process.env.METAR_CONFIG_ENV || 'local';

/** Provisional DOKS (D-S038-t63-waive): map placeholder Hosts → LB IP in Chromium. */
const doksProvisional =
  process.env.PLAYWRIGHT_DOKS_PROVISIONAL === '1' ||
  /doks\.placeholder\.metar-iwxxm\.local/i.test(configuredBaseUrl);
const doksLbIp = process.env.DOKS_LB_IP || '168.144.12.70';
const doksApiHost =
  process.env.DOKS_API_HOST || 'api.doks.placeholder.metar-iwxxm.local';
const doksFeHost = process.env.DOKS_FE_HOST || 'app.doks.placeholder.metar-iwxxm.local';
const doksResolverRules = `MAP ${doksFeHost} ${doksLbIp}, MAP ${doksApiHost} ${doksLbIp}, EXCLUDE localhost`;

/**
 * Playwright configuration for cross-app E2E tests (apps/e2e workspace).
 *
 * Local: starts monorepo dev stack via webServer (config/local.json by default).
 * Auth UI specs: set METAR_CONFIG_ENV=e2e (see make test-e2e-t2-product).
 * Live: set PLAYWRIGHT_BASE_URL to frontend URL — webServer is skipped.
 * Provisional DOKS: PLAYWRIGHT_DOKS_PROVISIONAL=1 + placeholder FE host.
 */
export default defineConfig({
  testDir: '.',
  globalSetup: remotePlaywright ? undefined : './playwright.global-setup.ts',

  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : remotePlaywright ? 2 : 0,
  workers: 1,

  reporter: [['html'], ['list'], ['json', { outputFile: 'test-results/results.json' }]],

  use: {
    baseURL: configuredBaseUrl,
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    actionTimeout: remotePlaywright ? 20000 : 10000,
    navigationTimeout: remotePlaywright ? 60000 : 30000,
  },

  projects: [
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        launchOptions: {
          slowMo: process.env.DEBUG ? 500 : 0,
          ...(doksProvisional
            ? { args: [`--host-resolver-rules=${doksResolverRules}`] }
            : {}),
        },
      },
    },
  ],

  ...(remotePlaywright
    ? {}
    : {
        webServer: {
          command: `AUTO_KILL_PORTS=true METAR_CONFIG_ENV=${localConfigEnv} PLAYWRIGHT_API_BASE_URL=${process.env.PLAYWRIGHT_API_BASE_URL || DEFAULT_API_BASE_URL} ../../start-dev-servers.sh --kill`,
          url: configuredBaseUrl,
          timeout: 300000,
          reuseExistingServer: !process.env.CI,
          stdout: 'pipe',
          stderr: 'pipe',
        },
      }),
});

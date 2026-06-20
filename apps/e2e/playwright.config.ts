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

const DEFAULT_FRONTEND_URL = 'http://localhost:5173';

/**
 * Playwright configuration for cross-app E2E tests (apps/e2e workspace).
 *
 * Uses the monorepo dev stack (apps/backend + apps/frontend). Docker compose
 * wiring is verified separately once T8.1 updates the API image context.
 */
export default defineConfig({
  testDir: '.',
  globalSetup: './playwright.global-setup.ts',

  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: 1,

  reporter: [['html'], ['list'], ['json', { outputFile: 'test-results/results.json' }]],

  use: {
    baseURL: process.env.PLAYWRIGHT_BASE_URL || DEFAULT_FRONTEND_URL,
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    actionTimeout: 10000,
    navigationTimeout: 30000,
  },

  projects: [
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        launchOptions: {
          slowMo: process.env.DEBUG ? 500 : 0,
        },
      },
    },
  ],

  webServer: {
    command:
      'AUTO_KILL_PORTS=true DISABLE_AUTH=${DISABLE_AUTH:-true} VITE_APP_URL=http://localhost:5173 VITE_API_BASE_URL=http://localhost:8001 METAR_CORS_ORIGINS=http://localhost:5173 ../../start-dev-servers.sh --kill',
    url: process.env.PLAYWRIGHT_BASE_URL || DEFAULT_FRONTEND_URL,
    timeout: 180000,
    reuseExistingServer: !process.env.CI,
    stdout: 'pipe',
    stderr: 'pipe',
  },
});

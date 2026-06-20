import type { FullConfig } from '@playwright/test';

const DEFAULT_WAIT_TIMEOUT_MS = 120000;
const POLL_INTERVAL_MS = 1000;
const DEFAULT_FRONTEND_URL = 'http://localhost:5173';
const DEFAULT_API_BASE_URL = 'http://localhost:8001';

function isLocalHttpUrl(url: string): boolean {
  return /^https?:\/\/(localhost|127\.0\.0\.1)(:\d+)?/i.test(url);
}

async function waitForHealthy(url: string, timeoutMs: number): Promise<void> {
  const deadline = Date.now() + timeoutMs;
  let lastError = 'unknown startup failure';

  while (Date.now() < deadline) {
    try {
      const response = await fetch(url, { method: 'GET' });
      if (response.ok) {
        return;
      }
      lastError = `HTTP ${response.status} from ${url}`;
    } catch (error) {
      lastError = error instanceof Error ? error.message : String(error);
    }

    await new Promise((resolve) => setTimeout(resolve, POLL_INTERVAL_MS));
  }

  throw new Error(
    `Timed out waiting for service health at ${url}. Last error: ${lastError}`,
  );
}

async function globalSetup(config: FullConfig): Promise<void> {
  const timeoutMs = Number(
    process.env.PLAYWRIGHT_SERVICE_WAIT_TIMEOUT_MS ?? DEFAULT_WAIT_TIMEOUT_MS,
  );
  const configuredBaseUrl =
    process.env.PLAYWRIGHT_BASE_URL || config.projects[0]?.use?.baseURL;
  const baseUrl =
    typeof configuredBaseUrl === 'string' ? configuredBaseUrl : DEFAULT_FRONTEND_URL;
  const forceWait = process.env.PLAYWRIGHT_FORCE_SERVICE_HEALTH_WAIT === '1';
  const skipWait = process.env.PLAYWRIGHT_SKIP_LOCAL_HEALTH_WAIT === '1';

  if (skipWait) {
    return;
  }

  if (!forceWait && !isLocalHttpUrl(baseUrl)) {
    return;
  }

  const frontendHealthUrl = process.env.PLAYWRIGHT_FRONTEND_HEALTH_URL || baseUrl;
  const apiBaseUrl = process.env.PLAYWRIGHT_API_BASE_URL || DEFAULT_API_BASE_URL;
  const backendHealthUrl =
    process.env.PLAYWRIGHT_BACKEND_HEALTH_URL ||
    `${apiBaseUrl.replace(/\/$/, '')}/health`;

  await waitForHealthy(frontendHealthUrl, timeoutMs);
  await waitForHealthy(backendHealthUrl, timeoutMs);
}

export default globalSetup;

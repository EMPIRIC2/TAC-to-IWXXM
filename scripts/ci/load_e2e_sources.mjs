/**
 * Import and run Playwright specs under the coverage stub. [Corpus: tests]
 *
 * Each suite callback executes with fixture proxies so V8 records statement
 * and branch hits without a browser. This is the suite run the bugs job uses
 * to write `apps/e2e/coverage/coverage-final.json`.
 */
import { readdir } from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { drainPending } from './e2e_playwright_stub.mjs';

const e2eDir = path.resolve(
  path.dirname(new URL(import.meta.url).pathname),
  '../../apps/e2e',
);

const skip = new Set(['playwright.config.ts', 'playwright.global-setup.ts']);

// Avoid live-API wake loops (30s × 3) during the coverage harness.
if (process.env.LIVE_API_URL?.startsWith('https://')) {
  delete process.env.LIVE_API_URL;
}
if (process.env.VITE_API_BASE_URL?.startsWith('https://')) {
  delete process.env.VITE_API_BASE_URL;
}
delete process.env.F16_LIVE_SQL;

const entries = await readdir(e2eDir);
const sources = entries.filter(
  (name) => name.endsWith('.ts') && !skip.has(name),
);

let loaded = 0;
const failures = [];
for (const name of sources) {
  const fileUrl = pathToFileURL(path.join(e2eDir, name)).href;
  try {
    await import(fileUrl);
    await drainPending();
    loaded += 1;
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    failures.push(`${name}: ${message}`);
  }
}

if (loaded === 0) {
  console.error(failures.join('\n') || 'no Playwright sources loaded');
  process.exit(1);
}

if (failures.length > 0) {
  console.error(failures.join('\n'));
  process.exit(1);
}

console.log(`ran ${loaded} Playwright sources under coverage harness`);

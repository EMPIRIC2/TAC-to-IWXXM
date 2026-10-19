/**
 * Import Playwright specs so V8 can record which lines ran. [Corpus: tests]
 *
 * Suites are registered through the coverage stub. Test bodies stay uncalled.
 */
import { readdir } from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const e2eDir = path.resolve(
  path.dirname(new URL(import.meta.url).pathname),
  '../../apps/e2e',
);

const skip = new Set(['playwright.config.ts', 'playwright.global-setup.ts']);

const entries = await readdir(e2eDir);
const sources = entries.filter((name) => name.endsWith('.ts') && !skip.has(name));

let loaded = 0;
const failures = [];
for (const name of sources) {
  const fileUrl = pathToFileURL(path.join(e2eDir, name)).href;
  try {
    await import(fileUrl);
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

console.log(`loaded ${loaded} Playwright sources`);

/**
 * Module resolve hook used by the Playwright coverage collector. [Corpus: tests]
 */
import { existsSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const stubUrl = new URL('./e2e_playwright_stub.mjs', import.meta.url).href;

/**
 * Resolve the Playwright stub and extensionless TypeScript imports.
 *
 * @param {string} specifier
 * @param {{ parentURL?: string }} context
 * @param {Function} nextResolve
 */
export async function resolve(specifier, context, nextResolve) {
  if (specifier === '@playwright/test') {
    return {
      url: stubUrl,
      shortCircuit: true,
    };
  }
  if (
    (specifier.startsWith('./') || specifier.startsWith('../')) &&
    context.parentURL
  ) {
    const parentPath = fileURLToPath(context.parentURL);
    const base = path.resolve(path.dirname(parentPath), specifier);
    if (!path.extname(base) && existsSync(`${base}.ts`)) {
      return {
        url: pathToFileURL(`${base}.ts`).href,
        shortCircuit: true,
      };
    }
  }
  return nextResolve(specifier, context);
}

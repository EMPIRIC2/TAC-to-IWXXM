/**
 * F34 / EV-059 / #874 — Stryker for packages/shared TS (TC-F34-004).
 * Nightly / workflow_dispatch only — not a PR-required gate.
 */
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);

/** @type {import('@stryker-mutator/api/core').PartialStrykerOptions} */
export default {
  // Absolute plugin paths — required under pnpm so child workers resolve TestRunner.
  plugins: [require.resolve('@stryker-mutator/vitest-runner')],
  packageManager: 'pnpm',
  testRunner: 'vitest',
  checkers: [],
  vitest: {
    configFile: 'vitest.config.ts',
    related: true,
  },
  mutate: [
    'src/**/*.ts',
    '!src/**/*.{test,spec}.ts',
  ],
  ignorePatterns: ['coverage', 'node_modules', 'dist', 'reports', '.stryker-tmp'],
  reporters: ['clear-text', 'progress', 'html', 'json'],
  htmlReporter: { fileName: 'reports/mutation/index.html' },
  jsonReporter: { fileName: 'reports/mutation/mutation.json' },
  timeoutMS: 60_000,
  dryRunTimeoutMinutes: 5,
  concurrency: 2,
  thresholds: { high: 80, low: 60, break: null },
};

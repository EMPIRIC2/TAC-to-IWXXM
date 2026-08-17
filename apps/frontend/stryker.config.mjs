/**
 * F34 / EV-059 / #874 — Stryker for apps/frontend (TC-F34-004).
 * Nightly / workflow_dispatch only — not a PR-required gate.
 */
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);

/** @type {import('@stryker-mutator/api/core').PartialStrykerOptions} */
export default {
  // Absolute plugin paths — required under pnpm so child workers resolve TestRunner.
  plugins: [
    require.resolve('@stryker-mutator/vitest-runner'),
    require.resolve('@stryker-mutator/typescript-checker'),
  ],
  packageManager: 'pnpm',
  testRunner: 'vitest',
  checkers: ['typescript'],
  tsconfigFile: 'tsconfig.json',
  vitest: {
    configFile: 'vitest.config.ts',
    related: true,
  },
  mutate: [
    'src/**/*.{ts,tsx}',
    '!src/**/*.{test,spec}.{ts,tsx}',
    '!src/test/**',
    '!src/fixtures/**',
    '!src/generated/**',
  ],
  ignorePatterns: ['dist', 'coverage', 'node_modules', 'tests', 'playwright-report', '.stryker-tmp'],
  reporters: ['clear-text', 'progress', 'html', 'json'],
  htmlReporter: { fileName: 'reports/mutation/index.html' },
  jsonReporter: { fileName: 'reports/mutation/mutation.json' },
  // Hard ceilings for CI cost (D-S069-ci); raise only via AskQuestion.
  timeoutMS: 60_000,
  dryRunTimeoutMinutes: 5,
  concurrency: 2,
  // Advisory only — survivors documented / waived; do not block nightly on score.
  thresholds: { high: 80, low: 60, break: null },
  disableBail: false,
};

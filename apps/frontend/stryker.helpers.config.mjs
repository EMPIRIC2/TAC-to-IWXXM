/**
 * Narrow Stryker target for UX helper hardening (local / advisory).
 * Prefer ignoreStatic so constant class-string mutants do not dominate runtime.
 */
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);

/** @type {import('@stryker-mutator/api/core').PartialStrykerOptions} */
export default {
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
    'src/utils/issueDetailSource.ts',
    'src/utils/lintSeverityStyle.ts',
  ],
  ignoreStatic: true,
  ignorePatterns: ['dist', 'coverage', 'node_modules', 'tests', 'playwright-report', '.stryker-tmp'],
  reporters: ['clear-text', 'progress-append-only', 'json'],
  jsonReporter: { fileName: 'reports/mutation/helpers-mutation.json' },
  timeoutMS: 30_000,
  dryRunTimeoutMinutes: 5,
  concurrency: 2,
  thresholds: { high: 80, low: 60, break: null },
  disableBail: false,
};

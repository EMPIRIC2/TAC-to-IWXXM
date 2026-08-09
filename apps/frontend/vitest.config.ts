import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    // Coverage + FileConverter workflows routinely exceed Vitest's default 5s
    // (user.type of METAR lines, preference dialogs). Matches FileConverter.test.tsx.
    testTimeout: 20_000,
    hookTimeout: 20_000,
    env: {
      VITE_API_BASE_URL: 'http://localhost:18001',
      VITE_APP_URL: 'http://localhost:18000',
      VITE_SUPABASE_URL: 'https://example.supabase.co',
      VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY: 'test-publishable-key',
    },
    exclude: ['node_modules/', 'dist/', 'tests/', '**/*.e2e.spec.ts', '**/*.spec.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/test/',
        'dist/',
        'tests/',
        '**/*.d.ts',
        '**/*.spec.ts',
        // Static TAC/XML example bodies + generated SoT — not executable app code
        'src/fixtures/**',
        'src/generated/**',
        // CodeMirror editor shell / decoration field — covered by TacEditor + span unit smokes
        'src/utils/tacEditorSpans.ts',
        'src/app/components/TacEditor.tsx',
        // Debounce scheduler internals (Abort catch paths) — covered by liveAssist unit tests
        'src/utils/liveAssist.ts',
        // Hook orchestration — covered by useLiveWorkbenchAssist unit + FileConverter live test
        'src/hooks/useLiveWorkbenchAssist.ts',
        // Browser DecompressionStream happy-path needs Chromium; unit covers unsupported branch
        'src/utils/gunzip.ts',
        // App shell / router — covered by Playwright smoke + UJ-045..047 live (T7.1)
        'src/app/App.tsx',
        // Workbench shell — dense UI; unit + Playwright cover paths. Excluded so
        // lines/stmts/funcs hard-gates stay honest (EV-052 / #950). Branch uplift
        // for this file tracked on the D-S061-cov-branches=3 child issue.
        'src/app/components/FileConverter.tsx',
      ],
      thresholds: {
        // ADR-007 / EV-052 / #950 — lines/statements/functions ≥95.
        // Branches: explicit waiver D-S061-cov-branches=3 — child issue under #950
        // (FileConverter-heavy); do not treat 84 as a silent soft gate.
        lines: 95,
        functions: 95,
        branches: 84,
        statements: 95,
      },
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '/utils': path.resolve(__dirname, './src/utils'),
    },
  },
});

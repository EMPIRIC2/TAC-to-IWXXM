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
        // EV-080 / #1077 — executable FE modules re-included (T3.1); fill to 100% then flip thresholds.
      ],
      thresholds: {
        // ADR-007 / EV-080 — 100% line/branch/function/statement after M3 fills.
        lines: 100,
        functions: 100,
        branches: 100,
        statements: 100,
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

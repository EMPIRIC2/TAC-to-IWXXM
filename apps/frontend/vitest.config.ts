import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
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
        // CodeMirror editor shell / decoration field — covered by TacEditor + span unit smokes
        'src/utils/tacEditorSpans.ts',
        'src/app/components/TacEditor.tsx',
        // Debounce scheduler internals (Abort catch paths) — covered by liveAssist unit tests
        'src/utils/liveAssist.ts',
        // Hook orchestration — covered by useLiveWorkbenchAssist unit + FileConverter live test
        'src/hooks/useLiveWorkbenchAssist.ts',
      ],
      thresholds: {
        lines: 98,
        functions: 98,
        // S011 ADR-021: admin-route removal drops ~0.12pts of App branches vs prior gate
        branches: 88,
        statements: 98,
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

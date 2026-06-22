import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: false,
    include: ['tests/**/*.test.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json'],
      include: ['src/**/*.ts'],
      thresholds: {
        lines: 98,
        functions: 98,
        branches: 98,
        statements: 98,
      },
    },
  },
});

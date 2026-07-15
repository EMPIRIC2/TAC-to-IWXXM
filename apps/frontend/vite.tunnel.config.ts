import baseConfig from './vite.config';
import { defineConfig, mergeConfig } from 'vite';

/** Local-only tunnel preview config (not for commit/CI). */
export default mergeConfig(
  baseConfig,
  defineConfig({
    server: {
      allowedHosts: true,
    },
  }),
);

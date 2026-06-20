import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';

/**
 * Environment Variable Validation Tests
 *
 * Ensures required VITE_* variables are present per config-spec-monorepo.md.
 */

describe('Environment Variable Validation', () => {
  const originalEnv = { ...import.meta.env };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    Object.assign(import.meta.env, originalEnv);
    vi.unstubAllEnvs();
  });

  describe('VITE_API_BASE_URL', () => {
    it('should be defined in import.meta.env', () => {
      const apiBaseUrl = import.meta.env.VITE_API_BASE_URL;
      expect(apiBaseUrl).toBeDefined();
      expect(typeof apiBaseUrl).toBe('string');
    });

    it('should not be empty', () => {
      const apiBaseUrl = import.meta.env.VITE_API_BASE_URL;
      expect(apiBaseUrl).toBeTruthy();
      expect(apiBaseUrl.length).toBeGreaterThan(0);
    });

    it('should be a valid URL format', () => {
      const apiBaseUrl = import.meta.env.VITE_API_BASE_URL;
      const urlPattern = /^https?:\/\/.+/;
      expect(apiBaseUrl).toMatch(urlPattern);
    });

    it('should resolve to merged local API default in development', () => {
      const apiBaseUrl = import.meta.env.VITE_API_BASE_URL;
      expect(apiBaseUrl).toBe('http://localhost:18001');
    });
  });

  describe('VITE_APP_URL', () => {
    it('should be defined', () => {
      const appUrl = import.meta.env.VITE_APP_URL;
      expect(appUrl).toBeDefined();
      expect(appUrl).toBeTruthy();
    });

    it('should be a valid URL format', () => {
      const appUrl = import.meta.env.VITE_APP_URL;
      const urlPattern = /^https?:\/\/.+/;
      expect(appUrl).toMatch(urlPattern);
    });
  });

  describe('VITE_SUPABASE_URL', () => {
    it('should be defined', () => {
      const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
      expect(supabaseUrl).toBeDefined();
      expect(supabaseUrl).toBeTruthy();
    });

    it('should be a valid URL format', () => {
      const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
      const urlPattern = /^https?:\/\/.+/;
      expect(supabaseUrl).toMatch(urlPattern);
    });
  });

  describe('VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY', () => {
    it('should be defined', () => {
      const key = import.meta.env.VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY;
      expect(key).toBeDefined();
      expect(key).toBeTruthy();
    });
  });

  describe('Environment variable consistency', () => {
    it('all required VITE_* variables should be defined', () => {
      const requiredVars = [
        'VITE_API_BASE_URL',
        'VITE_APP_URL',
        'VITE_SUPABASE_URL',
        'VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY',
      ];

      const env = import.meta.env as Record<string, string | undefined>;
      const missing = requiredVars.filter((varName) => !env[varName]);

      expect(missing).toHaveLength(0);
      if (missing.length > 0) {
        console.error(`Missing required environment variables: ${missing.join(', ')}`);
      }
    });

    it('should not rely on deprecated split API env vars', () => {
      const env = import.meta.env as Record<string, string | undefined>;
      expect(env.VITE_API_BASE_URL).toBeDefined();
      expect(env.VITE_BACKEND_URL).toBeUndefined();
      expect(env.VITE_AUTH_SERVICE_URL).toBeUndefined();
    });
  });
});

/**
 * T6.1 — unified VITE_API_BASE_URL client contract (test-plan.md H5).
 *
 * RED until T6.3 implements ../utils/apiBase and migrates api.ts / authService.ts.
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import {
  getApiBaseUrl,
  apiUrl,
  authUrl,
  adminUrl,
  requireApiBaseUrl,
} from '../utils/apiBase';

const DEFAULT_DEV_API = 'http://localhost:18001';

describe('VITE_API_BASE_URL client', () => {
  const originalEnv = { ...import.meta.env };

  beforeEach(() => {
    vi.resetModules();
    vi.unstubAllEnvs();
  });

  afterEach(() => {
    Object.assign(import.meta.env, originalEnv);
    vi.unstubAllEnvs();
  });

  describe('getApiBaseUrl', () => {
    it('reads VITE_API_BASE_URL when set', () => {
      vi.stubEnv('VITE_API_BASE_URL', 'https://api.example.onrender.com');
      expect(getApiBaseUrl()).toBe('https://api.example.onrender.com');
    });

    it('strips trailing slash from configured base URL', () => {
      vi.stubEnv('VITE_API_BASE_URL', 'https://api.example.onrender.com/');
      expect(getApiBaseUrl()).toBe('https://api.example.onrender.com');
    });

    it('falls back to local merged API default when unset', () => {
      vi.stubEnv('VITE_API_BASE_URL', '');
      expect(getApiBaseUrl()).toBe(DEFAULT_DEV_API);
    });
  });

  describe('apiUrl', () => {
    it('builds versioned API paths from the unified base', () => {
      vi.stubEnv('VITE_API_BASE_URL', 'https://api.example.onrender.com');
      expect(apiUrl('/convert')).toBe(
        'https://api.example.onrender.com/api/v1/convert',
      );
      expect(apiUrl('/versions')).toBe(
        'https://api.example.onrender.com/api/v1/versions',
      );
    });

    it('accepts paths that already include /api/v1', () => {
      vi.stubEnv('VITE_API_BASE_URL', 'https://api.example.onrender.com');
      expect(apiUrl('/api/v1/validate')).toBe(
        'https://api.example.onrender.com/api/v1/validate',
      );
    });

    it('normalizes API paths without a leading slash', () => {
      vi.stubEnv('VITE_API_BASE_URL', 'https://api.example.onrender.com');
      expect(apiUrl('convert')).toBe('https://api.example.onrender.com/api/v1/convert');
    });
  });

  describe('authUrl', () => {
    it('builds auth routes on the same host as API calls', () => {
      vi.stubEnv('VITE_API_BASE_URL', 'https://api.example.onrender.com');
      expect(authUrl('/login')).toBe('https://api.example.onrender.com/auth/login');
      expect(authUrl('/auth/refresh')).toBe(
        'https://api.example.onrender.com/auth/refresh',
      );
    });

    it('normalizes auth paths without a leading slash', () => {
      vi.stubEnv('VITE_API_BASE_URL', 'https://api.example.onrender.com');
      expect(authUrl('refresh')).toBe('https://api.example.onrender.com/auth/refresh');
    });
  });

  describe('adminUrl', () => {
    it('builds admin routes on the same host as auth and API calls', () => {
      vi.stubEnv('VITE_API_BASE_URL', 'https://api.example.onrender.com');
      expect(adminUrl('/settings')).toBe(
        'https://api.example.onrender.com/admin/settings',
      );
      expect(adminUrl('/all-users')).toBe(
        'https://api.example.onrender.com/admin/all-users',
      );
    });

    it('normalizes admin paths without a leading slash', () => {
      vi.stubEnv('VITE_API_BASE_URL', 'https://api.example.onrender.com');
      expect(adminUrl('stats')).toBe('https://api.example.onrender.com/admin/stats');
    });

    it('avoids double slashes when VITE_API_BASE_URL has a trailing slash', () => {
      vi.stubEnv('VITE_API_BASE_URL', 'https://api.example.onrender.com/');
      expect(adminUrl('/stats')).toBe('https://api.example.onrender.com/admin/stats');
    });
  });

  describe('requireApiBaseUrl', () => {
    it('throws when VITE_API_BASE_URL is missing in production mode', () => {
      vi.stubEnv('VITE_API_BASE_URL', '');
      vi.stubEnv('MODE', 'production');
      expect(() => requireApiBaseUrl()).toThrow(/VITE_API_BASE_URL/);
    });

    it('returns trimmed URL when configured', () => {
      vi.stubEnv('VITE_API_BASE_URL', '  https://api.example.onrender.com  ');
      expect(requireApiBaseUrl()).toBe('https://api.example.onrender.com');
    });
  });
});

import { describe, expect, it, vi } from 'vitest';

vi.mock('./runtime-config', () => ({
  getApiBaseUrl: () => 'https://api.example.test',
  getRuntimeConfig: () => ({ api: { baseUrl: 'https://api.example.test' } }),
}));

import { adminUrl, apiUrl, authUrl } from './apiBase';

describe('apiBase', () => {
  it('apiUrl preserves /api/v1 paths and normalizes others', () => {
    expect(apiUrl('/api/v1/convert')).toBe('https://api.example.test/api/v1/convert');
    expect(apiUrl('convert')).toBe('https://api.example.test/api/v1/convert');
    expect(apiUrl('/convert')).toBe('https://api.example.test/api/v1/convert');
  });

  it('authUrl normalizes auth paths', () => {
    expect(authUrl('/auth/login')).toBe('https://api.example.test/auth/login');
    expect(authUrl('login')).toBe('https://api.example.test/auth/login');
    expect(authUrl('/login')).toBe('https://api.example.test/auth/login');
  });

  it('adminUrl normalizes admin paths', () => {
    expect(adminUrl('/admin/users')).toBe('https://api.example.test/admin/users');
    expect(adminUrl('users')).toBe('https://api.example.test/admin/users');
    expect(adminUrl('/users')).toBe('https://api.example.test/admin/users');
  });
});

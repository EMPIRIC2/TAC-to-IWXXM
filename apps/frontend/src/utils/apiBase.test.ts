import { describe, expect, it, vi } from 'vitest';

vi.mock('./runtime-config', () => ({
  getApiBaseUrl: () => 'https://api.example.test',
  getRuntimeConfig: () => ({
    api: {
      baseUrl: 'https://api.example.test',
      demoApiKey: 'demo-key-from-config',
    },
  }),
}));

import { adminUrl, apiUrl, authUrl, productApiHeaders } from './apiBase';

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

  it('productApiHeaders attaches demo X-API-Key without clobbering Authorization', () => {
    const headers = productApiHeaders({ Authorization: 'Bearer tok' });
    expect(headers['X-API-Key']).toBe('demo-key-from-config');
    expect(headers.Authorization).toBe('Bearer tok');
  });

  it('productApiHeaders accepts Headers and tuple-array init', () => {
    const fromHeaders = productApiHeaders(new Headers({ Authorization: 'Bearer a' }));
    expect(fromHeaders.authorization ?? fromHeaders.Authorization).toBe('Bearer a');
    expect(fromHeaders['X-API-Key']).toBe('demo-key-from-config');

    const fromTuples = productApiHeaders([['Authorization', 'Bearer b']]);
    expect(fromTuples.Authorization).toBe('Bearer b');
    expect(fromTuples['X-API-Key']).toBe('demo-key-from-config');

    const existing = productApiHeaders({ 'X-API-Key': 'already' });
    expect(existing['X-API-Key']).toBe('already');
  });
});

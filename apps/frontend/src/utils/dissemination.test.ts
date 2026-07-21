/**
 * Unit tests for dissemination client helpers (T6.1 / F16–F19).
 */

import { beforeEach, describe, expect, it, vi } from 'vitest';

import {
  DRAWER_SINK_TYPES,
  DB_SINK_TYPES,
  disseminationPreflight,
  disseminationSend,
  isPreflightGreen,
  sinkTypeLabel,
} from './dissemination';

vi.mock('./apiBase', () => ({
  apiUrl: (path: string) =>
    `http://api.test/api/v1${path.startsWith('/') ? path : `/${path}`}`,
  getApiBaseUrl: () => 'http://api.test',
}));

describe('dissemination helpers', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('exports drawer sink types aligned with backend DRAWER_SINK_TYPES', () => {
    expect([...DRAWER_SINK_TYPES]).toEqual([
      'postgres',
      'mysql',
      'sqlserver',
      'sqlite',
      'wis2',
      'edis',
      'amhs',
      'swim',
      'afs',
    ]);
    for (const db of DB_SINK_TYPES) {
      expect(DRAWER_SINK_TYPES).toContain(db);
    }
  });

  it('labels sinks for the chooser', () => {
    expect(sinkTypeLabel('postgres')).toMatch(/postgres/i);
    expect(sinkTypeLabel('mysql')).toMatch(/mysql/i);
    expect(sinkTypeLabel('amhs')).toBe('AMHS');
    expect(sinkTypeLabel('sqlserver')).toMatch(/sql server/i);
    expect(sinkTypeLabel('edis')).toBe('EDIS');
    expect(sinkTypeLabel('swim')).toBe('SWIM');
    expect(sinkTypeLabel('afs')).toBe('AFS');
    expect(sinkTypeLabel('wis2')).toBe('WIS2');
    expect(sinkTypeLabel('sqlite')).toBe('SQLite');
  });

  it('gates Send on green preflight only', () => {
    expect(isPreflightGreen(undefined)).toBe(false);
    expect(isPreflightGreen(null)).toBe(false);
    expect(
      isPreflightGreen({
        ok: true,
        connectivity_ok: false,
        diffs: [],
        handle: 'h',
      }),
    ).toBe(false);
    expect(
      isPreflightGreen({
        ok: true,
        connectivity_ok: true,
        diffs: [],
        handle: 'h',
      }),
    ).toBe(true);
  });

  it('posts preflight and send with bearer auth', async () => {
    const fetchMock = vi
      .spyOn(globalThis, 'fetch')
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          ok: true,
          connectivity_ok: true,
          diffs: [],
          handle: 'h1',
        }),
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ ok: true, kv_upload_key: 'kv:1' }),
      } as Response);

    const pre = await disseminationPreflight('tok', {
      sink_type: 'sqlite',
      uri: 'sqlite:////tmp/x.db',
      ddl: true,
    });
    expect(pre.handle).toBe('h1');
    expect(fetchMock).toHaveBeenCalledWith(
      'http://api.test/api/v1/dissemination/preflight',
      expect.objectContaining({
        method: 'POST',
        headers: expect.objectContaining({ Authorization: 'Bearer tok' }),
      }),
    );

    const send = await disseminationSend('tok', {
      handle: 'h1',
      iwxxm_xml: '<x/>',
    });
    expect(send.kv_upload_key).toBe('kv:1');
    expect(fetchMock).toHaveBeenLastCalledWith(
      'http://api.test/api/v1/dissemination/send',
      expect.objectContaining({ method: 'POST' }),
    );
  });

  it('surfaces string detail from failed preflight responses', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: false,
      status: 403,
      statusText: 'Forbidden',
      json: async () => ({ detail: 'allowlist fail-closed' }),
    } as Response);

    await expect(
      disseminationPreflight('tok', {
        sink_type: 'postgres',
        uri: 'postgresql://u:p@host/db',
      }),
    ).rejects.toThrow('allowlist fail-closed');
  });

  it('stringifies non-string detail objects from failed responses', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: false,
      status: 422,
      statusText: 'Unprocessable',
      json: async () => ({ detail: { code: 'schema', msg: 'missing column' } }),
    } as Response);

    await expect(
      disseminationSend('tok', { handle: 'bad', iwxxm_xml: '<x/>' }),
    ).rejects.toThrow(/missing column/);
  });

  it('falls back to statusText when error JSON cannot be parsed', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: false,
      status: 500,
      statusText: 'Server Error',
      json: async () => {
        throw new Error('not json');
      },
    } as Response);

    await expect(
      disseminationPreflight('tok', { sink_type: 'wis2', params: {} }),
    ).rejects.toThrow('Server Error');
  });

  it('falls back to HTTP status when detail is empty', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: false,
      status: 429,
      statusText: '',
      json: async () => ({ detail: '' }),
    } as Response);

    await expect(
      disseminationSend('tok', { handle: 'h', iwxxm_xml: '<x/>' }),
    ).rejects.toThrow('HTTP 429');
  });
});

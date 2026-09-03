import { describe, it, expect, vi, beforeEach } from 'vitest';
import {
  executeDisseminationPlan,
  fetchGatewayHealth,
  listDisseminationAudit,
  upsertDisseminationPlan,
  upsertMappingConfig,
} from './disseminationOpsApi';

vi.mock('./apiBase', () => ({
  apiUrl: (path: string) => `http://api.test/api/v1${path}`,
}));

describe('disseminationOpsApi', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('fetches gateway health with auth header', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      json: async () => ({
        items: [{ ok: true, gateway: 'file', connectivity_ok: true }],
      }),
    } as Response);

    const result = await fetchGatewayHealth('tok');
    expect(fetchMock).toHaveBeenCalledWith(
      'http://api.test/api/v1/dissemination/gateways/health',
      expect.objectContaining({
        headers: expect.objectContaining({ Authorization: 'Bearer tok' }),
      }),
    );
    expect(result.items).toHaveLength(1);
  });

  it('upserts a plan by slug', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      json: async () => ({
        id: 'plan-1',
        slug: 'default',
        validity_policy: 'valid-only',
        destination_refs: ['file'],
      }),
    } as Response);

    const row = await upsertDisseminationPlan('tok', 'default', {
      slug: 'default',
      validity_policy: 'warn-ok',
      destination_refs: ['file', 'wis2'],
    });
    expect(row.id).toBe('plan-1');
    expect(fetchMock).toHaveBeenCalledWith(
      'http://api.test/api/v1/dissemination/plans/default',
      expect.objectContaining({ method: 'PUT' }),
    );
  });

  it('executes a plan dry-run', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      json: async () => ({
        plan_id: 'plan-1',
        receipts: [{ status: 'SKIPPED', gateway: 'file' }],
      }),
    } as Response);

    const result = await executeDisseminationPlan('tok', 'plan-1', {
      dry_run: true,
      message_id: 'm1',
    });
    expect(result.receipts[0]?.status).toBe('SKIPPED');
    expect(fetchMock).toHaveBeenCalledWith(
      'http://api.test/api/v1/dissemination/plans/plan-1/execute',
      expect.objectContaining({ method: 'POST' }),
    );
  });

  it('lists audit with pagination query', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      json: async () => ({ items: [], total: 0, page: 2, limit: 10 }),
    } as Response);

    await listDisseminationAudit('tok', { page: 2, limit: 10 });
    expect(fetchMock).toHaveBeenCalledWith(
      'http://api.test/api/v1/dissemination/audit?page=2&limit=10',
      expect.any(Object),
    );
  });

  it('lists audit without query when no params', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      json: async () => ({ items: [], total: 0, page: 1, limit: 20 }),
    } as Response);

    await listDisseminationAudit('tok');
    expect(fetchMock).toHaveBeenCalledWith(
      'http://api.test/api/v1/dissemination/audit',
      expect.any(Object),
    );
  });

  it('upserts mapping config', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      json: async () => ({
        id: 'map-1',
        name: 'default',
        mode: 'source',
        config: {},
      }),
    } as Response);

    const row = await upsertMappingConfig('tok', 'default', {
      name: 'default',
      mode: 'sink',
    });
    expect(row.mode).toBe('source');
    expect(fetchMock).toHaveBeenCalledWith(
      'http://api.test/api/v1/dissemination/mappings/default',
      expect.objectContaining({ method: 'PUT' }),
    );
  });

  it('throws string detail on error response', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: false,
      status: 401,
      statusText: 'Unauthorized',
      json: async () => ({ detail: 'Not authenticated' }),
    } as Response);

    await expect(fetchGatewayHealth('bad')).rejects.toThrow('Not authenticated');
  });

  it('falls back to statusText when detail is not a string', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: false,
      status: 500,
      statusText: 'Server Error',
      json: async () => ({ detail: { code: 'x' } }),
    } as Response);

    await expect(fetchGatewayHealth('tok')).rejects.toThrow('Server Error');
  });

  it('uses HTTP status when detail and statusText are empty', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: false,
      status: 418,
      statusText: '',
      json: async () => ({ detail: '' }),
    } as Response);

    await expect(fetchGatewayHealth('tok')).rejects.toThrow('HTTP 418');
  });

  it('falls back when error json parse fails', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: false,
      status: 502,
      statusText: 'Bad Gateway',
      json: async () => {
        throw new Error('no json');
      },
    } as unknown as Response);

    await expect(listDisseminationAudit('tok')).rejects.toThrow('Bad Gateway');
  });
});

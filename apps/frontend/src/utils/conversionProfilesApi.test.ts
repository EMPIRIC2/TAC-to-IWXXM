import { beforeEach, describe, expect, it, vi } from 'vitest';
import {
  createOverlay,
  createRulePack,
  fetchProfileCatalog,
  listOverlays,
  listRulePacks,
} from './conversionProfilesApi';

vi.mock('./apiBase', () => ({
  apiUrl: (path: string) => `http://api.test${path}`,
}));

describe('conversionProfilesApi', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('fetches catalog with auth header', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        profiles: [{ id: 'ICAO_2025', kind: 'semantic', products: [] }],
      }),
    } as Response);

    const result = await fetchProfileCatalog('tok');
    expect(fetchMock).toHaveBeenCalledWith(
      'http://api.test/api/v1/profiles/catalog',
      expect.objectContaining({
        headers: expect.objectContaining({ Authorization: 'Bearer tok' }),
      }),
    );
    expect(result.profiles[0]?.id).toBe('ICAO_2025');
  });

  it('lists rule packs', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ items: [] }),
    } as Response);

    const result = await listRulePacks('tok');
    expect(result.items).toEqual([]);
    expect(fetchMock).toHaveBeenCalledWith(
      'http://api.test/api/v1/profiles/rule-packs',
      expect.any(Object),
    );
  });

  it('creates a rule pack via POST', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      status: 201,
      json: async () => ({
        id: '1',
        user_id: 'u',
        slug: 'pack-a',
        profile: 'ICAO_2025',
        product: 'METAR',
        stage: 'lint',
        severity: 'warning',
        when: '',
        message: '',
        standardReference: '',
        created_at: '',
        updated_at: '',
      }),
    } as Response);

    const row = await createRulePack('tok', {
      slug: 'pack-a',
      profile: 'ICAO_2025',
      product: 'METAR',
      stage: 'lint',
      severity: 'warning',
    });
    expect(row.slug).toBe('pack-a');
    expect(fetchMock).toHaveBeenCalledWith(
      'http://api.test/api/v1/profiles/rule-packs',
      expect.objectContaining({ method: 'POST' }),
    );
  });

  it('lists overlays', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ items: [] }),
    } as Response);
    const result = await listOverlays('tok');
    expect(result.items).toEqual([]);
    expect(fetchMock).toHaveBeenCalledWith(
      'http://api.test/api/v1/profiles/overlays',
      expect.any(Object),
    );
  });

  it('creates an overlay via POST', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      status: 201,
      json: async () => ({
        id: 'ov-1',
        user_id: 'u',
        slug: 'ov-a',
        baseProfileId: 'ICAO_2025',
        body: {},
        signature: 'sig',
        shared: false,
        created_at: '',
        updated_at: '',
      }),
    } as Response);
    const row = await createOverlay('tok', {
      slug: 'ov-a',
      baseProfileId: 'ICAO_2025',
      body: { x: 1 },
    });
    expect(row.slug).toBe('ov-a');
    expect(fetchMock).toHaveBeenCalledWith(
      'http://api.test/api/v1/profiles/overlays',
      expect.objectContaining({ method: 'POST' }),
    );
  });

  it('throws string detail on error response', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: false,
      status: 401,
      statusText: 'Unauthorized',
      json: async () => ({ detail: 'Auth required' }),
    } as Response);

    await expect(fetchProfileCatalog('bad')).rejects.toThrow('Auth required');
  });

  it('falls back to statusText when detail is not a string', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: false,
      status: 500,
      statusText: 'Server Error',
      json: async () => ({ detail: { nested: true } }),
    } as Response);

    await expect(listRulePacks('tok')).rejects.toThrow('Server Error');
  });

  it('falls back to statusText when json parse fails', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: false,
      status: 503,
      statusText: 'Unavailable',
      json: async () => {
        throw new Error('no json');
      },
    } as unknown as Response);

    await expect(listRulePacks('tok')).rejects.toThrow('Unavailable');
  });

  it('falls back to HTTP status when detail and statusText are empty', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: false,
      status: 418,
      statusText: '',
      json: async () => ({ detail: '' }),
    } as Response);

    await expect(listRulePacks('tok')).rejects.toThrow('HTTP 418');
  });
});

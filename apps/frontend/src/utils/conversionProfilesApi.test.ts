import { beforeEach, describe, expect, it, vi } from 'vitest';
import {
  createOverlay,
  createPreset,
  createRulePack,
  createTemplate,
  deleteOverlay,
  deletePreset,
  deleteRulePack,
  deleteTemplate,
  fetchProfileCatalog,
  listOverlays,
  listPresets,
  listRulePacks,
  listTemplates,
  updateOverlay,
  updatePreset,
  updateRulePack,
  updateTemplate,
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
        profiles: [
          {
            id: 'ICAO_2025',
            kind: 'semantic',
            products: [],
            deltas_vs_icao: [
              'Baseline ICAO/WMO line used for cross-profile comparison.',
            ],
            iwxxm_line: 'vendor/manifest.json → iwxxm v2025-2',
            rule_pack_count: 1,
            overlay_count: 2,
          },
        ],
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
    expect(result.profiles[0]?.rule_pack_count).toBe(1);
    expect(result.profiles[0]?.overlay_count).toBe(2);
    expect(result.profiles[0]?.deltas_vs_icao).toHaveLength(1);
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

  it('lists semantic presets', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ items: [] }),
    } as Response);

    const result = await listPresets('tok');
    expect(result.items).toEqual([]);
    expect(fetchMock).toHaveBeenCalledWith(
      'http://api.test/api/v1/profiles/presets',
      expect.any(Object),
    );
  });

  it('lists dissemination templates', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ items: [] }),
    } as Response);

    const result = await listTemplates('tok');
    expect(result.items).toEqual([]);
    expect(fetchMock).toHaveBeenCalledWith(
      'http://api.test/api/v1/profiles/templates',
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

  it('updates a rule pack via PATCH', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        id: '1',
        user_id: 'u',
        slug: 'pack-b',
        profile: 'ICAO_2025',
        product: 'METAR',
        stage: 'lint',
        severity: 'error',
        when: '',
        message: '',
        standardReference: '',
        created_at: '',
        updated_at: '',
      }),
    } as Response);

    const row = await updateRulePack('tok', '1', {
      slug: 'pack-b',
      severity: 'error',
    });
    expect(row.slug).toBe('pack-b');
    expect(fetchMock).toHaveBeenCalledWith(
      'http://api.test/api/v1/profiles/rule-packs/1',
      expect.objectContaining({ method: 'PATCH' }),
    );
  });

  it('deletes a rule pack via DELETE', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      status: 204,
      json: async () => undefined,
    } as Response);

    await expect(deleteRulePack('tok', '1')).resolves.toBeUndefined();
    expect(fetchMock).toHaveBeenCalledWith(
      'http://api.test/api/v1/profiles/rule-packs/1',
      expect.objectContaining({ method: 'DELETE' }),
    );
  });

  it('creates a semantic preset via POST', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      status: 201,
      json: async () => ({
        id: 'pr-1',
        user_id: 'u',
        slug: 'us-default',
        name: 'US Default',
        semanticProfile: 'US_FAA_NWS',
        iwxxmVersion: '2025-2',
        extensions: ['IWXXM_US_3'],
        reportVariant: null,
        overlayId: null,
        shared: true,
        created_at: '',
        updated_at: '',
      }),
    } as Response);

    const row = await createPreset('tok', {
      slug: 'us-default',
      name: 'US Default',
      semanticProfile: 'US_FAA_NWS',
      iwxxmVersion: '2025-2',
      extensions: ['IWXXM_US_3'],
      shared: true,
    });
    expect(row.slug).toBe('us-default');
    expect(fetchMock).toHaveBeenCalledWith(
      'http://api.test/api/v1/profiles/presets',
      expect.objectContaining({ method: 'POST' }),
    );
  });

  it('updates a semantic preset via PATCH', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        id: 'pr-1',
        user_id: 'u',
        slug: 'us-default',
        name: 'US Default 2',
        semanticProfile: 'US_FAA_NWS',
        iwxxmVersion: '2025-2',
        extensions: ['IWXXM_US_3'],
        reportVariant: null,
        overlayId: null,
        shared: true,
        created_at: '',
        updated_at: '',
      }),
    } as Response);

    const row = await updatePreset('tok', 'pr-1', {
      name: 'US Default 2',
    });
    expect(row.name).toBe('US Default 2');
    expect(fetchMock).toHaveBeenCalledWith(
      'http://api.test/api/v1/profiles/presets/pr-1',
      expect.objectContaining({ method: 'PATCH' }),
    );
  });

  it('deletes a semantic preset via DELETE', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      status: 204,
      json: async () => undefined,
    } as Response);

    await expect(deletePreset('tok', 'pr-1')).resolves.toBeUndefined();
    expect(fetchMock).toHaveBeenCalledWith(
      'http://api.test/api/v1/profiles/presets/pr-1',
      expect.objectContaining({ method: 'DELETE' }),
    );
  });

  it('creates a dissemination template via POST', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      status: 201,
      json: async () => ({
        id: 'tpl-1',
        user_id: 'u',
        slug: 'shared-wis2',
        name: 'Shared WIS2',
        sinkType: 'wis2',
        product: 'metar',
        ddl: false,
        params: { topic: 'origin/a/wis2' },
        shared: true,
        created_at: '',
        updated_at: '',
      }),
    } as Response);
    const row = await createTemplate('tok', {
      slug: 'shared-wis2',
      name: 'Shared WIS2',
      sinkType: 'wis2',
      product: 'metar',
      params: { topic: 'origin/a/wis2' },
      shared: true,
    });
    expect(row.slug).toBe('shared-wis2');
    expect(fetchMock).toHaveBeenCalledWith(
      'http://api.test/api/v1/profiles/templates',
      expect.objectContaining({ method: 'POST' }),
    );
  });

  it('updates a dissemination template via PATCH', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        id: 'tpl-1',
        user_id: 'u',
        slug: 'shared-wis2',
        name: 'Shared WIS2 2',
        sinkType: 'wis2',
        product: 'taf',
        ddl: true,
        params: { topic: 'origin/a/wis2' },
        shared: true,
        created_at: '',
        updated_at: '',
      }),
    } as Response);
    const row = await updateTemplate('tok', 'tpl-1', {
      name: 'Shared WIS2 2',
      ddl: true,
    });
    expect(row.name).toBe('Shared WIS2 2');
    expect(fetchMock).toHaveBeenCalledWith(
      'http://api.test/api/v1/profiles/templates/tpl-1',
      expect.objectContaining({ method: 'PATCH' }),
    );
  });

  it('deletes a dissemination template via DELETE', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      status: 204,
      json: async () => undefined,
    } as Response);

    await expect(deleteTemplate('tok', 'tpl-1')).resolves.toBeUndefined();
    expect(fetchMock).toHaveBeenCalledWith(
      'http://api.test/api/v1/profiles/templates/tpl-1',
      expect.objectContaining({ method: 'DELETE' }),
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

  it('updates an overlay via PATCH', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        id: 'ov-1',
        user_id: 'u',
        slug: 'ov-b',
        baseProfileId: 'US_FAA_NWS',
        body: { x: 2 },
        signature: 'sig',
        shared: true,
        created_at: '',
        updated_at: '',
      }),
    } as Response);

    const row = await updateOverlay('tok', 'ov-1', {
      slug: 'ov-b',
      shared: true,
    });
    expect(row.slug).toBe('ov-b');
    expect(fetchMock).toHaveBeenCalledWith(
      'http://api.test/api/v1/profiles/overlays/ov-1',
      expect.objectContaining({ method: 'PATCH' }),
    );
  });

  it('deletes an overlay via DELETE', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      status: 204,
      json: async () => undefined,
    } as Response);

    await expect(deleteOverlay('tok', 'ov-1')).resolves.toBeUndefined();
    expect(fetchMock).toHaveBeenCalledWith(
      'http://api.test/api/v1/profiles/overlays/ov-1',
      expect.objectContaining({ method: 'DELETE' }),
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

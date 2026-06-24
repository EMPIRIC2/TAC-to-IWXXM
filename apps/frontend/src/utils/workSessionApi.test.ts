import { describe, it, expect, vi, beforeEach } from 'vitest';
import {
  createWorkSession,
  deleteWorkSession,
  getWorkSession,
  listAdminWorkSessions,
  listWorkSessions,
  restoreWorkSession,
  updateWorkSession,
} from './workSessionApi';

vi.mock('./apiBase', () => ({
  apiUrl: (path: string) => `http://api.test/api/v1${path}`,
  adminUrl: (path: string) => `http://api.test/admin${path}`,
}));

describe('workSessionApi', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('lists work sessions with auth header', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      json: async () => ({ items: [], total: 0, page: 1, limit: 20 }),
    } as Response);

    const result = await listWorkSessions('token-abc', { status: 'draft', limit: 5 });

    expect(fetchMock).toHaveBeenCalledWith(
      'http://api.test/api/v1/work-sessions?status=draft&limit=5',
      expect.objectContaining({
        headers: expect.objectContaining({ Authorization: 'Bearer token-abc' }),
      }),
    );
    expect(result.total).toBe(0);
  });

  it('lists work sessions with full query filters', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      json: async () => ({ items: [], total: 0, page: 2, limit: 10 }),
    } as Response);

    await listWorkSessions('token-abc', {
      from: '2026-01-01',
      to: '2026-06-01',
      include_deleted: true,
      page: 2,
    });

    expect(fetchMock).toHaveBeenCalledWith(
      'http://api.test/api/v1/work-sessions?from=2026-01-01&to=2026-06-01&include_deleted=true&page=2',
      expect.any(Object),
    );
  });

  it('creates a work session via POST', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      json: async () => ({ id: 'sess-1', status: 'draft', manual_tac: 'METAR' }),
    } as Response);

    const row = await createWorkSession('token-abc', { manual_tac: 'METAR TEST' });
    expect(row.id).toBe('sess-1');
  });

  it('fetches a single work session by id', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      json: async () => ({ id: 'sess-1', status: 'draft' }),
    } as Response);

    const row = await getWorkSession('token-abc', 'sess-1');
    expect(row.id).toBe('sess-1');
    expect(fetchMock).toHaveBeenCalledWith(
      'http://api.test/api/v1/work-sessions/sess-1',
      expect.objectContaining({
        headers: expect.objectContaining({ Authorization: 'Bearer token-abc' }),
      }),
    );
  });

  it('updates and deletes sessions', async () => {
    const fetchMock = vi
      .spyOn(globalThis, 'fetch')
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ id: 'sess-1', status: 'wip' }),
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ id: 'sess-1', deleted_at: '2026-06-23T00:00:00Z' }),
      } as Response);

    const updated = await updateWorkSession('token-abc', 'sess-1', { status: 'wip' });
    expect(updated.status).toBe('wip');

    const deleted = await deleteWorkSession('token-abc', 'sess-1');
    expect(deleted.deleted_at).toBeTruthy();
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });

  it('throws API detail on error response', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: false,
      status: 409,
      statusText: 'Conflict',
      json: async () => ({ detail: 'Only one WIP session is allowed per user' }),
    } as Response);

    await expect(
      updateWorkSession('token-abc', 'sess-1', { status: 'wip' }),
    ).rejects.toThrow('Only one WIP session is allowed per user');
  });

  it('restores a soft-deleted session', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      json: async () => ({ id: 'sess-1', deleted_at: null }),
    } as Response);

    const restored = await restoreWorkSession('token-abc', 'sess-1');
    expect(restored.deleted_at).toBeNull();
    expect(fetchMock).toHaveBeenCalledWith(
      'http://api.test/api/v1/work-sessions/sess-1/restore',
      expect.objectContaining({ method: 'POST' }),
    );
  });

  it('lists admin work sessions', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      json: async () => ({ items: [], total: 0, page: 1, limit: 50 }),
    } as Response);

    await listAdminWorkSessions('admin-token', { status: 'wip', limit: 50 });

    expect(fetchMock).toHaveBeenCalledWith(
      'http://api.test/admin/work-sessions?status=wip&limit=50',
      expect.objectContaining({
        headers: expect.objectContaining({ Authorization: 'Bearer admin-token' }),
      }),
    );
  });

  it('lists admin work sessions with page filter', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      json: async () => ({ items: [], total: 0, page: 2, limit: 10 }),
    } as Response);

    await listAdminWorkSessions('admin-token', { page: 2, limit: 10 });

    expect(fetchMock).toHaveBeenCalledWith(
      'http://api.test/admin/work-sessions?page=2&limit=10',
      expect.any(Object),
    );
  });

  it('lists sessions without query string when filters omitted', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      json: async () => ({ items: [], total: 0, page: 1, limit: 20 }),
    } as Response);

    await listWorkSessions('token-abc');

    expect(fetchMock).toHaveBeenCalledWith(
      'http://api.test/api/v1/work-sessions',
      expect.any(Object),
    );
  });

  it('throws status text when API detail is not a string', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: false,
      status: 500,
      statusText: 'Server Error',
      json: async () => ({ detail: ['validation failed'] }),
    } as Response);

    await expect(getWorkSession('token-abc', 'sess-1')).rejects.toThrow('Server Error');
  });

  it('throws status text when error JSON cannot be parsed', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: false,
      status: 502,
      statusText: 'Bad Gateway',
      json: async () => {
        throw new Error('invalid json');
      },
    } as unknown as Response);

    await expect(getWorkSession('token-abc', 'sess-1')).rejects.toThrow('Bad Gateway');
  });

  it('throws HTTP status code when error detail and status text are empty', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: false,
      status: 418,
      statusText: '',
      json: async () => ({ detail: '' }),
    } as Response);

    await expect(getWorkSession('token-abc', 'sess-1')).rejects.toThrow('HTTP 418');
  });

  it('lists admin sessions without query when no filters provided', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      json: async () => ({ items: [], total: 0, page: 1, limit: 20 }),
    } as Response);

    await listAdminWorkSessions('admin-token');

    expect(fetchMock).toHaveBeenCalledWith(
      'http://api.test/admin/work-sessions',
      expect.any(Object),
    );
  });
});

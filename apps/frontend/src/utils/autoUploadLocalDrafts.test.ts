import { beforeEach, describe, expect, it, vi } from 'vitest';
import type { WorkSession } from '@metar/shared';
import { autoUploadEligibleLocalDrafts } from './autoUploadLocalDrafts';
import { createWorkSession } from './workSessionApi';
import { deleteLocalWorkSession, listLocalWorkSessions } from './localWorkSessionStore';

vi.mock('./workSessionApi', () => ({
  createWorkSession: vi.fn(),
}));
vi.mock('./localWorkSessionStore', () => ({
  deleteLocalWorkSession: vi.fn(),
  listLocalWorkSessions: vi.fn(),
}));

const createWorkSessionMock = vi.mocked(createWorkSession);
const deleteLocalWorkSessionMock = vi.mocked(deleteLocalWorkSession);
const listLocalWorkSessionsMock = vi.mocked(listLocalWorkSessions);

function session(
  id: string,
  status: WorkSession['status'],
  deletedAt: string | null = null,
): WorkSession {
  return {
    id,
    user_id: 'local',
    product: 'metar',
    status,
    title: id,
    manual_tac: 'METAR KJFK 121251Z',
    pending_files: [],
    converted_results: [],
    errors: [],
    issues: [],
    conversion_params: {},
    kv_upload_key: null,
    created_at: '2026-01-01T00:00:00.000Z',
    updated_at: '2026-01-01T00:00:00.000Z',
    deleted_at: deletedAt,
  };
}

describe('autoUploadEligibleLocalDrafts', () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });

  it('uploads active drafts and WIP rows, then soft-deletes only successful uploads', async () => {
    const draft = session('draft', 'draft');
    const wip = session('wip', 'wip');
    listLocalWorkSessionsMock.mockResolvedValue({
      items: [
        draft,
        wip,
        session('finished', 'finished'),
        session('deleted', 'draft', 'now'),
      ],
      total: 4,
      page: 1,
      limit: 100,
    });
    createWorkSessionMock.mockResolvedValue({ id: 'remote' } as WorkSession);
    deleteLocalWorkSessionMock.mockResolvedValue({} as WorkSession);

    await expect(autoUploadEligibleLocalDrafts('jwt')).resolves.toEqual({
      uploaded: 2,
      errors: [],
    });
    expect(listLocalWorkSessionsMock).toHaveBeenCalledWith({
      include_deleted: false,
      limit: 100,
    });
    expect(createWorkSessionMock).toHaveBeenCalledTimes(2);
    expect(deleteLocalWorkSessionMock).toHaveBeenCalledWith('draft');
    expect(deleteLocalWorkSessionMock).toHaveBeenCalledWith('wip');
  });

  it('reports Error and non-Error upload failures without deleting their drafts', async () => {
    listLocalWorkSessionsMock.mockResolvedValue({
      items: [session('error', 'draft'), session('string', 'wip')],
      total: 2,
      page: 1,
      limit: 100,
    });
    createWorkSessionMock
      .mockRejectedValueOnce(new Error('offline'))
      .mockRejectedValueOnce('denied');

    await expect(autoUploadEligibleLocalDrafts('jwt')).resolves.toEqual({
      uploaded: 0,
      errors: [
        { sessionId: 'error', message: 'offline' },
        { sessionId: 'string', message: 'denied' },
      ],
    });
    expect(deleteLocalWorkSessionMock).not.toHaveBeenCalled();
  });
});

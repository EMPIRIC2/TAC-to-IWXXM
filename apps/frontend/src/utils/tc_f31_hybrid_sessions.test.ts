/**
 * T4.1 / TC-F31-002..005 — guest notice, auto-upload, privacy gates (UJ-045..047).
 */
import { beforeEach, describe, expect, it, vi } from 'vitest';
import type { WorkSession } from '@metar/shared';
import {
  GUEST_LOSS_OF_PROGRESS_MESSAGE,
  shouldShowGuestLossOfProgressNotice,
} from './guestLossNotice';
import { autoUploadEligibleLocalDrafts } from './autoUploadLocalDrafts';
import {
  STORAGE_INVENTORY,
  canPersistWorkHistoryLocal,
  clearPrivacyPreferences,
  defaultPrivacyPreferences,
  savePrivacyPreferences,
} from './privacyPreferences';

vi.mock('./localWorkSessionStore', () => ({
  listLocalWorkSessions: vi.fn(),
  deleteLocalWorkSession: vi.fn(),
}));

vi.mock('./workSessionApi', () => ({
  createWorkSession: vi.fn(),
}));

import { deleteLocalWorkSession, listLocalWorkSessions } from './localWorkSessionStore';
import { createWorkSession } from './workSessionApi';

function makeLocalSession(
  overrides: Partial<WorkSession> & Pick<WorkSession, 'id' | 'status'>,
): WorkSession {
  return {
    user_id: 'local',
    product: 'metar',
    title: 'Draft',
    manual_tac: 'METAR KJFK 231751Z NIL=',
    pending_files: [],
    converted_results: [],
    errors: [],
    issues: [],
    conversion_params: {},
    kv_upload_key: null,
    deleted_at: null,
    created_at: '2026-08-03T00:00:00Z',
    updated_at: '2026-08-03T00:00:00Z',
    ...overrides,
  };
}

describe('TC-F31-002 guest loss-of-progress notice', () => {
  it('shows only for guests with local unsaved work', () => {
    expect(
      shouldShowGuestLossOfProgressNotice({
        isLoggedIn: false,
        hasLocalUnsavedWork: true,
      }),
    ).toBe(true);
    expect(
      shouldShowGuestLossOfProgressNotice({
        isLoggedIn: false,
        hasLocalUnsavedWork: false,
      }),
    ).toBe(false);
    expect(
      shouldShowGuestLossOfProgressNotice({
        isLoggedIn: true,
        hasLocalUnsavedWork: true,
      }),
    ).toBe(false);
  });

  it('exposes persistent banner copy', () => {
    expect(GUEST_LOSS_OF_PROGRESS_MESSAGE.toLowerCase()).toMatch(/lost|sign/);
  });
});

describe('TC-F31-004 auto-upload local drafts on login', () => {
  beforeEach(() => {
    vi.mocked(listLocalWorkSessions).mockReset();
    vi.mocked(deleteLocalWorkSession).mockReset();
    vi.mocked(createWorkSession).mockReset();
  });

  it('uploads eligible drafts and clears local copies (no merge prompt)', async () => {
    const draft = makeLocalSession({ id: 'local-1', status: 'draft' });
    const wip = makeLocalSession({ id: 'local-2', status: 'wip' });
    const finished = makeLocalSession({ id: 'local-3', status: 'finished' });
    vi.mocked(listLocalWorkSessions).mockResolvedValue({
      items: [draft, wip, finished],
      total: 3,
      page: 1,
      limit: 100,
    });
    vi.mocked(createWorkSession).mockImplementation(async (_token, payload) =>
      makeLocalSession({
        id: `server-${payload.title ?? 'x'}`,
        status: payload.status ?? 'draft',
        user_id: 'auth-user',
      }),
    );
    vi.mocked(deleteLocalWorkSession).mockImplementation(async (id) =>
      makeLocalSession({ id, status: 'draft' }),
    );

    const result = await autoUploadEligibleLocalDrafts('jwt-token');
    expect(result.uploaded).toBe(2);
    expect(result.errors).toEqual([]);
    expect(createWorkSession).toHaveBeenCalledTimes(2);
    expect(deleteLocalWorkSession).toHaveBeenCalledWith('local-1');
    expect(deleteLocalWorkSession).toHaveBeenCalledWith('local-2');
    expect(deleteLocalWorkSession).not.toHaveBeenCalledWith('local-3');
  });

  it('records per-item errors without aborting the batch', async () => {
    const a = makeLocalSession({ id: 'a', status: 'draft' });
    const b = makeLocalSession({ id: 'b', status: 'draft' });
    vi.mocked(listLocalWorkSessions).mockResolvedValue({
      items: [a, b],
      total: 2,
      page: 1,
      limit: 100,
    });
    vi.mocked(createWorkSession)
      .mockRejectedValueOnce(new Error('server 500'))
      .mockResolvedValueOnce(
        makeLocalSession({ id: 'server-b', status: 'draft', user_id: 'u' }),
      );
    vi.mocked(deleteLocalWorkSession).mockResolvedValue(
      makeLocalSession({ id: 'b', status: 'draft' }),
    );

    const result = await autoUploadEligibleLocalDrafts('jwt');
    expect(result.uploaded).toBe(1);
    expect(result.errors).toEqual([{ sessionId: 'a', message: 'server 500' }]);
  });
});

describe('TC-F31-005 privacy gates IndexedDB + Auth cookie disclosure', () => {
  beforeEach(() => {
    clearPrivacyPreferences();
  });

  it('defaults workHistoryLocal on and discloses Auth cookies in inventory', () => {
    const prefs = defaultPrivacyPreferences();
    expect(prefs.workHistoryLocal).toBe(true);
    expect(canPersistWorkHistoryLocal(prefs)).toBe(true);
    expect(STORAGE_INVENTORY.some((i) => i.kind === 'indexedDB' && !i.necessary)).toBe(
      true,
    );
    expect(
      STORAGE_INVENTORY.some((i) => i.kind === 'cookie' && /auth/i.test(i.purpose)),
    ).toBe(true);
  });

  it('blocks IndexedDB work-history writes when declined', () => {
    savePrivacyPreferences({ workHistoryLocal: false });
    expect(canPersistWorkHistoryLocal()).toBe(false);
  });
});

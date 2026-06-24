import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useWorkSessionSync, AUTOSAVE_DEBOUNCE_MS } from './useWorkSessionSync';
import type { ConverterSnapshot } from '@/utils/workSessionPayload';

const mockCreate = vi.fn();
const mockUpdate = vi.fn();

vi.mock('/utils/workSessionApi', () => ({
  createWorkSession: (...args: unknown[]) => mockCreate(...args),
  updateWorkSession: (...args: unknown[]) => mockUpdate(...args),
}));

const snapshot: ConverterSnapshot = {
  manualInput: 'METAR KJFK 121251Z 18012KT 10SM',
  pendingFiles: [],
  convertedFiles: [],
  conversionLog: null,
  conversionParams: { iwxxmVersion: '2025-2' },
};

describe('useWorkSessionSync', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    mockCreate.mockReset();
    mockUpdate.mockReset();
    mockCreate.mockResolvedValue({
      id: 'new-session',
      status: 'draft',
      title: 'KJFK',
      manual_tac: snapshot.manualInput,
      pending_files: [],
      converted_results: [],
      errors: [],
      issues: [],
      conversion_params: {},
      kv_upload_key: null,
      deleted_at: null,
      user_id: 'user-1',
      created_at: '2026-06-24T00:00:00Z',
      updated_at: '2026-06-24T00:00:00Z',
    });
    mockUpdate.mockResolvedValue({
      id: 'existing-session',
      status: 'draft',
      title: 'KJFK',
      manual_tac: snapshot.manualInput,
      pending_files: [],
      converted_results: [],
      errors: [],
      issues: [],
      conversion_params: {},
      kv_upload_key: null,
      deleted_at: null,
      user_id: 'user-1',
      created_at: '2026-06-24T00:00:00Z',
      updated_at: '2026-06-24T00:00:01Z',
    });
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('debounces auto-save by 3 seconds (F5-R6)', async () => {
    const onSessionSaved = vi.fn();
    const onSessionIdAssigned = vi.fn();

    const { result } = renderHook(() =>
      useWorkSessionSync({
        accessToken: 'token',
        sessionId: null,
        sessionStatus: null,
        onSessionSaved,
        onSessionIdAssigned,
      }),
    );

    act(() => {
      result.current.scheduleAutoSave(snapshot);
    });

    expect(mockCreate).not.toHaveBeenCalled();

    await act(async () => {
      vi.advanceTimersByTime(AUTOSAVE_DEBOUNCE_MS - 1);
    });
    expect(mockCreate).not.toHaveBeenCalled();

    await act(async () => {
      vi.advanceTimersByTime(1);
    });

    expect(mockCreate).toHaveBeenCalledTimes(1);
    expect(onSessionIdAssigned).toHaveBeenCalledWith('new-session');
    expect(onSessionSaved).toHaveBeenCalled();
  });

  it('PATCHes existing session on persist when sessionId is set', async () => {
    const { result } = renderHook(() =>
      useWorkSessionSync({
        accessToken: 'token',
        sessionId: 'existing-session',
        sessionStatus: 'draft',
        onSessionSaved: vi.fn(),
        onSessionIdAssigned: vi.fn(),
      }),
    );

    await act(async () => {
      await result.current.persistSession(snapshot);
    });

    expect(mockUpdate).toHaveBeenCalledWith(
      'token',
      'existing-session',
      expect.any(Object),
    );
    expect(mockCreate).not.toHaveBeenCalled();
  });

  it('skips persist when session is finished (read-only)', async () => {
    const { result } = renderHook(() =>
      useWorkSessionSync({
        accessToken: 'token',
        sessionId: 'finished-session',
        sessionStatus: 'finished',
        onSessionSaved: vi.fn(),
        onSessionIdAssigned: vi.fn(),
      }),
    );

    expect(result.current.isReadOnly).toBe(true);

    await act(async () => {
      await result.current.persistSession(snapshot);
    });

    expect(mockCreate).not.toHaveBeenCalled();
    expect(mockUpdate).not.toHaveBeenCalled();
  });

  it('skips debounced auto-save when read-only', () => {
    const { result } = renderHook(() =>
      useWorkSessionSync({
        accessToken: 'token',
        sessionId: 'finished-session',
        sessionStatus: 'finished',
        onSessionSaved: vi.fn(),
        onSessionIdAssigned: vi.fn(),
      }),
    );

    act(() => {
      result.current.scheduleAutoSave(snapshot);
    });

    expect(mockCreate).not.toHaveBeenCalled();
  });

  it('flushAutoSave clears pending debounce and persists immediately', async () => {
    const { result } = renderHook(() =>
      useWorkSessionSync({
        accessToken: 'token',
        sessionId: 'existing-session',
        sessionStatus: 'draft',
        onSessionSaved: vi.fn(),
        onSessionIdAssigned: vi.fn(),
      }),
    );

    act(() => {
      result.current.scheduleAutoSave(snapshot);
    });

    await act(async () => {
      await result.current.flushAutoSave(snapshot);
    });

    expect(mockUpdate).toHaveBeenCalledTimes(1);
  });

  it('marks save indicator error when persist fails', async () => {
    mockCreate.mockRejectedValueOnce(new Error('save failed'));
    const { result } = renderHook(() =>
      useWorkSessionSync({
        accessToken: 'token',
        sessionId: null,
        sessionStatus: null,
        onSessionSaved: vi.fn(),
        onSessionIdAssigned: vi.fn(),
      }),
    );

    await act(async () => {
      await result.current.persistSession(snapshot);
    });

    expect(result.current.saveIndicator).toBe('error');
  });
});

/**
 * F5 debounced auto-save and status transitions for the converter.
 */

import { useCallback, useEffect, useRef, useState } from 'react';
import type { WorkSession, WorkSessionStatus } from '@metar/shared';
import { createWorkSession, updateWorkSession } from '/utils/workSessionApi';
import {
  buildWorkSessionPayload,
  type ConverterSnapshot,
} from '/utils/workSessionPayload';

export const AUTOSAVE_DEBOUNCE_MS = 3000;

export type AutoSaveIndicator = 'idle' | 'pending' | 'saving' | 'saved' | 'error';

export interface UseWorkSessionSyncOptions {
  accessToken?: string;
  sessionId: string | null;
  sessionStatus?: WorkSessionStatus | null;
  onSessionSaved: (session: WorkSession) => void;
  onSessionIdAssigned: (id: string) => void;
}

export function useWorkSessionSync({
  accessToken,
  sessionId,
  sessionStatus,
  onSessionSaved,
  onSessionIdAssigned,
}: UseWorkSessionSyncOptions) {
  const [saveIndicator, setSaveIndicator] = useState<AutoSaveIndicator>('idle');
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const sessionIdRef = useRef(sessionId);

  useEffect(() => {
    sessionIdRef.current = sessionId;
  }, [sessionId]);

  const isReadOnly = sessionStatus === 'finished';

  useEffect(() => {
    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }
    };
  }, []);

  const persistSession = useCallback(
    async (
      snapshot: ConverterSnapshot,
      options?: { status?: WorkSessionStatus; kvUploadKey?: string },
    ): Promise<WorkSession | null> => {
      if (!accessToken || isReadOnly) {
        return null;
      }

      setSaveIndicator('saving');
      const payload = buildWorkSessionPayload(snapshot, {
        status: options?.status,
        kvUploadKey: options?.kvUploadKey,
      });

      try {
        let saved: WorkSession;
        const activeId = sessionIdRef.current;
        if (activeId) {
          saved = await updateWorkSession(accessToken, activeId, payload);
        } else {
          saved = await createWorkSession(accessToken, payload);
          onSessionIdAssigned(saved.id);
        }
        onSessionSaved(saved);
        setSaveIndicator('saved');
        return saved;
      } catch (error) {
        console.error('[useWorkSessionSync] persist failed:', error);
        setSaveIndicator('error');
        return null;
      }
    },
    [accessToken, isReadOnly, onSessionIdAssigned, onSessionSaved],
  );

  const scheduleAutoSave = useCallback(
    (snapshot: ConverterSnapshot) => {
      if (!accessToken || isReadOnly) {
        return;
      }
      setSaveIndicator('pending');
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }
      debounceRef.current = setTimeout(() => {
        void persistSession(snapshot);
      }, AUTOSAVE_DEBOUNCE_MS);
    },
    [accessToken, isReadOnly, persistSession],
  );

  const flushAutoSave = useCallback(
    async (snapshot: ConverterSnapshot) => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
        debounceRef.current = null;
      }
      return persistSession(snapshot);
    },
    [persistSession],
  );

  return {
    isReadOnly,
    saveIndicator,
    scheduleAutoSave,
    persistSession,
    flushAutoSave,
  };
}

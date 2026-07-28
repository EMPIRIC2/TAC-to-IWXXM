/**
 * TC — one-time guest sessionStorage → IndexedDB migrate (E17-14 / F7.h).
 */

import { beforeEach, describe, expect, it } from 'vitest';
import type { ConverterSnapshot } from './workSessionPayload';
import {
  clearGuestConverterState,
  saveGuestConverterState,
} from './guestConverterState';
import {
  clearLocalWorkSessions,
  listLocalWorkSessions,
  migrateGuestSessionStorageToIndexedDb,
  resetLocalWorkSessionDbCache,
} from './localWorkSessionStore';

const snapshot: ConverterSnapshot = {
  manualInput: 'METAR KJFK 121755Z 18004KT 10SM FEW250 24/18 A2992',
  pendingFiles: [],
  convertedFiles: [],
  conversionLog: null,
  conversionParams: { product: 'metar' },
};

describe('migrateGuestSessionStorageToIndexedDb (E17-14)', () => {
  beforeEach(async () => {
    clearGuestConverterState();
    sessionStorage.clear();
    resetLocalWorkSessionDbCache();
    await clearLocalWorkSessions();
  });

  it('migrates guest sessionStorage into IndexedDB once and clears the guest key', async () => {
    saveGuestConverterState(snapshot);
    expect(sessionStorage.getItem('metar_guest_converter_state')).toBeTruthy();

    const first = await migrateGuestSessionStorageToIndexedDb();
    expect(first.migrated).toBe(true);
    expect(first.sessionId).toBeTruthy();
    expect(sessionStorage.getItem('metar_guest_converter_state')).toBeNull();

    const listed = await listLocalWorkSessions();
    expect(listed.total).toBe(1);
    expect(listed.items[0]?.manual_tac).toContain('KJFK');
    expect(listed.items[0]?.product).toBe('metar');

    const second = await migrateGuestSessionStorageToIndexedDb();
    expect(second.migrated).toBe(false);
    expect(second.sessionId).toBeNull();
    expect((await listLocalWorkSessions()).total).toBe(1);
  });

  it('is a no-op when guest sessionStorage is empty', async () => {
    const result = await migrateGuestSessionStorageToIndexedDb();
    expect(result.migrated).toBe(false);
    expect(result.sessionId).toBeNull();
    expect((await listLocalWorkSessions()).total).toBe(0);
  });
});

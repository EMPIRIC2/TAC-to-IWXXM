/**
 * Local IndexedDB work-session store (F7.h / F21 / ADR-031).
 *
 * Persistence target: browser IndexedDB via `idb` (T2.3). This stub exists so
 * TC-004 unit tests can import the contract and fail red until implementation.
 */

import type {
  WorkSession,
  WorkSessionListResponse,
  WorkSessionProduct,
  WorkSessionUpsertPayload,
} from '@metar/shared';

/** My METARs filter — METAR/SPECI only (UJ-004 / TC-004). */
export const MY_METARS_PRODUCTS: WorkSessionProduct[] = ['metar', 'speci'];

export const EXPORT_SCHEMA_ID = 'tac-work-sessions-export-v1' as const;

export interface LocalWorkSessionExportV1 {
  schema: typeof EXPORT_SCHEMA_ID;
  exported_at: string;
  sessions: WorkSession[];
}

export interface ListLocalWorkSessionsParams {
  status?: WorkSession['status'];
  product?: WorkSessionProduct | WorkSessionProduct[];
  include_deleted?: boolean;
  page?: number;
  limit?: number;
}

function notImplemented(op: string): never {
  throw new Error(`localWorkSessionStore.${op}: not implemented (T2.3)`);
}

/** Clear all local sessions (test helper / privacy wipe). */
export async function clearLocalWorkSessions(): Promise<void> {
  notImplemented('clearLocalWorkSessions');
}

export async function createLocalWorkSession(
  _payload: WorkSessionUpsertPayload,
): Promise<WorkSession> {
  notImplemented('createLocalWorkSession');
}

export async function getLocalWorkSession(_sessionId: string): Promise<WorkSession> {
  notImplemented('getLocalWorkSession');
}

export async function updateLocalWorkSession(
  _sessionId: string,
  _payload: WorkSessionUpsertPayload,
): Promise<WorkSession> {
  notImplemented('updateLocalWorkSession');
}

export async function deleteLocalWorkSession(_sessionId: string): Promise<WorkSession> {
  notImplemented('deleteLocalWorkSession');
}

export async function restoreLocalWorkSession(
  _sessionId: string,
): Promise<WorkSession> {
  notImplemented('restoreLocalWorkSession');
}

export async function listLocalWorkSessions(
  _params?: ListLocalWorkSessionsParams,
): Promise<WorkSessionListResponse> {
  notImplemented('listLocalWorkSessions');
}

/** My METARs = product IN (metar, speci), excluding soft-deleted by default. */
export async function listMyMetars(
  params: Omit<ListLocalWorkSessionsParams, 'product'> = {},
): Promise<WorkSessionListResponse> {
  return listLocalWorkSessions({
    ...params,
    product: MY_METARS_PRODUCTS,
  });
}

export async function exportLocalWorkSessions(): Promise<LocalWorkSessionExportV1> {
  notImplemented('exportLocalWorkSessions');
}

export async function importLocalWorkSessions(
  _doc: LocalWorkSessionExportV1,
): Promise<{ imported: number }> {
  notImplemented('importLocalWorkSessions');
}

export interface GuestMigrateResult {
  migrated: boolean;
  sessionId: string | null;
}

/**
 * One-time migrate of guest ``metar_guest_converter_state`` → IndexedDB (E17-14).
 */
export async function migrateGuestSessionStorageToIndexedDb(): Promise<GuestMigrateResult> {
  notImplemented('migrateGuestSessionStorageToIndexedDb');
}

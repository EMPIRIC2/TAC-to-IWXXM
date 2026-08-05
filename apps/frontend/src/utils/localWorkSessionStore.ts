/**
 * Local IndexedDB work-session store (F7.h / F21 / ADR-031).
 *
 * Uses Jake Archibald's ``idb`` wrapper. No JWT / server session calls.
 */

import { openDB, type DBSchema, type IDBPDatabase } from 'idb';
import type {
  WorkSession,
  WorkSessionListResponse,
  WorkSessionProduct,
  WorkSessionStatus,
  WorkSessionUpsertPayload,
} from '@metar/shared';
import { buildWorkSessionPayload, type ConverterSnapshot } from './workSessionPayload';
import {
  clearGuestConverterState,
  readGuestConverterState,
} from './guestConverterState';
import { canPersistWorkHistoryLocal } from './privacyPreferences';

/** My METARs filter — METAR/SPECI only (UJ-004 / TC-004). */
export const MY_METARS_PRODUCTS: WorkSessionProduct[] = ['metar', 'speci'];

export const EXPORT_SCHEMA_ID = 'tac-work-sessions-export-v1' as const;

/** Thrown when F22 prefs decline guest IndexedDB work-history writes (TC-F31-005). */
export class LocalWorkHistoryDisabledError extends Error {
  constructor(
    message = 'Local work-history persistence is disabled by privacy preferences',
  ) {
    super(message);
    this.name = 'LocalWorkHistoryDisabledError';
  }
}

function assertWorkHistoryPersistAllowed(): void {
  if (!canPersistWorkHistoryLocal()) {
    throw new LocalWorkHistoryDisabledError();
  }
}

const DB_NAME = 'tac-work-sessions';
const DB_VERSION = 1;
const STORE = 'sessions';
const LOCAL_USER_ID = 'local';

export interface LocalWorkSessionExportV1 {
  schema: typeof EXPORT_SCHEMA_ID;
  exported_at: string;
  sessions: WorkSession[];
}

export interface ListLocalWorkSessionsParams {
  status?: WorkSessionStatus;
  product?: WorkSessionProduct | WorkSessionProduct[];
  include_deleted?: boolean;
  page?: number;
  limit?: number;
}

export interface GuestMigrateResult {
  migrated: boolean;
  sessionId: string | null;
}

interface TacWorkSessionsDb extends DBSchema {
  sessions: {
    key: string;
    value: WorkSession;
    indexes: {
      'by-updated': string;
      'by-product': string;
      'by-status': string;
    };
  };
}

let dbPromise: Promise<IDBPDatabase<TacWorkSessionsDb>> | null = null;

function getDb(): Promise<IDBPDatabase<TacWorkSessionsDb>> {
  if (!dbPromise) {
    dbPromise = openDB<TacWorkSessionsDb>(DB_NAME, DB_VERSION, {
      upgrade(db) {
        const store = db.createObjectStore(STORE, { keyPath: 'id' });
        store.createIndex('by-updated', 'updated_at');
        store.createIndex('by-product', 'product');
        store.createIndex('by-status', 'status');
      },
    });
  }
  return dbPromise;
}

/** Reset cached DB handle (tests). */
export function resetLocalWorkSessionDbCache(): void {
  dbPromise = null;
}

function nowIso(): string {
  return new Date().toISOString();
}

function newId(): string {
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
    return crypto.randomUUID();
  }
  return `local-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
}

function mergePayload(
  existing: WorkSession | null,
  payload: WorkSessionUpsertPayload,
): WorkSession {
  const stamp = nowIso();
  if (!existing) {
    return {
      id: newId(),
      user_id: LOCAL_USER_ID,
      product: payload.product ?? 'metar',
      status: payload.status ?? 'draft',
      title: payload.title ?? 'Untitled',
      manual_tac: payload.manual_tac ?? '',
      pending_files: payload.pending_files ?? [],
      converted_results: payload.converted_results ?? [],
      errors: payload.errors ?? [],
      issues: payload.issues ?? [],
      conversion_params: payload.conversion_params ?? {},
      kv_upload_key: payload.kv_upload_key ?? null,
      deleted_at: null,
      created_at: stamp,
      updated_at: stamp,
    };
  }
  return {
    ...existing,
    product: payload.product ?? existing.product,
    status: payload.status ?? existing.status,
    title: payload.title ?? existing.title,
    manual_tac: payload.manual_tac ?? existing.manual_tac,
    pending_files: payload.pending_files ?? existing.pending_files,
    converted_results: payload.converted_results ?? existing.converted_results,
    errors: payload.errors ?? existing.errors,
    issues: payload.issues ?? existing.issues,
    conversion_params: payload.conversion_params ?? existing.conversion_params,
    kv_upload_key:
      payload.kv_upload_key !== undefined
        ? payload.kv_upload_key
        : existing.kv_upload_key,
    updated_at: stamp,
  };
}

async function countActiveWip(excludeId?: string): Promise<number> {
  const db = await getDb();
  const all = await db.getAll(STORE);
  return all.filter(
    (s) =>
      s.status === 'wip' &&
      s.deleted_at == null &&
      (excludeId == null || s.id !== excludeId),
  ).length;
}

async function assertSingleWip(
  nextStatus: WorkSessionStatus | undefined,
  excludeId?: string,
): Promise<void> {
  if (nextStatus !== 'wip') {
    return;
  }
  if ((await countActiveWip(excludeId)) > 0) {
    throw new Error('Only one WIP session is allowed per browser profile');
  }
}

/** Clear all local sessions (test helper / privacy wipe). */
export async function clearLocalWorkSessions(): Promise<void> {
  const db = await getDb();
  await db.clear(STORE);
}

export async function createLocalWorkSession(
  payload: WorkSessionUpsertPayload,
): Promise<WorkSession> {
  assertWorkHistoryPersistAllowed();
  await assertSingleWip(payload.status);
  const row = mergePayload(null, payload);
  const db = await getDb();
  await db.put(STORE, row);
  return row;
}

export async function getLocalWorkSession(sessionId: string): Promise<WorkSession> {
  const db = await getDb();
  const row = await db.get(STORE, sessionId);
  if (!row) {
    throw new Error(`Work session not found: ${sessionId}`);
  }
  return row;
}

export async function updateLocalWorkSession(
  sessionId: string,
  payload: WorkSessionUpsertPayload,
): Promise<WorkSession> {
  assertWorkHistoryPersistAllowed();
  const existing = await getLocalWorkSession(sessionId);
  await assertSingleWip(payload.status, sessionId);
  const row = mergePayload(existing, payload);
  const db = await getDb();
  await db.put(STORE, row);
  return row;
}

export async function deleteLocalWorkSession(sessionId: string): Promise<WorkSession> {
  const existing = await getLocalWorkSession(sessionId);
  const row: WorkSession = {
    ...existing,
    deleted_at: nowIso(),
    updated_at: nowIso(),
  };
  const db = await getDb();
  await db.put(STORE, row);
  return row;
}

export async function restoreLocalWorkSession(sessionId: string): Promise<WorkSession> {
  assertWorkHistoryPersistAllowed();
  const existing = await getLocalWorkSession(sessionId);
  const row: WorkSession = {
    ...existing,
    deleted_at: null,
    updated_at: nowIso(),
  };
  const db = await getDb();
  await db.put(STORE, row);
  return row;
}

export async function listLocalWorkSessions(
  params: ListLocalWorkSessionsParams = {},
): Promise<WorkSessionListResponse> {
  const db = await getDb();
  let items = await db.getAll(STORE);
  items.sort((a, b) => b.updated_at.localeCompare(a.updated_at));

  if (!params.include_deleted) {
    items = items.filter((s) => s.deleted_at == null);
  }
  if (params.status) {
    items = items.filter((s) => s.status === params.status);
  }
  if (params.product) {
    const products = Array.isArray(params.product) ? params.product : [params.product];
    items = items.filter((s) => products.includes(s.product));
  }

  const total = items.length;
  const page = params.page && params.page > 0 ? params.page : 1;
  const limit = params.limit && params.limit > 0 ? params.limit : 20;
  const start = (page - 1) * limit;
  const slice = items.slice(start, start + limit);

  return { items: slice, total, page, limit };
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
  const db = await getDb();
  const sessions = await db.getAll(STORE);
  sessions.sort((a, b) => b.updated_at.localeCompare(a.updated_at));
  return {
    schema: EXPORT_SCHEMA_ID,
    exported_at: nowIso(),
    sessions,
  };
}

export async function importLocalWorkSessions(
  doc: LocalWorkSessionExportV1,
): Promise<{ imported: number }> {
  assertWorkHistoryPersistAllowed();
  if (doc.schema !== EXPORT_SCHEMA_ID) {
    throw new Error(`Unsupported export schema: ${String(doc.schema)}`);
  }
  const db = await getDb();
  let imported = 0;
  for (const session of doc.sessions) {
    await db.put(STORE, {
      ...session,
      user_id: session.user_id || LOCAL_USER_ID,
    });
    imported += 1;
  }
  return { imported };
}

/**
 * One-time migrate of guest ``metar_guest_converter_state`` → IndexedDB (E17-14).
 */
export async function migrateGuestSessionStorageToIndexedDb(): Promise<GuestMigrateResult> {
  const snapshot: ConverterSnapshot | null = readGuestConverterState();
  if (!snapshot) {
    return { migrated: false, sessionId: null };
  }
  const payload = buildWorkSessionPayload(snapshot, { status: 'draft' });
  const row = await createLocalWorkSession(payload);
  clearGuestConverterState();
  return { migrated: true, sessionId: row.id };
}

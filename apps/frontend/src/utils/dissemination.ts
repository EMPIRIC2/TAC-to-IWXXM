/**
 * Dissemination (F16–F19) client helpers — sink enums + preflight/send API.
 *
 * Aligns with packages/dissemination DRAWER_SINK_TYPES and api-contract
 * POST /api/v1/dissemination/preflight|send (ADR-030 / E14-03).
 */

import { apiUrl } from './apiBase';

/** Drawer sink chooser order — keep aligned with packages/dissemination.models. */
export const DRAWER_SINK_TYPES = [
  'postgres',
  'mysql',
  'sqlserver',
  'sqlite',
  'wis2',
  'edis',
  'amhs',
  'swim',
  'afs',
] as const;

export type SinkType = (typeof DRAWER_SINK_TYPES)[number];

export const DB_SINK_TYPES: readonly SinkType[] = [
  'postgres',
  'mysql',
  'sqlserver',
  'sqlite',
] as const;

export interface SchemaDiffItem {
  kind: string;
  table: string;
  detail: string;
  column?: string | null;
}

export interface PreflightRequest {
  sink_type: SinkType;
  uri?: string | null;
  ddl?: boolean;
  product?: string | null;
  iwxxm_version?: string | null;
  params?: Record<string, unknown>;
}

export interface PreflightResponse {
  ok: boolean;
  connectivity_ok: boolean;
  diffs: SchemaDiffItem[];
  handle?: string | null;
  detail?: string | null;
}

export interface SendRequest {
  handle?: string | null;
  sink_type?: SinkType | null;
  uri?: string | null;
  iwxxm_xml?: string | null;
  tac_text?: string | null;
  product?: string | null;
  iwxxm_version?: string | null;
  params?: Record<string, unknown>;
}

export interface SendResponse {
  ok: boolean;
  kv_upload_key?: string | null;
  detail?: string | null;
}

function authHeaders(accessToken: string): HeadersInit {
  return {
    Authorization: `Bearer ${accessToken}`,
    'Content-Type': 'application/json',
  };
}

async function parseJson<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    const detail =
      typeof error.detail === 'string'
        ? error.detail
        : typeof error === 'object' && error !== null && 'detail' in error
          ? JSON.stringify((error as { detail: unknown }).detail)
          : response.statusText;
    throw new Error(detail || `HTTP ${response.status}`);
  }
  return response.json() as Promise<T>;
}

/**
 * Whether Send may proceed after a preflight result (Q7=A — block until green).
 *
 * @param preflight - Latest preflight response, or null if none yet
 * @returns true only when ok, no diffs, and a memory-only handle is present
 */
export function isPreflightGreen(
  preflight: PreflightResponse | null | undefined,
): boolean {
  if (!preflight) return false;
  if (!preflight.ok || !preflight.connectivity_ok) return false;
  if (preflight.diffs.length > 0) return false;
  return Boolean(preflight.handle);
}

/**
 * Call POST /api/v1/dissemination/preflight.
 *
 * @param accessToken - Bearer JWT
 * @param body - Sink-typed preflight request
 */
export async function disseminationPreflight(
  accessToken: string,
  body: PreflightRequest,
): Promise<PreflightResponse> {
  const response = await fetch(apiUrl('/dissemination/preflight'), {
    method: 'POST',
    headers: authHeaders(accessToken),
    body: JSON.stringify(body),
  });
  return parseJson<PreflightResponse>(response);
}

/**
 * Call POST /api/v1/dissemination/send.
 *
 * @param accessToken - Bearer JWT
 * @param body - Handle from green preflight and/or payload
 */
export async function disseminationSend(
  accessToken: string,
  body: SendRequest,
): Promise<SendResponse> {
  const response = await fetch(apiUrl('/dissemination/send'), {
    method: 'POST',
    headers: authHeaders(accessToken),
    body: JSON.stringify(body),
  });
  return parseJson<SendResponse>(response);
}

/** Human labels for the drawer sink chooser. */
export function sinkTypeLabel(sink: SinkType): string {
  const labels: Record<SinkType, string> = {
    postgres: 'Postgres',
    mysql: 'MySQL / MariaDB',
    sqlserver: 'SQL Server',
    sqlite: 'SQLite',
    wis2: 'WIS2',
    edis: 'EDIS',
    amhs: 'AMHS',
    swim: 'SWIM',
    afs: 'AFS',
  };
  return labels[sink];
}

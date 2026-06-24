/**
 * F5 work session API client — CRUD against /api/v1/work-sessions.
 */

import type {
  WorkSession,
  WorkSessionListResponse,
  WorkSessionStatus,
  WorkSessionUpsertPayload,
} from '@metar/shared';
import { adminUrl, apiUrl } from './apiBase';

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
      typeof error.detail === 'string' ? error.detail : response.statusText;
    throw new Error(detail || `HTTP ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export interface ListWorkSessionsParams {
  status?: WorkSessionStatus;
  from?: string;
  to?: string;
  include_deleted?: boolean;
  page?: number;
  limit?: number;
}

export async function listWorkSessions(
  accessToken: string,
  params: ListWorkSessionsParams = {},
): Promise<WorkSessionListResponse> {
  const query = new URLSearchParams();
  if (params.status) query.set('status', params.status);
  if (params.from) query.set('from', params.from);
  if (params.to) query.set('to', params.to);
  if (params.include_deleted) query.set('include_deleted', 'true');
  if (params.page) query.set('page', String(params.page));
  if (params.limit) query.set('limit', String(params.limit));
  const suffix = query.toString() ? `?${query.toString()}` : '';
  const response = await fetch(apiUrl(`/work-sessions${suffix}`), {
    headers: authHeaders(accessToken),
  });
  return parseJson<WorkSessionListResponse>(response);
}

export async function createWorkSession(
  accessToken: string,
  payload: WorkSessionUpsertPayload,
): Promise<WorkSession> {
  const response = await fetch(apiUrl('/work-sessions'), {
    method: 'POST',
    headers: authHeaders(accessToken),
    body: JSON.stringify(payload),
  });
  return parseJson<WorkSession>(response);
}

export async function getWorkSession(
  accessToken: string,
  sessionId: string,
): Promise<WorkSession> {
  const response = await fetch(apiUrl(`/work-sessions/${sessionId}`), {
    headers: authHeaders(accessToken),
  });
  return parseJson<WorkSession>(response);
}

export async function updateWorkSession(
  accessToken: string,
  sessionId: string,
  payload: WorkSessionUpsertPayload,
): Promise<WorkSession> {
  const response = await fetch(apiUrl(`/work-sessions/${sessionId}`), {
    method: 'PATCH',
    headers: authHeaders(accessToken),
    body: JSON.stringify(payload),
  });
  return parseJson<WorkSession>(response);
}

export async function deleteWorkSession(
  accessToken: string,
  sessionId: string,
): Promise<WorkSession> {
  const response = await fetch(apiUrl(`/work-sessions/${sessionId}`), {
    method: 'DELETE',
    headers: authHeaders(accessToken),
  });
  return parseJson<WorkSession>(response);
}

export async function restoreWorkSession(
  accessToken: string,
  sessionId: string,
): Promise<WorkSession> {
  const response = await fetch(apiUrl(`/work-sessions/${sessionId}/restore`), {
    method: 'POST',
    headers: authHeaders(accessToken),
  });
  return parseJson<WorkSession>(response);
}

export async function listAdminWorkSessions(
  accessToken: string,
  params: ListWorkSessionsParams = {},
): Promise<WorkSessionListResponse> {
  const query = new URLSearchParams();
  if (params.status) query.set('status', params.status);
  if (params.page) query.set('page', String(params.page));
  if (params.limit) query.set('limit', String(params.limit));
  const suffix = query.toString() ? `?${query.toString()}` : '';
  const response = await fetch(adminUrl(`/work-sessions${suffix}`), {
    headers: authHeaders(accessToken),
  });
  return parseJson<WorkSessionListResponse>(response);
}

/**
 * Authenticated Dissemination ops API client (EV-936 / UJ-071).
 */

import { apiUrl } from './apiBase';

/**
 * Function `authHeaders`.
 */
function authHeaders(accessToken: string): HeadersInit {
  return {
    Authorization: `Bearer ${accessToken}`,
    'Content-Type': 'application/json',
  };
}

/**
 * Function `parseJson`.
 */
async function parseJson<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    const detail =
      typeof error.detail === 'string' ? error.detail : response.statusText;
    throw new Error(detail || `HTTP ${response.status}`);
  }
  return response.json() as Promise<T>;
}

/**
 * Type `GatewayHealthRow`.
 * @example
 * const _ = true;
 */
export interface GatewayHealthRow {
  ok: boolean;
  gateway: string;
  connectivity_ok: boolean;
  detail?: string | null;
}

/**
 * Type `GatewayHealthListResponse`.
 * @example
 * const _ = true;
 */
export interface GatewayHealthListResponse {
  items: GatewayHealthRow[];
}

/**
 * Type `DisseminationPlanOut`.
 * @example
 * const _ = true;
 */
export interface DisseminationPlanOut {
  id: string;
  user_id: string;
  slug: string;
  validity_policy: string;
  destination_refs: string[];
  transforms: string[];
  retry?: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
}

/**
 * Type `DisseminationPlanCreate`.
 * @example
 * const _ = true;
 */
export interface DisseminationPlanCreate {
  slug: string;
  validity_policy?: 'valid-only' | 'warn-ok';
  destination_refs?: string[];
  transforms?: string[];
  retry?: Record<string, unknown> | null;
}

/**
 * Type `PlanExecuteResponse`.
 * @example
 * const _ = true;
 */
export interface PlanExecuteResponse {
  plan_id: string;
  receipts: Array<{
    status: string;
    gateway: string;
    detail?: string | null;
    attempt?: number;
    completed_at?: string | null;
  }>;
}

/**
 * Type `AuditRecordOut`.
 * @example
 * const _ = true;
 */
export interface AuditRecordOut {
  id: string;
  user_id: string;
  message_id?: string | null;
  station?: string | null;
  profile?: string | null;
  iwxxm_version?: string | null;
  product?: string | null;
  status: string;
  gateway: string;
  detail?: string | null;
  destinations: Record<string, unknown>;
  created_at: string;
}

/**
 * Type `AuditListResponse`.
 * @example
 * const _ = true;
 */
export interface AuditListResponse {
  items: AuditRecordOut[];
  total: number;
  page: number;
  limit: number;
}

/**
 * Type `MappingConfigOut`.
 * @example
 * const _ = true;
 */
export interface MappingConfigOut {
  id: string;
  user_id: string;
  name: string;
  mode: string;
  config: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

/**
 * Type `MappingConfigCreate`.
 * @example
 * const _ = true;
 */
export interface MappingConfigCreate {
  name: string;
  mode: 'source' | 'sink';
  config?: Record<string, unknown>;
}

/**
 * GET /api/v1/dissemination/gateways/health
 * @example
 * const _ = true;
 */
export async function fetchGatewayHealth(
  accessToken: string,
): Promise<GatewayHealthListResponse> {
  const response = await fetch(apiUrl('/dissemination/gateways/health'), {
    headers: authHeaders(accessToken),
  });
  return parseJson(response);
}

/**
 * PUT /api/v1/dissemination/plans/{slug}
 * @example
 * const _ = true;
 */
export async function upsertDisseminationPlan(
  accessToken: string,
  slug: string,
  payload: DisseminationPlanCreate,
): Promise<DisseminationPlanOut> {
  const response = await fetch(
    apiUrl(`/dissemination/plans/${encodeURIComponent(slug)}`),
    {
      method: 'PUT',
      headers: authHeaders(accessToken),
      body: JSON.stringify({ ...payload, slug }),
    },
  );
  return parseJson(response);
}

/**
 * POST /api/v1/dissemination/plans/{id}/execute
 * @example
 * const _ = true;
 */
export async function executeDisseminationPlan(
  accessToken: string,
  planId: string,
  body: {
    dry_run?: boolean;
    message_id?: string;
    station?: string;
    product?: string;
  } = {},
): Promise<PlanExecuteResponse> {
  const response = await fetch(
    apiUrl(`/dissemination/plans/${encodeURIComponent(planId)}/execute`),
    {
      method: 'POST',
      headers: authHeaders(accessToken),
      body: JSON.stringify({ dry_run: true, ...body }),
    },
  );
  return parseJson(response);
}

/**
 * GET /api/v1/dissemination/audit
 * @example
 * const _ = true;
 */
export async function listDisseminationAudit(
  accessToken: string,
  params: { page?: number; limit?: number } = {},
): Promise<AuditListResponse> {
  const query = new URLSearchParams();
  if (params.page) query.set('page', String(params.page));
  if (params.limit) query.set('limit', String(params.limit));
  const suffix = query.toString() ? `?${query.toString()}` : '';
  const response = await fetch(apiUrl(`/dissemination/audit${suffix}`), {
    headers: authHeaders(accessToken),
  });
  return parseJson(response);
}

/**
 * PUT /api/v1/dissemination/mappings/{name}
 * @example
 * const _ = true;
 */
export async function upsertMappingConfig(
  accessToken: string,
  name: string,
  payload: MappingConfigCreate,
): Promise<MappingConfigOut> {
  const response = await fetch(
    apiUrl(`/dissemination/mappings/${encodeURIComponent(name)}`),
    {
      method: 'PUT',
      headers: authHeaders(accessToken),
      body: JSON.stringify({ ...payload, name }),
    },
  );
  return parseJson(response);
}

/**
 * Authenticated ConversionProfile API client (EV-933 / UJ-072 / F7.w).
 */

import { apiUrl } from './apiBase';

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
  if (response.status === 204) {
    return undefined as T;
  }
  return response.json() as Promise<T>;
}

/** Catalog profile entry (inspector). */
export interface ProfileCatalogEntry {
  id: string;
  kind: string;
  status?: string | null;
  priority?: string | null;
  products: string[];
  legacy_alias?: string | null;
  emit_key?: string | null;
  vendor_pins?: Record<string, unknown>;
  implementation?: Record<string, unknown>;
}

export interface ProfileCatalogResponse {
  schema_version?: number | string | null;
  profiles: ProfileCatalogEntry[];
}

/** Persisted rule pack. */
export interface RulePackOut {
  id: string;
  user_id: string;
  slug: string;
  profile: string;
  product: string;
  stage: string;
  severity: string;
  when: string;
  message: string;
  standardReference: string;
  created_at: string;
  updated_at: string;
}

export interface RulePackListResponse {
  items: RulePackOut[];
}

export interface RulePackCreateBody {
  slug: string;
  profile: string;
  product: string;
  stage: string;
  severity: string;
  when?: string;
  message?: string;
  standardReference?: string;
}

/**
 * Fetch read-only ConversionProfile catalog.
 *
 * @param accessToken - Bearer JWT
 */
export async function fetchProfileCatalog(
  accessToken: string,
): Promise<ProfileCatalogResponse> {
  const response = await fetch(apiUrl('/api/v1/profiles/catalog'), {
    headers: authHeaders(accessToken),
  });
  return parseJson(response);
}

/**
 * List rule packs for the signed-in user.
 *
 * @param accessToken - Bearer JWT
 */
export async function listRulePacks(
  accessToken: string,
): Promise<RulePackListResponse> {
  const response = await fetch(apiUrl('/api/v1/profiles/rule-packs'), {
    headers: authHeaders(accessToken),
  });
  return parseJson(response);
}

/**
 * Create a rule pack.
 *
 * @param accessToken - Bearer JWT
 * @param body - Pack fields
 */
export async function createRulePack(
  accessToken: string,
  body: RulePackCreateBody,
): Promise<RulePackOut> {
  const response = await fetch(apiUrl('/api/v1/profiles/rule-packs'), {
    method: 'POST',
    headers: authHeaders(accessToken),
    body: JSON.stringify(body),
  });
  return parseJson(response);
}

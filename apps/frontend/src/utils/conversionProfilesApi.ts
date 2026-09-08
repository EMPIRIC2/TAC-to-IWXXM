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

/** Catalog variant row for profile-scoped METAR-family roots. */
export interface MetarFamilyVariant {
  tac_lead: string;
  api_product: string;
  iwxxm_root: string;
  rule_id?: string | null;
  rule_id_prefix?: string | null;
  minimal_observation?: boolean | null;
  manobs?: string | null;
  notes?: string | null;
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
  deltas_vs_icao?: string[];
  iwxxm_line?: string | null;
  metar_family_variants?: MetarFamilyVariant[];
  rule_pack_count?: number | null;
  overlay_count?: number | null;
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

export interface RulePackUpdateBody {
  slug?: string;
  profile?: string;
  product?: string;
  stage?: string;
  severity?: string;
  when?: string;
  message?: string;
  standardReference?: string;
}

export interface PresetOut {
  id: string;
  user_id: string;
  slug: string;
  name: string;
  semanticProfile: string;
  iwxxmVersion: string;
  extensions: string[];
  reportVariant?: string | null;
  overlayId?: string | null;
  shared: boolean;
  created_at: string;
  updated_at: string;
}

export interface PresetListResponse {
  items: PresetOut[];
}

export interface DisseminationTemplateOut {
  id: string;
  user_id: string;
  slug: string;
  name: string;
  sinkType: string;
  product?: string | null;
  ddl: boolean;
  params: Record<string, unknown>;
  shared: boolean;
  created_at: string;
  updated_at: string;
}

export interface DisseminationTemplateListResponse {
  items: DisseminationTemplateOut[];
}

export interface DisseminationTemplateCreateBody {
  slug: string;
  name: string;
  sinkType: string;
  product?: string | null;
  ddl?: boolean;
  params?: Record<string, unknown>;
  shared?: boolean;
}

export interface DisseminationTemplateUpdateBody {
  slug?: string;
  name?: string;
  sinkType?: string;
  product?: string | null;
  ddl?: boolean;
  params?: Record<string, unknown>;
  shared?: boolean;
}

export interface PresetCreateBody {
  slug: string;
  name: string;
  semanticProfile: string;
  iwxxmVersion: string;
  extensions?: string[];
  reportVariant?: string | null;
  overlayId?: string | null;
  shared?: boolean;
}

export interface PresetUpdateBody {
  slug?: string;
  name?: string;
  semanticProfile?: string;
  iwxxmVersion?: string;
  extensions?: string[];
  reportVariant?: string | null;
  overlayId?: string | null;
  shared?: boolean;
}

/** Persisted signed overlay. */
export interface OverlayOut {
  id: string;
  user_id: string;
  slug: string;
  baseProfileId: string;
  body: Record<string, unknown>;
  signature: string;
  shared: boolean;
  created_at: string;
  updated_at: string;
}

export interface OverlayListResponse {
  items: OverlayOut[];
}

export interface OverlayCreateBody {
  slug: string;
  baseProfileId: string;
  body?: Record<string, unknown>;
  shared?: boolean;
}

export interface OverlayUpdateBody {
  slug?: string;
  baseProfileId?: string;
  body?: Record<string, unknown>;
  shared?: boolean;
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
 * List semantic presets for the signed-in user.
 *
 * @param accessToken - Bearer JWT
 */
export async function listPresets(accessToken: string): Promise<PresetListResponse> {
  const response = await fetch(apiUrl('/api/v1/profiles/presets'), {
    headers: authHeaders(accessToken),
  });
  return parseJson(response);
}

/**
 * List dissemination templates for the signed-in user.
 *
 * @param accessToken - Bearer JWT
 */
export async function listTemplates(
  accessToken: string,
): Promise<DisseminationTemplateListResponse> {
  const response = await fetch(apiUrl('/api/v1/profiles/templates'), {
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

/**
 * Update one rule pack.
 *
 * @param accessToken - Bearer JWT
 * @param packId - Persisted pack id
 * @param body - Partial pack fields
 */
export async function updateRulePack(
  accessToken: string,
  packId: string,
  body: RulePackUpdateBody,
): Promise<RulePackOut> {
  const response = await fetch(apiUrl(`/api/v1/profiles/rule-packs/${packId}`), {
    method: 'PATCH',
    headers: authHeaders(accessToken),
    body: JSON.stringify(body),
  });
  return parseJson(response);
}

/**
 * Delete one rule pack.
 *
 * @param accessToken - Bearer JWT
 * @param packId - Persisted pack id
 */
export async function deleteRulePack(
  accessToken: string,
  packId: string,
): Promise<void> {
  const response = await fetch(apiUrl(`/api/v1/profiles/rule-packs/${packId}`), {
    method: 'DELETE',
    headers: authHeaders(accessToken),
  });
  await parseJson<unknown>(response);
}

/**
 * Create a semantic preset.
 *
 * @param accessToken - Bearer JWT
 * @param body - Preset fields
 */
export async function createPreset(
  accessToken: string,
  body: PresetCreateBody,
): Promise<PresetOut> {
  const response = await fetch(apiUrl('/api/v1/profiles/presets'), {
    method: 'POST',
    headers: authHeaders(accessToken),
    body: JSON.stringify(body),
  });
  return parseJson(response);
}

/**
 * Update one semantic preset.
 *
 * @param accessToken - Bearer JWT
 * @param presetId - Persisted preset id
 * @param body - Partial preset fields
 */
export async function updatePreset(
  accessToken: string,
  presetId: string,
  body: PresetUpdateBody,
): Promise<PresetOut> {
  const response = await fetch(apiUrl(`/api/v1/profiles/presets/${presetId}`), {
    method: 'PATCH',
    headers: authHeaders(accessToken),
    body: JSON.stringify(body),
  });
  return parseJson(response);
}

/**
 * Delete one semantic preset.
 *
 * @param accessToken - Bearer JWT
 * @param presetId - Persisted preset id
 */
export async function deletePreset(
  accessToken: string,
  presetId: string,
): Promise<void> {
  const response = await fetch(apiUrl(`/api/v1/profiles/presets/${presetId}`), {
    method: 'DELETE',
    headers: authHeaders(accessToken),
  });
  await parseJson<unknown>(response);
}

/**
 * Create a dissemination template.
 *
 * @param accessToken - Bearer JWT
 * @param body - Template fields
 */
export async function createTemplate(
  accessToken: string,
  body: DisseminationTemplateCreateBody,
): Promise<DisseminationTemplateOut> {
  const response = await fetch(apiUrl('/api/v1/profiles/templates'), {
    method: 'POST',
    headers: authHeaders(accessToken),
    body: JSON.stringify(body),
  });
  return parseJson(response);
}

/**
 * Update one dissemination template.
 *
 * @param accessToken - Bearer JWT
 * @param templateId - Persisted template id
 * @param body - Partial template fields
 */
export async function updateTemplate(
  accessToken: string,
  templateId: string,
  body: DisseminationTemplateUpdateBody,
): Promise<DisseminationTemplateOut> {
  const response = await fetch(apiUrl(`/api/v1/profiles/templates/${templateId}`), {
    method: 'PATCH',
    headers: authHeaders(accessToken),
    body: JSON.stringify(body),
  });
  return parseJson(response);
}

/**
 * Delete one dissemination template.
 *
 * @param accessToken - Bearer JWT
 * @param templateId - Persisted template id
 */
export async function deleteTemplate(
  accessToken: string,
  templateId: string,
): Promise<void> {
  const response = await fetch(apiUrl(`/api/v1/profiles/templates/${templateId}`), {
    method: 'DELETE',
    headers: authHeaders(accessToken),
  });
  await parseJson<unknown>(response);
}

/**
 * List signed overlays for the signed-in user.
 *
 * @param accessToken - Bearer JWT
 */
export async function listOverlays(accessToken: string): Promise<OverlayListResponse> {
  const response = await fetch(apiUrl('/api/v1/profiles/overlays'), {
    headers: authHeaders(accessToken),
  });
  return parseJson(response);
}

/**
 * Create a server-signed overlay.
 *
 * @param accessToken - Bearer JWT
 * @param body - Overlay fields
 */
export async function createOverlay(
  accessToken: string,
  body: OverlayCreateBody,
): Promise<OverlayOut> {
  const response = await fetch(apiUrl('/api/v1/profiles/overlays'), {
    method: 'POST',
    headers: authHeaders(accessToken),
    body: JSON.stringify(body),
  });
  return parseJson(response);
}

/**
 * Update one overlay.
 *
 * @param accessToken - Bearer JWT
 * @param overlayId - Persisted overlay id
 * @param body - Partial overlay fields
 */
export async function updateOverlay(
  accessToken: string,
  overlayId: string,
  body: OverlayUpdateBody,
): Promise<OverlayOut> {
  const response = await fetch(apiUrl(`/api/v1/profiles/overlays/${overlayId}`), {
    method: 'PATCH',
    headers: authHeaders(accessToken),
    body: JSON.stringify(body),
  });
  return parseJson(response);
}

/**
 * Delete one overlay.
 *
 * @param accessToken - Bearer JWT
 * @param overlayId - Persisted overlay id
 */
export async function deleteOverlay(
  accessToken: string,
  overlayId: string,
): Promise<void> {
  const response = await fetch(apiUrl(`/api/v1/profiles/overlays/${overlayId}`), {
    method: 'DELETE',
    headers: authHeaders(accessToken),
  });
  await parseJson<unknown>(response);
}

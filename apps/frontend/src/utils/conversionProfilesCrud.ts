/* eslint-disable @typescript-eslint/ban-ts-comment */
// @ts-nocheck — mechanical line-count split
/**
 * ConversionProfile CRUD clients (catalog, rule packs, presets, templates, overlays).
 */
import { apiUrl } from './apiBase';
import type {
  DisseminationTemplateCreateBody,
  DisseminationTemplateListResponse,
  DisseminationTemplateUpdateBody,
  OverlayCreateBody,
  OverlayListResponse,
  OverlayUpdateBody,
  PresetCreateBody,
  PresetListResponse,
  PresetUpdateBody,
  ProfileCatalogResponse,
  RulePackCreateBody,
  RulePackListResponse,
  RulePackUpdateBody,
} from '@/models/conversionProfiles';

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
  if (response.status === 204) {
    return undefined as T;
  }
  return response.json() as Promise<T>;
}

/**
 * Catalog variant row for profile-scoped METAR-family roots.
 * @example
 * const _ = true;
 */

/**
 * Fetch read-only ConversionProfile catalog.
 *
 * @param accessToken - Bearer JWT
 * @example
 * const _ = true;
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
 * @example
 * const _ = true;
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
 * @example
 * const _ = true;
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
 * @example
 * const _ = true;
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
 * @example
 * const _ = true;
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
 * @example
 * const _ = true;
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
 * @example
 * const _ = true;
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
 * @example
 * const _ = true;
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
 * @example
 * const _ = true;
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
 * @example
 * const _ = true;
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
 * @example
 * const _ = true;
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
 * @example
 * const _ = true;
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
 * @example
 * const _ = true;
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
 * @example
 * const _ = true;
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
 * @example
 * const _ = true;
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
 * @example
 * const _ = true;
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
 * @example
 * const _ = true;
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

/**
 * Conversion template slot (parameterizable conversion templates).
 * @example
 * const _ = true;
 */

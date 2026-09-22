/**
 * Authenticated ConversionProfile API client (EV-933 / UJ-072 / F7.w).
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

/**
 * Catalog profile entry (inspector).
 * @example
 * const _ = true;
 */
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

/**
 * Type `ProfileCatalogResponse`.
 * @example
 * const _ = true;
 */
export interface ProfileCatalogResponse {
  schema_version?: number | string | null;
  profiles: ProfileCatalogEntry[];
}

/**
 * Persisted rule pack.
 * @example
 * const _ = true;
 */
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

/**
 * Type `RulePackListResponse`.
 * @example
 * const _ = true;
 */
export interface RulePackListResponse {
  items: RulePackOut[];
}

/**
 * Type `RulePackCreateBody`.
 * @example
 * const _ = true;
 */
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
 * Type `RulePackUpdateBody`.
 * @example
 * const _ = true;
 */
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

/**
 * Type `PresetOut`.
 * @example
 * const _ = true;
 */
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

/**
 * Type `PresetListResponse`.
 * @example
 * const _ = true;
 */
export interface PresetListResponse {
  items: PresetOut[];
}

/**
 * Type `DisseminationTemplateOut`.
 * @example
 * const _ = true;
 */
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

/**
 * Type `DisseminationTemplateListResponse`.
 * @example
 * const _ = true;
 */
export interface DisseminationTemplateListResponse {
  items: DisseminationTemplateOut[];
}

/**
 * Type `DisseminationTemplateCreateBody`.
 * @example
 * const _ = true;
 */
export interface DisseminationTemplateCreateBody {
  slug: string;
  name: string;
  sinkType: string;
  product?: string | null;
  ddl?: boolean;
  params?: Record<string, unknown>;
  shared?: boolean;
}

/**
 * Type `DisseminationTemplateUpdateBody`.
 * @example
 * const _ = true;
 */
export interface DisseminationTemplateUpdateBody {
  slug?: string;
  name?: string;
  sinkType?: string;
  product?: string | null;
  ddl?: boolean;
  params?: Record<string, unknown>;
  shared?: boolean;
}

/**
 * Type `PresetCreateBody`.
 * @example
 * const _ = true;
 */
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

/**
 * Type `PresetUpdateBody`.
 * @example
 * const _ = true;
 */
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

/**
 * Persisted signed overlay.
 * @example
 * const _ = true;
 */
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

/**
 * Type `OverlayListResponse`.
 * @example
 * const _ = true;
 */
export interface OverlayListResponse {
  items: OverlayOut[];
}

/**
 * Type `OverlayCreateBody`.
 * @example
 * const _ = true;
 */
export interface OverlayCreateBody {
  slug: string;
  baseProfileId: string;
  body?: Record<string, unknown>;
  shared?: boolean;
}

/**
 * Type `OverlayUpdateBody`.
 * @example
 * const _ = true;
 */
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
export interface ConversionTemplateSlot {
  id: string;
  label: string;
  type: string;
  optional?: boolean;
  digits?: number | null;
  enumValues?: string | null;
  literal?: string | null;
  iwxxmField?: string;
  /** convert | decode_only | skip */
  mode?: string;
  gloss?: string;
}

/**
 * Conversion template (first-party or custom).
 * @example
 * const _ = true;
 */
export interface ConversionTemplateOut {
  id: string;
  user_id?: string | null;
  slug: string;
  name: string;
  access: string;
  iwxxmBlock: string;
  slots: ConversionTemplateSlot[];
  sample?: string;
  comments?: string | null;
  forkOf?: string | null;
  shared?: boolean;
  profiles?: string[];
  created_at?: string | null;
  updated_at?: string | null;
}

/**
 * Type `ConversionTemplateListResponse`.
 * @example
 * const _ = true;
 */
export interface ConversionTemplateListResponse {
  items: ConversionTemplateOut[];
}

/**
 * Five Libraries asset kinds (Profile builder + Convert pickers).
 * @example
 * const _ = true;
 */
export type LibraryAssetKind =
  | 'conversion'
  | 'tac_validation'
  | 'iwxxm_validation'
  | 'dissemination'
  | 'decoding';

/**
 * First-party or custom library asset.
 * @example
 * const _ = true;
 */
export interface LibraryAssetOut {
  id: string;
  kind: LibraryAssetKind;
  name: string;
  access: 'first_party' | 'custom' | string;
  engineProfileId: string;
  attachedNationalLine: string;
  body?: Record<string, unknown>;
  forkOf?: string | null;
  userId?: string | null;
  slug?: string | null;
  shared?: boolean;
  created_at?: string | null;
  updated_at?: string | null;
  yamlBody?: string | null;
  status?: 'draft' | 'activated' | string | null;
  schemaVersion?: number | null;
}

/**
 * Type `LibraryAssetListResponse`.
 * @example
 * const _ = true;
 */
export interface LibraryAssetListResponse {
  items: LibraryAssetOut[];
}

/**
 * List first-party and owner custom library assets.
 *
 * @param accessToken - Bearer JWT
 * @param kind - Optional kind filter
 * @example
 * const _ = true;
 */
export async function listLibraryAssets(
  accessToken: string,
  kind?: LibraryAssetKind,
): Promise<LibraryAssetListResponse> {
  const query = kind ? `?kind=${encodeURIComponent(kind)}` : '';
  const response = await fetch(apiUrl(`/api/v1/profiles/library-assets${query}`), {
    headers: authHeaders(accessToken),
  });
  return parseJson(response);
}

/**
 * Type `LibraryYamlValidateResponse`.
 * @example
 * const _ = true;
 */
export interface LibraryYamlValidateResponse {
  valid_yaml: boolean;
  yaml_error: string | null;
  kind: LibraryAssetKind | null;
  name: string | null;
  lifecycle: 'draft' | 'activated';
  fail_count: number;
  warn_count: number;
  can_activate: boolean;
  diagnostics: Array<{
    path: string;
    pattern: string;
    severity: 'ok' | 'warn' | 'fail';
    message: string;
    captures: Array<{ index: number; name: string }>;
    sample_matched: boolean | null;
  }>;
}

/**
 * Validate library YAML + regex without persisting.
 *
 * @param accessToken - Bearer JWT
 * @param body - YAML + expected kind
 * @example
 * const _ = true;
 */
export async function validateLibraryYaml(
  accessToken: string,
  body: {
    yamlBody: string;
    kind: LibraryAssetKind;
    lifecycle?: 'draft' | 'activated';
  },
): Promise<LibraryYamlValidateResponse> {
  const response = await fetch(
    apiUrl('/api/v1/profiles/library-assets/validate-yaml'),
    {
      method: 'POST',
      headers: authHeaders(accessToken),
      body: JSON.stringify(body),
    },
  );
  return parseJson(response);
}

/**
 * Create a custom library asset (draft or activated).
 *
 * @param accessToken - Bearer JWT
 * @param body - Create payload
 * @example
 * const _ = true;
 */
export async function createLibraryAsset(
  accessToken: string,
  body: {
    slug: string;
    name: string;
    kind: LibraryAssetKind;
    engineProfileId: string;
    attachedNationalLine: string;
    body?: Record<string, unknown>;
    forkOf?: string;
    shared?: boolean;
    yamlBody?: string;
    status?: 'draft' | 'activated';
    schemaVersion?: number;
  },
): Promise<LibraryAssetOut> {
  const response = await fetch(apiUrl('/api/v1/profiles/library-assets'), {
    method: 'POST',
    headers: authHeaders(accessToken),
    body: JSON.stringify(body),
  });
  return parseJson(response);
}

/**
 * Patch an owned custom library asset.
 *
 * @param accessToken - Bearer JWT
 * @param assetId - Custom asset UUID
 * @param body - Partial update
 * @example
 * const _ = true;
 */
export async function updateLibraryAsset(
  accessToken: string,
  assetId: string,
  body: {
    name?: string;
    yamlBody?: string;
    status?: 'draft' | 'activated';
    body?: Record<string, unknown>;
  },
): Promise<LibraryAssetOut> {
  const response = await fetch(
    apiUrl(`/api/v1/profiles/library-assets/${encodeURIComponent(assetId)}`),
    {
      method: 'PATCH',
      headers: authHeaders(accessToken),
      body: JSON.stringify(body),
    },
  );
  return parseJson(response);
}

/**
 * Type `ConversionTemplatePreviewResponse`.
 * @example
 * const _ = true;
 */
export interface ConversionTemplatePreviewResponse {
  templateId: string;
  focusGroup: string;
  matched: boolean;
  captures: Array<Record<string, string>>;
  xmlBlock: string;
  compiledPattern: string;
  skipped?: Array<Record<string, string>>;
}

/**
 * List first-party and custom conversion templates.
 *
 * @param accessToken - Bearer JWT
 * @example
 * const _ = true;
 */
export async function listConversionTemplates(
  accessToken: string,
): Promise<ConversionTemplateListResponse> {
  const response = await fetch(apiUrl('/api/v1/profiles/conversion-templates'), {
    headers: authHeaders(accessToken),
  });
  return parseJson(response);
}

/**
 * Preview TAC group mapping for a conversion template.
 *
 * @param accessToken - Bearer JWT
 * @param body - Preview request
 * @example
 * const _ = true;
 */
export async function previewConversionTemplate(
  accessToken: string,
  body: {
    templateId: string;
    focusGroup: string;
    fullTac?: string;
    slots?: ConversionTemplateSlot[];
    iwxxmBlock?: string;
  },
): Promise<ConversionTemplatePreviewResponse> {
  const response = await fetch(
    apiUrl('/api/v1/profiles/conversion-templates/preview'),
    {
      method: 'POST',
      headers: authHeaders(accessToken),
      body: JSON.stringify(body),
    },
  );
  return parseJson(response);
}

/**
 * Create a custom conversion template (often a fork).
 *
 * @param accessToken - Bearer JWT
 * @param body - Create payload
 * @example
 * const _ = true;
 */
export async function createConversionTemplate(
  accessToken: string,
  body: {
    slug: string;
    name: string;
    iwxxmBlock: string;
    slots: ConversionTemplateSlot[];
    sample?: string;
    comments?: string;
    forkOf?: string;
    shared?: boolean;
  },
): Promise<ConversionTemplateOut> {
  const response = await fetch(apiUrl('/api/v1/profiles/conversion-templates'), {
    method: 'POST',
    headers: authHeaders(accessToken),
    body: JSON.stringify(body),
  });
  return parseJson(response);
}

/**
 * Update an owned custom conversion template (fails closed for first-party ids).
 *
 * @param accessToken - Bearer JWT
 * @param templateId - Custom template id
 * @param body - Partial update (camelCase aliases)
 * @example
 * const _ = true;
 */
export async function updateConversionTemplate(
  accessToken: string,
  templateId: string,
  body: {
    slug?: string;
    name?: string;
    iwxxmBlock?: string;
    slots?: ConversionTemplateSlot[];
    sample?: string;
    comments?: string | null;
    shared?: boolean;
  },
): Promise<ConversionTemplateOut> {
  const response = await fetch(
    apiUrl(`/api/v1/profiles/conversion-templates/${encodeURIComponent(templateId)}`),
    {
      method: 'PATCH',
      headers: authHeaders(accessToken),
      body: JSON.stringify(body),
    },
  );
  return parseJson(response);
}

/** Conversion profile catalog / rule-pack / preset / overlay API shapes. */

/**
 * Opaque vendor pin map on a catalog profile entry.
 * @example
 * const _ = true;
 */
export interface ProfileVendorPins {
  [key: string]: unknown;
}

/**
 * Opaque implementation metadata on a catalog profile entry.
 * @example
 * const _ = true;
 */
export interface ProfileImplementationMeta {
  [key: string]: unknown;
}

/**
 * JSON-like object for overlay bodies and dissemination template params.
 * @example
 * const _ = true;
 */
export interface JsonObject {
  [key: string]: unknown;
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
  vendor_pins?: ProfileVendorPins;
  implementation?: ProfileImplementationMeta;
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
  params: JsonObject;
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
  params?: JsonObject;
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
  params?: JsonObject;
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
  body: JsonObject;
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
  body?: JsonObject;
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
  body?: JsonObject;
  shared?: boolean;
}

/**
 * Fetch read-only ConversionProfile catalog.
 *
 * @param accessToken - Bearer JWT
 * @example
 * const _ = true;
 */

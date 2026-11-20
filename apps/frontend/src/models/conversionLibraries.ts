/** Library YAML asset and conversion-template API shapes. */

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
 * One capture map from a conversion-template preview.
 * @example
 * const _ = true;
 */
export interface ConversionTemplateCapture {
  [key: string]: string;
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
  captures: ConversionTemplateCapture[];
  xmlBlock: string;
  compiledPattern: string;
  skipped?: ConversionTemplateCapture[];
}

/**
 * Frontend-owned API wire types (non-OpenAPI aliases).
 */

/**
 * Type `HealthResponse`.
 * @example
 * const _ = true;
 */
export interface HealthResponse {
  status: 'healthy' | 'degraded';
  version: string;
  tac2iwxxm_available: boolean;
}

/**
 * Type `AirportRegionResponse`.
 * @example
 * const _ = true;
 */

/**
 * Type `AirportRegionResponse`.
 * @example
 * const _ = true;
 */
export interface AirportRegionResponse {
  airport_code: string;
  icao_region: string;
}

/**
 * Type `ApiError`.
 * @example
 * const _ = true;
 */

/**
 * Type `ApiError`.
 * @example
 * const _ = true;
 */
export interface ApiError {
  message: string;
  errors: string[];
  total_errors?: number;
}

/**
 * Structured hard-convert failure surfaced by the backend.
 *
 * Preserves ``detail.errors`` / ``detail.issues`` from non-2xx convert responses so
 * the workbench can render the same operator-facing log panel it uses for 200 responses
 * with partial or failed conversion details.
 * @example
 * const _ = true;
 */

/**
 * Per-file outcome from ``POST /api/v1/ingest/mass`` (F33).
 * @example
 * const _ = true;
 */
export interface MassIngestFileResult {
  name: string;
  accepted: boolean;
  reason: string | null;
  size_bytes: number;
  content: string | null;
}

/**
 * Response from ``POST /api/v1/ingest/mass`` (F33 / EV-042).
 * @example
 * const _ = true;
 */

/**
 * Response from ``POST /api/v1/ingest/mass`` (F33 / EV-042).
 * @example
 * const _ = true;
 */
export interface MassIngestResponse {
  accepted_count: number;
  rejected_count: number;
  results: MassIngestFileResult[];
}

/**
 * Auth-gated mass file/folder ingest with server-side caps and sniff guards.
 *
 * **Endpoint**: POST /api/v1/ingest/mass
 *
 * Client expands folder picks to files before upload; zip archives may be sent
 * as-is for server unpack ([Corpus: product §F33], [Corpus: api]).
 *
 * @param params.files - Multipart files and/or ``.zip`` archives
 * @param params.accessToken - Required Bearer JWT
 * @param params.signal - Optional abort signal
 * @returns Per-file accept/reject list and summary counts
 * @example
 * const _ = true;
 */

/**
 * One code-name dictionary row from GET /code-name-dictionary.
 * @example
 * const _ = true;
 */
export interface CodeNameDictionaryItem {
  id: string;
  code: string;
  meaning: string;
  products: string[];
  countries: string[];
  wmo_amendment: string | null;
}

/**
 * Facets for Code names filters.
 * @example
 * const _ = true;
 */

/**
 * Facets for Code names filters.
 * @example
 * const _ = true;
 */
export interface CodeNameDictionaryFacets {
  products: string[];
  countries: string[];
  wmo_amendments: string[];
}

/**
 * Fetch the tagged Decoding code-name dictionary.
 *
 * **Endpoint**: GET /api/v1/code-name-dictionary
 * @example
 * const _ = true;
 */

/**
 * Selection-option kinds for Convert (four) + Send drawer (dissemination).
 * @example
 * const _ = true;
 */
export type SelectionOptionKind =
  | 'conversion'
  | 'tac_validation'
  | 'iwxxm_validation'
  | 'decoding'
  | 'dissemination';

/**
 * Fetch deployed selection options for dropdowns (TP-YCL-01).
 *
 * **Endpoint**: GET /api/v1/selection-options
 * @example
 * const _ = true;
 */

/**
 * Schema status payload from GET schema-status.
 * @example
 * const _ = true;
 */
export interface SchemaStatusResponse {
  [key: string]: unknown;
}

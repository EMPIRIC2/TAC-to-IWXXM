/**
 * Backend API Client
 *
 * Handles all communication with the METAR to IWXXM backend API.
 * All endpoints use the versioned base path: /api/v1/
 */

import { apiUrl, getApiBaseUrl } from './apiBase';
import { apiErrorMessage, withTimeout } from './apiErrors';
import { DEFAULT_IWXXM_VERSION } from './iwxxmVersions';
import { wireSemanticProfile } from './semanticProfile';
import type {
  DecodeTacResponse,
  LintIssueCatalogResponse,
  LintTacResponse,
  ValidateResponse,
} from '@/models/openapi';
import type { AirportRegionResponse, HealthResponse } from '@/models/api';

export type {
  BulletinMeta,
  BulletinReportResult,
  ConversionIssue,
  ConversionResponse,
  ConversionResult,
  ConvertBulletinResponse,
  DecodeResidual,
  DecodeSegment,
  DecodeTacResponse,
  FailedSpan,
  LintFix,
  LintIssue,
  LintIssueCatalogEntry,
  LintIssueCatalogResponse,
  LintTacResponse,
  ValidateResponse,
} from '@/models/openapi';

export type {
  AirportRegionResponse,
  ApiError,
  CodeNameDictionaryFacets,
  CodeNameDictionaryItem,
  HealthResponse,
  MassIngestFileResult,
  MassIngestResponse,
  SchemaStatusResponse,
  SelectionOptionKind,
} from '@/models/api';

export { ConvertApiError, withTimeout } from './apiErrors';
import {
  convertMetarToIwxxm,
  convertBulletin,
  convertMetarToIwxxmZip,
} from './apiConvert';
export { convertMetarToIwxxm, convertBulletin, convertMetarToIwxxmZip };
import {
  EndpointNotImplementedError,
  ingestCollect,
  massIngestFiles,
  fetchRuleCatalog,
  fetchCodeNameDictionary,
  fetchSelectionOptions,
} from './apiCatalog';
export {
  EndpointNotImplementedError,
  ingestCollect,
  massIngestFiles,
  fetchRuleCatalog,
  fetchCodeNameDictionary,
  fetchSelectionOptions,
};

/**
 * Check backend health status
 *
 * **Endpoint**: GET /health
 * @example
 * const _ = true;
 */
export async function checkHealth(): Promise<HealthResponse> {
  try {
    const response = await fetch(`${getApiBaseUrl()}/health`, {
      method: 'GET',
    });

    if (!response.ok) {
      throw new Error(`Health check failed: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Health check error:', error);
    throw error;
  }
}

/**
 * Convert METAR/SPECI text to IWXXM XML
 *
 * Supports both manual text input and file uploads.
 *
 * **Endpoint**: POST /api/v1/convert
 *
 * @param params - Conversion parameters
 * @param params.manualText - Optional: METAR text to convert
 * @param params.files - Optional: File list to convert
 * @returns Conversion results with XML content
 * @example
 * const _ = true;
 */

/**
 * Lint TAC via tac-validate (parse gate + shared rules — not Schematron).
 *
 * **Endpoint**: POST /api/v1/lint-tac
 *
 * @param params.manualText - TAC text
 * @param params.product - Optional product hint
 * @param params.signal - AbortSignal for live workbench cancellation
 * @returns Lint report with optional start/end spans
 * @example
 * const _ = true;
 */
export async function lintTac(params: {
  manualText: string;
  product?: string;
  accessToken?: string;
  signal?: AbortSignal;
}): Promise<LintTacResponse> {
  const formData = new FormData();
  formData.append('manual_text', params.manualText);
  if (params.product) {
    formData.append('product', params.product.toUpperCase());
  }

  const response = await withTimeout(
    fetch(apiUrl('/lint-tac'), {
      method: 'POST',
      body: formData,
      signal: params.signal,
    }),
    15000,
  );

  if (!response.ok) {
    const error = await response.json().catch(() => ({
      message: `Lint failed: ${response.statusText}`,
    }));
    throw new Error(apiErrorMessage(error, `HTTP ${response.status}`));
  }

  return (await response.json()) as LintTacResponse;
}

/**
 * Run layered IWXXM validation (TAC and/or XML).
 *
 * **Endpoint**: POST /api/v1/validate
 *
 * @param params.manualText - Optional TAC to convert then validate
 * @param params.xmlContent - Optional IWXXM XML to validate directly
 * @returns Layered validation report (`ValidateResponse`)
 * @example
 * const _ = true;
 */

/**
 * Run layered IWXXM validation (TAC and/or XML).
 *
 * **Endpoint**: POST /api/v1/validate
 *
 * @param params.manualText - Optional TAC to convert then validate
 * @param params.xmlContent - Optional IWXXM XML to validate directly
 * @returns Layered validation report (`ValidateResponse`)
 * @example
 * const _ = true;
 */
export async function validateIwxxm(params: {
  manualText?: string;
  xmlContent?: string;
  product?: string;
  profile?: string;
  iwxxmVersion?: string;
  layers?: string[];
  stopOnError?: boolean;
  extensions?: string[];
  accessToken?: string;
  signal?: AbortSignal;
}): Promise<ValidateResponse> {
  const formData = new FormData();
  if (params.manualText?.trim()) {
    formData.append('manual_text', params.manualText.trim());
  }
  if (params.xmlContent?.trim()) {
    formData.append('xml_content', params.xmlContent.trim());
  }
  formData.append('semantic_profile', wireSemanticProfile(params.profile));
  formData.append('iwxxm_version', params.iwxxmVersion || DEFAULT_IWXXM_VERSION);
  formData.append('stop_on_error', params.stopOnError === false ? 'false' : 'true');
  const layers = params.layers?.length ? params.layers : ['ALL'];
  for (const layer of layers) {
    formData.append('layers', layer);
  }

  if (params.extensions?.length) {
    for (const token of params.extensions) {
      formData.append('extensions', token);
    }
  }

  const response = await withTimeout(
    fetch(apiUrl('/validate'), {
      method: 'POST',
      body: formData,
      signal: params.signal,
    }),
    60000,
  );

  if (!response.ok) {
    const error = await response.json().catch(() => ({
      message: `Validation failed: ${response.statusText}`,
    }));
    throw new Error(apiErrorMessage(error, `HTTP ${response.status}`));
  }

  return (await response.json()) as ValidateResponse;
}

/**
 * Fetch IWXXM schema / profile pin status from the API.
 *
 * **Endpoint**: GET /api/v1/schema-status
 * @example
 * const _ = true;
 */

/**
 * Fetch IWXXM schema / profile pin status from the API.
 *
 * **Endpoint**: GET /api/v1/schema-status
 * @example
 * const _ = true;
 */
export async function fetchSchemaStatus(): Promise<{
  profile_pins?: {
    ca_eccc?: {
      iwxxm_version?: string;
      extension_bundle_available?: boolean;
    };
  };
}> {
  const response = await withTimeout(fetch(apiUrl('/schema-status')), 15000);
  if (!response.ok) {
    throw new Error(`Schema status request failed: HTTP ${response.status}`);
  }
  return (await response.json()) as {
    profile_pins?: {
      ca_eccc?: {
        iwxxm_version?: string;
        extension_bundle_available?: boolean;
      };
    };
  };
}

/**
 * Fetch the tac-validate issue registry catalog (F15 / E11-31).
 *
 * **Endpoint**: GET /api/v1/lint-issue-catalog
 * @example
 * const _ = true;
 */

/**
 * Fetch the tac-validate issue registry catalog (F15 / E11-31).
 *
 * **Endpoint**: GET /api/v1/lint-issue-catalog
 * @example
 * const _ = true;
 */
export async function fetchLintIssueCatalog(params?: {
  product?: string;
  family?: string;
  issue_type?: string;
  source_access?: string;
  semantic_profile?: string;
  exchange_profile?: string;
  accessToken?: string;
  signal?: AbortSignal;
}): Promise<LintIssueCatalogResponse> {
  const query = new URLSearchParams();
  if (params?.product && params.product.trim()) {
    query.set('product', params.product.trim().toLowerCase());
  }
  if (params?.family && params.family.trim()) {
    query.set('family', params.family.trim().toLowerCase());
  }
  if (params?.issue_type && params.issue_type.trim()) {
    query.set('issue_type', params.issue_type.trim().toLowerCase());
  }
  if (params?.source_access && params.source_access.trim()) {
    query.set('source_access', params.source_access.trim().toLowerCase());
  }
  if (params?.semantic_profile && params.semantic_profile.trim()) {
    query.set('semantic_profile', params.semantic_profile.trim());
  }
  if (params?.exchange_profile && params.exchange_profile.trim()) {
    query.set('exchange_profile', params.exchange_profile.trim());
  }
  const qs = query.toString() ? `?${query.toString()}` : '';
  const response = await withTimeout(
    fetch(apiUrl(`/lint-issue-catalog${qs}`), {
      method: 'GET',
      signal: params?.signal,
    }),
    15000,
  );

  if (!response.ok) {
    const error = await response.json().catch(() => ({
      message: `Catalog fetch failed: ${response.statusText}`,
    }));
    throw new Error(apiErrorMessage(error, `HTTP ${response.status}`));
  }

  return (await response.json()) as LintIssueCatalogResponse;
}

/**
 * Decode TAC into ordered Code | Explanation segments.
 *
 * **Endpoint**: POST /api/v1/decode-tac
 *
 * @param params.manualText - TAC text
 * @param params.product - Required F6 product id
 * @returns Ordered segments and residuals
 * @example
 * const _ = true;
 */

/**
 * Decode TAC into ordered Code | Explanation segments.
 *
 * **Endpoint**: POST /api/v1/decode-tac
 *
 * @param params.manualText - TAC text
 * @param params.product - Required F6 product id
 * @returns Ordered segments and residuals
 * @example
 * const _ = true;
 */
export async function decodeTac(params: {
  manualText: string;
  product: string;
  accessToken?: string;
  signal?: AbortSignal;
}): Promise<DecodeTacResponse> {
  const formData = new FormData();
  formData.append('manual_text', params.manualText);
  formData.append('product', params.product.toUpperCase());

  const response = await withTimeout(
    fetch(apiUrl('/decode-tac'), {
      method: 'POST',
      body: formData,
      signal: params.signal,
    }),
    15000,
  );

  if (!response.ok) {
    const error = await response.json().catch(() => ({
      message: `Decode failed: ${response.statusText}`,
    }));
    throw new Error(apiErrorMessage(error, `HTTP ${response.status}`));
  }

  return (await response.json()) as DecodeTacResponse;
}

/**
 * Convert METAR/SPECI text to IWXXM XML in a ZIP file
 *
 * Supports batch conversion with both text and files.
 * Returns a ZIP archive containing converted XML files.
 *
 * **Endpoint**: POST /api/v1/convert-zip
 *
 * @param params - Conversion parameters
 * @param params.manualText - Optional: METAR text to convert
 * @param params.files - Optional: File list to convert
 * @returns Blob containing ZIP file with converted XMLs
 * @example
 * const _ = true;
 */

/**
 * Fetch ICAO region for an airport code (F3 airport data services).
 *
 * **Endpoint**: GET /api/v1/translation/airport-region/{icao}
 * @example
 * const _ = true;
 */
export async function fetchAirportRegion(icao: string): Promise<AirportRegionResponse> {
  const code = icao.trim().toUpperCase();
  const response = await withTimeout(
    fetch(apiUrl(`/translation/airport-region/${code}`), {}),
  );

  if (!response.ok) {
    throw new Error(`Airport region lookup failed (${response.status})`);
  }

  return response.json();
}

/**
 * Download file from blob
 *
 * @param blob - File blob to download
 * @param filename - Filename for the download
 * @example
 * const _ = true;
 */

/**
 * Download file from blob
 *
 * @param blob - File blob to download
 * @param filename - Filename for the download
 * @example
 * const _ = true;
 */
export function downloadBlob(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

/**
 * Per-file outcome from ``POST /api/v1/ingest/mass`` (F33).
 * @example
 * const _ = true;
 */

export default {
  checkHealth,
  convertMetarToIwxxm,
  convertMetarToIwxxmZip,
  lintTac,
  validateIwxxm,
  decodeTac,
  fetchLintIssueCatalog,
  fetchRuleCatalog,
  fetchSelectionOptions,
  fetchAirportRegion,
  massIngestFiles,
  downloadBlob,
};

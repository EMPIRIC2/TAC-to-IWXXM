/**
 * Backend API Client
 *
 * Handles all communication with the METAR to IWXXM backend API.
 * All endpoints use the versioned base path: /api/v1/
 */

import { apiUrl, getApiBaseUrl } from './apiBase';
import { DEFAULT_IWXXM_VERSION } from './iwxxmVersions';
import type {
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
  QualityMetricsDetailResponse,
  QualityMetricsListResponse,
  ValidateResponse,
} from './openapiTypes';

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
  QualityMetricsDetailResponse,
  QualityMetricsListResponse,
  ValidateResponse,
};

/**
 * Timeout wrapper for fetch requests
 */
function withTimeout<T>(promise: Promise<T>, timeoutMs: number = 30000): Promise<T> {
  return Promise.race([
    promise,
    new Promise<T>((_, reject) =>
      setTimeout(
        () =>
          reject(
            new Error(
              `Request timeout after ${timeoutMs / 1000}s - Backend may be unreachable`,
            ),
          ),
        timeoutMs,
      ),
    ),
  ]);
}

export interface HealthResponse {
  status: 'healthy' | 'degraded';
  version: string;
  tac2iwxxm_available: boolean;
}

export interface AirportRegionResponse {
  airport_code: string;
  icao_region: string;
}

export interface ApiError {
  message: string;
  errors: string[];
  total_errors?: number;
}

/** Prefer FastAPI string ``detail``, then nested message, then ``message``. */
function apiErrorMessage(
  error: { detail?: unknown; message?: unknown },
  fallback: string,
): string {
  if (typeof error.detail === 'string' && error.detail) {
    return error.detail;
  }
  if (
    error.detail &&
    typeof error.detail === 'object' &&
    'message' in error.detail &&
    typeof (error.detail as { message: unknown }).message === 'string'
  ) {
    return (error.detail as { message: string }).message;
  }
  if (typeof error.message === 'string' && error.message) {
    return error.message;
  }
  return fallback;
}

/**
 * Check backend health status
 *
 * **Endpoint**: GET /health
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
 */
export async function convertMetarToIwxxm(params: {
  manualText?: string;
  files?: File[];
  product?: string;
  profile?: string;
  iwxxmVersion?: string;
  validateOutput?: boolean;
  validationLevel?: string;
  stopOnError?: boolean;
  bulletinId?: string;
  issuingCenter?: string;
  includeNilReasons?: boolean;
  /** Filters conversion/validation/lint issue verbosity (sent when API accepts it). */
  logLevel?: string;
  preview?: boolean;
  accessToken?: string;
  signal?: AbortSignal;
}): Promise<ConversionResponse> {
  const formData = new FormData();

  if (params.manualText?.trim()) {
    formData.append('manual_text', params.manualText.trim());
  }

  if (params.files && params.files.length > 0) {
    params.files.forEach((file) => {
      formData.append('files', file);
    });
  }

  // F6.e — product required by API; default METAR when caller omits (legacy callers)
  formData.append('product', (params.product || 'METAR').toUpperCase());
  formData.append('profile', params.profile || 'annex3');

  // Add IWXXM version (default to 2025-2)
  formData.append('iwxxm_version', params.iwxxmVersion || DEFAULT_IWXXM_VERSION);

  // Add validation flag (default to false)
  formData.append('validate_output', params.validateOutput ? 'true' : 'false');
  formData.append('validation_level', params.validationLevel || 'basic');
  formData.append('stop_on_error', params.stopOnError ? 'true' : 'false');
  formData.append(
    'include_nil_reasons',
    params.includeNilReasons === false ? 'false' : 'true',
  );
  if (params.logLevel) {
    formData.append('log_level', params.logLevel.toUpperCase());
  }

  if (params.bulletinId?.trim()) {
    formData.append('bulletin_id', params.bulletinId.trim().toUpperCase());
  }
  if (params.issuingCenter?.trim()) {
    formData.append('issuing_center', params.issuingCenter.trim().toUpperCase());
  }

  if (params.preview) {
    formData.append('preview', 'true');
  }

  try {
    console.log('[API] Request to:', apiUrl('/convert'));

    const response = await withTimeout(
      fetch(apiUrl('/convert'), {
        method: 'POST',
        body: formData,
        signal: params.signal,
      }),
      30000,
    );

    if (!response.ok) {
      const error = await response.json().catch(() => ({
        message: `Conversion failed: ${response.statusText}`,
        errors: [],
      }));
      throw new Error(
        error.detail?.message || error.message || `HTTP ${response.status}`,
      );
    }

    return await response.json();
  } catch (error) {
    if (error instanceof Error && error.message.includes('timeout')) {
      console.error('[API TIMEOUT]', error.message);
      throw error;
    }
    console.error('[API ERROR]', error);
    throw error;
  }
}

/**
 * Split a WMO AHL bulletin and convert each TAC report.
 *
 * **Endpoint**: POST /api/v1/convert-bulletin
 */
export async function convertBulletin(params: {
  manualText?: string;
  files?: File[];
  product: string;
  profile?: string;
  iwxxmVersion?: string;
  lint?: boolean;
  accessToken?: string;
  signal?: AbortSignal;
}): Promise<ConvertBulletinResponse> {
  const formData = new FormData();
  if (params.manualText?.trim()) {
    formData.append('manual_text', params.manualText.trim());
  }
  if (params.files?.length) {
    params.files.forEach((file) => formData.append('files', file));
  }
  formData.append('product', params.product.toUpperCase());
  formData.append('profile', params.profile || 'annex3');
  formData.append('iwxxm_version', params.iwxxmVersion || DEFAULT_IWXXM_VERSION);
  formData.append('lint', params.lint === false ? 'false' : 'true');

  const response = await withTimeout(
    fetch(apiUrl('/convert-bulletin'), {
      method: 'POST',
      body: formData,
      signal: params.signal,
    }),
    60000,
  );

  if (!response.ok) {
    const error = await response.json().catch(() => ({
      message: `Bulletin conversion failed: ${response.statusText}`,
    }));
    const detail = error.detail;
    const message =
      (typeof detail === 'object' && detail?.message) ||
      detail ||
      error.message ||
      `HTTP ${response.status}`;
    throw new Error(typeof message === 'string' ? message : JSON.stringify(message));
  }

  return (await response.json()) as ConvertBulletinResponse;
}

export class EndpointNotImplementedError extends Error {
  status: number;
  code: string;

  constructor(message: string, status = 501, code = 'not_implemented') {
    super(message);
    this.name = 'EndpointNotImplementedError';
    this.status = status;
    this.code = code;
  }
}

/**
 * Ingest / validate IWXXM COLLECT (or gzipped COLLECT).
 *
 * **Endpoint**: POST /api/v1/ingest-collect (placeholder until implemented).
 */
export async function ingestCollect(params: {
  manualText?: string;
  files?: File[];
  profile?: string;
  iwxxmVersion?: string;
  accessToken?: string;
  signal?: AbortSignal;
}): Promise<{ message: string; status: string }> {
  const formData = new FormData();
  if (params.manualText?.trim()) {
    formData.append('manual_text', params.manualText.trim());
  }
  if (params.files?.length) {
    params.files.forEach((file) => formData.append('files', file));
  }
  formData.append('profile', params.profile || 'annex3');
  formData.append('iwxxm_version', params.iwxxmVersion || DEFAULT_IWXXM_VERSION);

  const response = await withTimeout(
    fetch(apiUrl('/ingest-collect'), {
      method: 'POST',
      body: formData,
      signal: params.signal,
    }),
    30000,
  );

  if (response.status === 501) {
    const body = await response.json().catch(() => ({}));
    throw new EndpointNotImplementedError(
      body?.detail?.message ||
        body?.message ||
        'COLLECT / FTBP ingest is not implemented yet (placeholder).',
      501,
      body?.detail?.code || 'not_implemented',
    );
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({
      message: `COLLECT ingest failed: ${response.statusText}`,
    }));
    throw new Error(
      error.detail?.message || error.message || `HTTP ${response.status}`,
    );
  }

  return (await response.json()) as { message: string; status: string };
}

/**
 * Lint TAC via tac-validate (parse gate + shared rules — not Schematron).
 *
 * **Endpoint**: POST /api/v1/lint-tac
 *
 * @param params.manualText - TAC text
 * @param params.product - Optional product hint
 * @param params.signal - AbortSignal for live workbench cancellation
 * @returns Lint report with optional start/end spans
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
 */
export async function validateIwxxm(params: {
  manualText?: string;
  xmlContent?: string;
  product?: string;
  profile?: string;
  iwxxmVersion?: string;
  layers?: string[];
  stopOnError?: boolean;
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
  formData.append('profile', params.profile || 'annex3');
  formData.append('iwxxm_version', params.iwxxmVersion || DEFAULT_IWXXM_VERSION);
  formData.append('stop_on_error', params.stopOnError === false ? 'false' : 'true');
  const layers = params.layers?.length ? params.layers : ['ALL'];
  for (const layer of layers) {
    formData.append('layers', layer);
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
 * Fetch the tac-validate issue registry catalog (F15 / E11-31).
 *
 * **Endpoint**: GET /api/v1/lint-issue-catalog
 */
export async function fetchLintIssueCatalog(params?: {
  product?: string;
  family?: string;
  issue_type?: string;
  source_access?: string;
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
 * List precomputed official-corpus quality metrics.
 *
 * **Endpoint**: GET /api/v1/quality-metrics
 *
 * @param params.product - Optional product filter (e.g. metar)
 * @returns Summaries and file inventory rows
 */
export async function fetchQualityMetrics(params?: {
  product?: string;
  signal?: AbortSignal;
}): Promise<QualityMetricsListResponse> {
  const qs =
    params?.product && params.product.trim()
      ? `?product=${encodeURIComponent(params.product.trim().toLowerCase())}`
      : '';
  const response = await withTimeout(
    fetch(apiUrl(`/quality-metrics${qs}`), {
      method: 'GET',
      signal: params?.signal,
    }),
    15000,
  );

  if (!response.ok) {
    const error = await response.json().catch(() => ({
      message: `Quality metrics fetch failed: ${response.statusText}`,
    }));
    throw new Error(apiErrorMessage(error, `HTTP ${response.status}`));
  }

  const body = (await response.json()) as QualityMetricsListResponse;
  return {
    generated_at: body.generated_at,
    iwxxm_pin: body.iwxxm_pin,
    summaries: body.summaries ?? [],
    files: body.files ?? [],
  };
}

/**
 * Fetch quality metrics detail for one corpus stem.
 *
 * **Endpoint**: GET /api/v1/quality-metrics/{stem}
 *
 * @param params.stem - Catalog / fixture stem (e.g. metar-A3-1)
 * @returns Per-stem TAC, XML, match, residuals, lint, validate
 */
export async function fetchQualityMetricsDetail(params: {
  stem: string;
  signal?: AbortSignal;
}): Promise<QualityMetricsDetailResponse> {
  const stem = encodeURIComponent(params.stem.trim());
  const response = await withTimeout(
    fetch(apiUrl(`/quality-metrics/${stem}`), {
      method: 'GET',
      signal: params.signal,
    }),
    15000,
  );

  if (!response.ok) {
    const error = await response.json().catch(() => ({
      message: `Quality metrics detail failed: ${response.statusText}`,
    }));
    throw new Error(apiErrorMessage(error, `HTTP ${response.status}`));
  }

  return (await response.json()) as QualityMetricsDetailResponse;
}

/**
 * Decode TAC into ordered Code | Explanation segments.
 *
 * **Endpoint**: POST /api/v1/decode-tac
 *
 * @param params.manualText - TAC text
 * @param params.product - Required F6 product id
 * @returns Ordered segments and residuals
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
 */
export async function convertMetarToIwxxmZip(params: {
  manualText?: string;
  files?: File[];
}): Promise<Blob> {
  const formData = new FormData();

  if (params.manualText?.trim()) {
    formData.append('manual_text', params.manualText.trim());
  }

  if (params.files && params.files.length > 0) {
    params.files.forEach((file) => {
      formData.append('files', file);
    });
  }

  try {
    const response = await fetch(apiUrl('/convert-zip'), {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({
        message: `ZIP conversion failed: ${response.statusText}`,
        errors: [],
      }));
      throw new Error(error.detail?.message || error.message);
    }

    return await response.blob();
  } catch (error) {
    console.error('ZIP conversion error:', error);
    throw error;
  }
}

/**
 * Fetch ICAO region for an airport code (F3 airport data services).
 *
 * **Endpoint**: GET /api/v1/translation/airport-region/{icao}
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

/** Per-file outcome from ``POST /api/v1/ingest/mass`` (F33). */
export interface MassIngestFileResult {
  name: string;
  accepted: boolean;
  reason: string | null;
  size_bytes: number;
  content: string | null;
}

/** Response from ``POST /api/v1/ingest/mass`` (F33 / EV-042). */
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
 */
export async function massIngestFiles(params: {
  files: File[];
  accessToken: string;
  signal?: AbortSignal;
}): Promise<MassIngestResponse> {
  if (!params.accessToken.trim()) {
    throw new Error('Sign in required for mass ingest');
  }
  if (!params.files.length) {
    throw new Error('At least one file is required');
  }

  const formData = new FormData();
  for (const file of params.files) {
    formData.append('files', file, file.name);
  }

  const response = await withTimeout(
    fetch(apiUrl('/ingest/mass'), {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${params.accessToken}`,
      },
      body: formData,
      signal: params.signal,
    }),
    120000,
  );

  if (!response.ok) {
    const error = await response.json().catch(() => ({
      message: `Mass ingest failed: ${response.statusText}`,
    }));
    throw new Error(apiErrorMessage(error, `HTTP ${response.status}`));
  }

  return (await response.json()) as MassIngestResponse;
}

export default {
  checkHealth,
  convertMetarToIwxxm,
  convertMetarToIwxxmZip,
  lintTac,
  validateIwxxm,
  decodeTac,
  fetchLintIssueCatalog,
  fetchQualityMetrics,
  fetchQualityMetricsDetail,
  fetchAirportRegion,
  massIngestFiles,
  downloadBlob,
};

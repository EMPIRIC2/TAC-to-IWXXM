/**
 * Backend API Client
 *
 * Handles all communication with the METAR to IWXXM backend API.
 * All endpoints use the versioned base path: /api/v1/
 */

import { apiUrl, getApiBaseUrl } from './apiBase';

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

export interface ConversionResult {
  name: string;
  content: string;
  source: string;
  size_bytes: number;
  tac_input?: string;
  iwxxm_xml?: string;
  xml?: string;
}

export interface ConversionIssue {
  source: string;
  message: string;
  hint?: string;
  code?: string;
  severity?: 'error' | 'warning' | 'info';
  layer?: string;
  location?: string;
  start?: number;
  end?: number;
}

export interface FailedSpan {
  start: number;
  end: number;
  code?: string;
  message?: string;
}

export interface ConversionResponse {
  results: ConversionResult[];
  errors: string[];
  issues?: ConversionIssue[];
  total_processed: number;
  successful: number;
  failed: number;
  /** Soft-preview envelope (ADR-022); set when preview=true */
  ok?: boolean | null;
  failed_spans?: FailedSpan[];
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

/**
 * Get the access token from local storage
 */
function getAccessToken(): string | null {
  return localStorage.getItem('supabase_access_token');
}

/**
 * Create authorization headers for API requests
 */
function _getAuthHeaders(): HeadersInit {
  const token = getAccessToken();
  return {
    Authorization: token ? `Bearer ${token}` : '',
    'Content-Type': 'application/json',
  };
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
  preview?: boolean;
  accessToken?: string;
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
  formData.append('iwxxm_version', params.iwxxmVersion || '2025-2');

  // Add validation flag (default to false)
  formData.append('validate_output', params.validateOutput ? 'true' : 'false');

  if (params.preview) {
    formData.append('preview', 'true');
  }

  try {
    const token = params.accessToken || getAccessToken() || '';
    console.log(
      '[API] convertMetarToIwxxm called with token:',
      token ? `${token.substring(0, 20)}...` : 'MISSING',
    );
    console.log('[API] Request to:', apiUrl('/convert'));

    const response = await withTimeout(
      fetch(apiUrl('/convert'), {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
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

export interface DecodeSegment {
  start: number;
  end: number;
  code: string;
  explanation: string;
}

export interface DecodeResidual {
  start: number;
  end: number;
  text: string;
}

export interface DecodeTacResponse {
  product: string;
  segments: DecodeSegment[];
  residuals: DecodeResidual[];
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
}): Promise<DecodeTacResponse> {
  const formData = new FormData();
  formData.append('manual_text', params.manualText);
  formData.append('product', params.product.toUpperCase());

  const token = params.accessToken || getAccessToken() || '';
  const response = await withTimeout(
    fetch(apiUrl('/decode-tac'), {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: formData,
    }),
    15000,
  );

  if (!response.ok) {
    const error = await response.json().catch(() => ({
      message: `Decode failed: ${response.statusText}`,
    }));
    throw new Error(
      error.detail?.message || error.message || `HTTP ${response.status}`,
    );
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
      headers: {
        Authorization: `Bearer ${getAccessToken() || ''}`,
      },
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
    fetch(apiUrl(`/translation/airport-region/${code}`), {
      headers: _getAuthHeaders(),
    }),
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

export default {
  checkHealth,
  convertMetarToIwxxm,
  convertMetarToIwxxmZip,
  decodeTac,
  fetchAirportRegion,
  downloadBlob,
};

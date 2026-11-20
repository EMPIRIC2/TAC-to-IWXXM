/* eslint-disable complexity */
/**
 * Convert / bulletin HTTP clients.
 */
import { apiUrl } from './apiBase';
import { isAbortError } from './liveAssist';
import { conversionLibraryIdFromProfile } from './libraryIds';
import type {
  ConversionIssue,
  ConversionResponse,
  ConvertBulletinResponse,
} from '@/models/openapi';
import { ConvertApiError, apiErrorMessage, withTimeout } from './apiErrors';

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
 * convertMetarToIwxxm.
 * @example
 * const _ = true;
 */
export async function convertMetarToIwxxm(params: {
  manualText?: string;
  files?: File[];
  product?: string;
  profile?: string;
  /** Optional saved semantic preset id (requires accessToken). */
  presetId?: string;
  conversionLibraryId?: string;
  tacValidationLibraryId?: string;
  iwxxmValidationLibraryId?: string;
  disseminationLibraryId?: string;
  decodingLibraryId?: string;
  iwxxmVersion?: string;
  strict?: boolean;
  strictLint?: boolean;
  strictConvert?: boolean;
  strictValidate?: boolean;
  validateOutput?: boolean;
  validationLevel?: string;
  stopOnError?: boolean;
  bulletinId?: string;
  issuingCenter?: string;
  includeNilReasons?: boolean;
  /** Filters conversion/validation/lint issue verbosity (sent when API accepts it). */
  logLevel?: string;
  preview?: boolean;
  /** When true, fold decode residuals into remarks/HRT (omit for profile default). */
  propagateResidualsToRemarks?: boolean;
  /** When false, omit national RMK content from IWXXM (default true when omitted). */
  includeNationalRemarks?: boolean;
  extensions?: string[];
  exchangeOutput?: boolean;
  /** Exchange packaging profile (ignored on convert-only; used when packaging). */
  exchangeProfile?: string;
  /** Optional profile-scoped report variant within the selected product family. */
  reportVariant?: string;
  /** Optional signed ConversionProfile overlay id (requires accessToken). */
  overlayId?: string;
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
  // EV-bridge hard cut: Conversion library resolves the engine profile server-side.
  // Do not send semantic_profile / profile / preset / overlay / exchange on Convert.
  if (params.conversionLibraryId?.trim()) {
    formData.append('conversion_library_id', params.conversionLibraryId.trim());
  } else if (params.profile?.trim()) {
    // Transitional FE callers that only know a profile wire id.
    formData.append(
      'conversion_library_id',
      conversionLibraryIdFromProfile(params.profile),
    );
  }
  if (params.tacValidationLibraryId?.trim()) {
    formData.append('tac_validation_library_id', params.tacValidationLibraryId.trim());
  }
  if (params.iwxxmValidationLibraryId?.trim()) {
    formData.append(
      'iwxxm_validation_library_id',
      params.iwxxmValidationLibraryId.trim(),
    );
  }
  if (params.disseminationLibraryId?.trim()) {
    formData.append('dissemination_library_id', params.disseminationLibraryId.trim());
  }
  if (params.decodingLibraryId?.trim()) {
    formData.append('decoding_library_id', params.decodingLibraryId.trim());
  }
  if (params.reportVariant?.trim()) {
    formData.append('report_variant', params.reportVariant.trim().toUpperCase());
  }

  if (params.iwxxmVersion?.trim()) {
    formData.append('iwxxm_version', params.iwxxmVersion.trim());
  }

  // Add validation flag (default to false)
  formData.append('validate_output', params.validateOutput ? 'true' : 'false');
  formData.append('validation_level', params.validationLevel || 'basic');
  if (params.strict !== undefined) {
    formData.append('strict', params.strict ? 'true' : 'false');
  }
  if (params.strictLint !== undefined) {
    formData.append('strict_lint', params.strictLint ? 'true' : 'false');
  }
  if (params.strictConvert !== undefined) {
    formData.append('strict_convert', params.strictConvert ? 'true' : 'false');
  }
  if (params.strictValidate !== undefined) {
    formData.append('strict_validate', params.strictValidate ? 'true' : 'false');
  }
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

  if (params.propagateResidualsToRemarks === true) {
    formData.append('propagate_residuals_to_remarks', 'true');
  } else if (params.propagateResidualsToRemarks === false) {
    formData.append('propagate_residuals_to_remarks', 'false');
  }

  if (params.includeNationalRemarks === true) {
    formData.append('include_national_remarks', 'true');
  } else if (params.includeNationalRemarks === false) {
    formData.append('include_national_remarks', 'false');
  }

  if (params.extensions?.length) {
    for (const token of params.extensions) {
      formData.append('extensions', token);
    }
  }

  if (params.exchangeOutput) {
    formData.append('exchange_output', 'true');
  }

  try {
    console.log('[API] Request to:', apiUrl('/convert'));

    const bearer = params.accessToken?.trim();
    const headers: HeadersInit | undefined = bearer
      ? { Authorization: `Bearer ${bearer}` }
      : undefined;

    const response = await withTimeout(
      fetch(apiUrl('/convert'), {
        method: 'POST',
        body: formData,
        headers,
        signal: params.signal,
      }),
      30000,
    );

    if (!response.ok) {
      const error = await response.json().catch(() => ({
        message: `Conversion failed: ${response.statusText}`,
        errors: [],
      }));
      const detail =
        error.detail && typeof error.detail === 'object'
          ? (error.detail as Record<string, unknown>)
          : null;
      const errors = Array.isArray(detail?.errors)
        ? detail.errors.filter((item): item is string => typeof item === 'string')
        : Array.isArray(error.errors)
          ? error.errors.filter(
              (item: unknown): item is string => typeof item === 'string',
            )
          : [];
      const issues = Array.isArray(detail?.issues)
        ? (detail.issues as ConversionIssue[])
        : Array.isArray(error.issues)
          ? (error.issues as ConversionIssue[])
          : [];
      throw new ConvertApiError(apiErrorMessage(error, `HTTP ${response.status}`), {
        status: response.status,
        errors,
        issues,
      });
    }

    return await response.json();
  } catch (error) {
    if (isAbortError(error)) {
      throw error;
    }
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
 * @example
 * const _ = true;
 */

/**
 * Split a WMO AHL bulletin and convert each TAC report.
 *
 * **Endpoint**: POST /api/v1/convert-bulletin
 * @example
 * const _ = true;
 */
/**
 * convertBulletin.
 * @example
 * const _ = true;
 */
export async function convertBulletin(params: {
  manualText?: string;
  files?: File[];
  product: string;
  profile?: string;
  /** Conversion library asset id (preferred over profile after EV-bridge). */
  conversionLibraryId?: string;
  /** Dissemination library asset id (transforms on Convert & Send / bulletin). */
  disseminationLibraryId?: string;
  /**
   * Legacy exchange overlay. Ignored on convert-bulletin after EV-bridge hard cut
   * (use disseminationLibraryId). Kept on the params type for transitional callers.
   */
  exchangeProfile?: string;
  iwxxmVersion?: string;
  lint?: boolean;
  /** When true, fold decode residuals into remarks/HRT (omit for profile default). */
  propagateResidualsToRemarks?: boolean;
  /** When false, omit national RMK content from IWXXM (default true when omitted). */
  includeNationalRemarks?: boolean;
  /** National extension tokens (for example IWXXM_CA). */
  extensions?: string[];
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
  if (params.conversionLibraryId?.trim()) {
    formData.append('conversion_library_id', params.conversionLibraryId.trim());
  } else if (params.profile?.trim()) {
    formData.append(
      'conversion_library_id',
      conversionLibraryIdFromProfile(params.profile),
    );
  }
  if (params.disseminationLibraryId?.trim()) {
    formData.append('dissemination_library_id', params.disseminationLibraryId.trim());
  }
  // EV-bridge hard cut: omit exchange_profile (Dissemination library owns packaging).
  if (params.iwxxmVersion?.trim()) {
    formData.append('iwxxm_version', params.iwxxmVersion.trim());
  }
  formData.append('lint', params.lint === false ? 'false' : 'true');
  if (params.propagateResidualsToRemarks === true) {
    formData.append('propagate_residuals_to_remarks', 'true');
  } else if (params.propagateResidualsToRemarks === false) {
    formData.append('propagate_residuals_to_remarks', 'false');
  }

  if (params.includeNationalRemarks === true) {
    formData.append('include_national_remarks', 'true');
  } else if (params.includeNationalRemarks === false) {
    formData.append('include_national_remarks', 'false');
  }
  if (params.extensions?.length) {
    for (const token of params.extensions) {
      if (token.trim()) {
        formData.append('extensions', token.trim());
      }
    }
  }
  const bearer = params.accessToken?.trim();
  const headers: HeadersInit | undefined = bearer
    ? { Authorization: `Bearer ${bearer}` }
    : undefined;
  const response = await withTimeout(
    fetch(apiUrl('/convert-bulletin'), {
      method: 'POST',
      body: formData,
      headers,
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

/**
 * Thrown when the backend returns HTTP 501 for a not-yet-implemented route.
 * @example
 * const _ = true;
 */

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
 * convertMetarToIwxxmZip.
 * @example
 * const _ = true;
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
 * @example
 * const _ = true;
 */

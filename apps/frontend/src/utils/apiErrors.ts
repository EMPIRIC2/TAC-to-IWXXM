/**
 * API error types and fetch helpers shared by client modules.
 */
import type { ConversionIssue } from '@/models/openapi';

/**
 * Timeout wrapper for fetch requests
 */
/**
 * withTimeout.
 * @example
 * const _ = true;
 */
export function withTimeout<T>(
  promise: Promise<T>,
  timeoutMs: number = 30000,
): Promise<T> {
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

/**
 * Type `HealthResponse`.
 * @example
 * const _ = true;
 */

/**
 * Structured hard-convert failure surfaced by the backend.
 *
 * Preserves ``detail.errors`` / ``detail.issues`` from non-2xx convert responses so
 * the workbench can render the same operator-facing log panel it uses for 200 responses
 * with partial or failed conversion details.
 * @example
 * const _ = true;
 */
export class ConvertApiError extends Error {
  status: number;
  errors: string[];
  issues: ConversionIssue[];

  constructor(
    message: string,
    {
      status,
      errors = [],
      issues = [],
    }: {
      status: number;
      errors?: string[];
      issues?: ConversionIssue[];
    },
  ) {
    super(message);
    this.name = 'ConvertApiError';
    this.status = status;
    this.errors = errors;
    this.issues = issues;
  }
}

/** Prefer FastAPI string ``detail``, then nested message, then ``message``. */

/**
 * apiErrorMessage.
 * @example
 * const _ = true;
 */
export function apiErrorMessage(
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
 * @example
 * const _ = true;
 */

/**
 * Thrown when the backend returns HTTP 501 for a not-yet-implemented route.
 * @example
 * const _ = true;
 */
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
 * @example
 * const _ = true;
 */

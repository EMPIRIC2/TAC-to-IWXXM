/**
 * Map FileConverter conversion parameters onto `/api/v1/convert` multipart fields
 * and client-side conversion/validation/lint log filtering (ADR-023 / ADR-024).
 * @example
 * const _ = true;
 */

export type ConvertOnError = 'skip' | 'fail' | 'warn';
/**
 * Type `ConvertLogLevel`.
 * @example
 * const _ = true;
 */
export type ConvertLogLevel = 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL';
/**
 * Type `ConsoleLineLevel`.
 * @example
 * const _ = true;
 */
export type ConsoleLineLevel = 'info' | 'warn' | 'error';
/**
 * Type `IssueSeverity`.
 * @example
 * const _ = true;
 */
export type IssueSeverity = 'error' | 'warning' | 'info' | string;

/**
 * Type `ConvertValidationFlags`.
 * @example
 * const _ = true;
 */
export interface ConvertValidationFlags {
  validateOutput: boolean;
  validationLevel: 'basic' | 'comprehensive';
}

/**
 * Soft-preview never runs post-convert Schematron/XSD; hard convert honors Strict Validation.
 *
 * @param strict - UI "Strict Validation" checkbox
 * @param softPreview - Soft-preview / preview=true mode
 * @example
 * const _ = true;
 */
export function mapStrictToValidation(
  strict: boolean,
  softPreview: boolean,
): ConvertValidationFlags {
  if (softPreview) {
    return { validateOutput: false, validationLevel: 'basic' };
  }
  return {
    validateOutput: strict,
    validationLevel: strict ? 'comprehensive' : 'basic',
  };
}

/**
 * Map On Error Behavior to API ``stop_on_error``.
 *
 * @param onError - UI select value
 * @example
 * const _ = true;
 */
export function mapOnErrorToStopOnError(onError: ConvertOnError): boolean {
  return onError === 'fail';
}

const LINE_RANK: Record<ConsoleLineLevel, number> = {
  info: 1,
  warn: 2,
  error: 3,
};

const MIN_RANK: Record<ConvertLogLevel, number> = {
  DEBUG: 0,
  INFO: 1,
  WARNING: 2,
  ERROR: 3,
  CRITICAL: 3,
};

/**
 * Whether a workbench console line should show given the operator log-level select.
 *
 * Filters conversion / validation / lint process messages (not server env ``LOG_LEVEL``).
 *
 * @param lineLevel - Console line severity
 * @param minLevel - Operator Log Level preference
 * @example
 * const _ = true;
 */
export function consoleLevelPasses(
  lineLevel: ConsoleLineLevel,
  minLevel: ConvertLogLevel,
): boolean {
  return LINE_RANK[lineLevel] >= MIN_RANK[minLevel];
}

/**
 * Map issue severity string onto console ranks.
 *
 * @param severity - Issue severity from convert/lint/validate
 * @example
 * const _ = true;
 */
export function issueSeverityRank(severity: IssueSeverity | undefined): number {
  const s = (severity ?? 'error').toLowerCase();
  if (s === 'debug') {
    return 0;
  }
  if (s === 'info' || s === 'information') {
    return 1;
  }
  if (s === 'warn' || s === 'warning') {
    return 2;
  }
  return 3;
}

/**
 * Whether a conversion/validation/lint issue should appear for the operator log level.
 *
 * @param severity - Issue severity
 * @param minLevel - Operator Log Level (filters process log for input/output)
 * @example
 * const _ = true;
 */
export function issueLevelPasses(
  severity: IssueSeverity | undefined,
  minLevel: ConvertLogLevel,
): boolean {
  return issueSeverityRank(severity) >= MIN_RANK[minLevel];
}

const BULLETIN_ID_RE = /^[A-Z]{4}[0-9]{2}$/;
const ISSUING_CENTER_RE = /^[A-Z]{4}$/;

/**
 * True when Bulletin ID is empty or 4 letters + 2 digits.
 * @example
 * const _ = true;
 */
export function isValidBulletinId(value: string): boolean {
  const raw = value.trim().toUpperCase();
  return raw === '' || BULLETIN_ID_RE.test(raw);
}

/**
 * True when Issuing Center is empty or exactly 4 letters (CCCC).
 * @example
 * const _ = true;
 */
export function isValidIssuingCenter(value: string): boolean {
  const raw = value.trim().toUpperCase();
  return raw === '' || ISSUING_CENTER_RE.test(raw);
}

/**
 * Strict raise policy for workbench issue chrome (ADR-054).
 *
 * Server returns all issues; the client raises attention chrome only for the
 * raised severity set. Strict OFF → critical + error. Strict ON → full ladder.
 */

export type StrictSeverity = 'critical' | 'error' | 'warning' | 'info';

export interface StrictRaiseSteps {
  lint: boolean;
  convert: boolean;
  validate: boolean;
}

const OFF_SET = new Set<string>(['critical', 'error']);
const ON_SET = new Set<string>([
  'critical',
  'error',
  'warning',
  'warn',
  'info',
  'note',
]);

/**
 * Severities considered raised for the current Strict settings.
 *
 * @param strict - Master Strict checkbox
 * @param steps - Optional step flags (ignored when Strict is off)
 * @returns Set of normalized severity tokens
 * @example
 * const _ = true;
 */
export function raisedSeveritySet(
  strict: boolean,
  steps: StrictRaiseSteps = { lint: true, convert: true, validate: true },
): Set<string> {
  if (!strict) {
    return new Set(OFF_SET);
  }
  if (!(steps.lint || steps.convert || steps.validate)) {
    return new Set(OFF_SET);
  }
  return new Set(ON_SET);
}

/**
 * Whether an issue severity should use raised (attention) chrome.
 *
 * @param severity - Issue severity from convert/lint/validate
 * @param strict - Master Strict checkbox
 * @param steps - Optional step flags
 * @returns True when the issue is raised
 * @example
 * const _ = true;
 */
export function isSeverityRaised(
  severity: string | null | undefined,
  strict: boolean,
  steps?: StrictRaiseSteps,
): boolean {
  const token = (severity ?? 'error').trim().toLowerCase();
  const raised = raisedSeveritySet(strict, steps);
  if (raised.has(token)) {
    return true;
  }
  // Missing severity treated as error (raised when Strict off or on).
  if (!severity || !severity.trim()) {
    return raised.has('error');
  }
  return false;
}

/**
 * Convert failures (critical) block publish/download. IWXXM validation errors do not.
 *
 * @param severity - Issue severity
 * @returns True when this severity alone blocks download
 * @example
 * const _ = true;
 */
export function severityBlocksDownload(severity: string | null | undefined): boolean {
  return (severity ?? '').trim().toLowerCase() === 'critical';
}

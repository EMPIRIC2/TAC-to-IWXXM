/**
 * Ordered Convert checks: TAC lint, then XML schema, then Schematron.
 */

/**
 * Type `LayerRunStatus`.
 * @example
 * const _ = true;
 */
export type LayerRunStatus = 'not run' | 'passed' | 'failed';

/**
 * Type `TacLintLayerStatus`.
 * @example
 * const _ = true;
 */
export type TacLintLayerStatus =
  | 'waiting'
  | 'running'
  | 'passed'
  | 'failed'
  | 'warnings';

/**
 * Type `LayerIssue`.
 * @example
 * const _ = true;
 */
export interface LayerIssue {
  layer?: string | null;
  severity?: string | null;
}

const SCHEMA_KEYS = new Set(['xmlschema', 'schema']);
const SCHEMATRON_KEYS = new Set(['schematron']);

/**
 * Fold a layer id to letters only.
 *
 * @param value - Engine layer id
 * @returns Lowercase letters
 * @example
 * const _ = true;
 */
export function layerKey(value: string): string {
  return value
    .trim()
    .toLowerCase()
    .replace(/[^a-z]/g, '');
}

/**
 * Whether a strict convert finished without an error status.
 *
 * @param opts.strict - Strict validation is on
 * @param opts.softPreview - Soft-preview is on
 * @param opts.convertedCount - Successful convert results kept
 * @param opts.status - Convert status type
 * @returns True when schema and Schematron were part of that convert
 * @example
 * const _ = true;
 */
export function strictConvertRan(opts: {
  strict: boolean;
  softPreview: boolean;
  convertedCount: number;
  status: string;
}): boolean {
  if (!opts.strict || opts.softPreview) return false;
  if (opts.convertedCount <= 0) return false;
  return opts.status !== 'error';
}

/**
 * Error-severity layer ids from a conversion log.
 *
 * @param log - Conversion log, or null when there is no log
 * @returns Layer ids that failed
 * @example
 * const _ = true;
 */
export function errorLayerNames(
  log: { issues?: readonly LayerIssue[] | null } | null,
): string[] {
  const names: string[] = [];
  for (const issue of log?.issues ?? []) {
    if (!issue.layer) continue;
    if (issue.severity && issue.severity !== 'error') continue;
    names.push(issue.layer);
  }
  return names;
}

/**
 * Passed, failed, or not run for schema or Schematron.
 *
 * @param kind - Which publish check
 * @param report - Last validate result, or null
 * @param issueLayers - Error layers the engine already returned
 * @returns Layer status word
 * @example
 * const _ = true;
 */
export function outputLayerStatus(
  kind: 'schema' | 'schematron',
  report: {
    layers_passed?: readonly string[] | null;
    layers_failed?: readonly string[] | null;
  } | null,
  issueLayers: readonly string[],
): LayerRunStatus {
  const keys = kind === 'schema' ? SCHEMA_KEYS : SCHEMATRON_KEYS;
  const hit = (values: readonly string[] | null | undefined) =>
    (values ?? []).some((value) => keys.has(layerKey(value)));
  if (hit(report?.layers_failed) || hit(issueLayers)) return 'failed';
  if (hit(report?.layers_passed)) return 'passed';
  return 'not run';
}

/**
 * Count lint issues and how many are errors.
 *
 * @param issues - Live lint issues
 * @returns Error count and total count
 * @example
 * const _ = true;
 */
export function lintIssueCounts(issues: readonly { severity?: string | null }[]): {
  errorCount: number;
  issueCount: number;
} {
  let errorCount = 0;
  for (const issue of issues) {
    if (issue.severity === 'error') errorCount += 1;
  }
  return { errorCount, issueCount: issues.length };
}

/**
 * Live TAC lint status for the ordered check list.
 *
 * @param opts.hasTac - Editor has text
 * @param opts.loading - Lint request is in flight
 * @param opts.errorCount - Error-severity issues
 * @param opts.issueCount - All current issues
 * @returns Status word
 * @example
 * const _ = true;
 */
export function tacLintLayerStatus(opts: {
  hasTac: boolean;
  loading: boolean;
  errorCount: number;
  issueCount: number;
}): TacLintLayerStatus {
  if (!opts.hasTac) return 'waiting';
  if (opts.errorCount > 0) return 'failed';
  if (opts.issueCount > 0) return 'warnings';
  if (opts.loading) return 'running';
  return 'passed';
}

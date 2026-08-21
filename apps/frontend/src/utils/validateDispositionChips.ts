/**
 * Derive Quality metrics validate disposition chips (EV-055 AC6).
 *
 * Soft-skip codes must not present as success. Plain-language operator copy only
 * (no internal planning ids — EV-048).
 */

/** Soft Schematron skip code from the validate engine. */
export const VALIDATE_CODE_SCHEMATRON_SKIPPED = 'SCHEMATRON_SKIPPED';

/** Soft schema-import warning code from the validate engine. */
export const VALIDATE_CODE_SCHEMA_IMPORT_WARNING = 'SCHEMA_IMPORT_WARNING';

export const QUALITY_METRICS_SCHEMATRON_EVALUATED = 'Schematron rules: checked';
export const QUALITY_METRICS_SCHEMATRON_SKIPPED = 'Schematron rules: skipped';
export const QUALITY_METRICS_SCHEMA_IMPORT_RESOLVED = 'XML schema imports: OK';
export const QUALITY_METRICS_SCHEMA_IMPORT_WARNING = 'XML schema imports: unresolved';

export type ValidateDispositionChip = {
  /** Stable test id suffix. */
  id: 'schematron' | 'schema-import';
  /** Operator-visible label. */
  label: string;
  /** True when disposition is healthy for this cycle. */
  ok: boolean;
};

function issueCodes(issues: Record<string, unknown>[]): Set<string> {
  const codes = new Set<string>();
  for (const issue of issues) {
    if (typeof issue.code === 'string' && issue.code.trim()) {
      codes.add(issue.code.trim());
    }
  }
  return codes;
}

/**
 * Build Schematron + schema-import disposition chips from validate issues.
 *
 * @param validateIssues - Detail `validate_issues` rows
 * @returns Two chips (schematron, schema-import)
 */
export function validateDispositionChips(
  validateIssues: Record<string, unknown>[],
): ValidateDispositionChip[] {
  const codes = issueCodes(validateIssues);
  const schematronSkipped = codes.has(VALIDATE_CODE_SCHEMATRON_SKIPPED);
  const schemaImportWarning = codes.has(VALIDATE_CODE_SCHEMA_IMPORT_WARNING);

  return [
    {
      id: 'schematron',
      label: schematronSkipped
        ? QUALITY_METRICS_SCHEMATRON_SKIPPED
        : QUALITY_METRICS_SCHEMATRON_EVALUATED,
      ok: !schematronSkipped,
    },
    {
      id: 'schema-import',
      label: schemaImportWarning
        ? QUALITY_METRICS_SCHEMA_IMPORT_WARNING
        : QUALITY_METRICS_SCHEMA_IMPORT_RESOLVED,
      ok: !schemaImportWarning,
    },
  ];
}

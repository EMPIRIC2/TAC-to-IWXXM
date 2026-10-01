/**
 * Display F2 validate results for validate-only IWXXM mode (F7.s / #838).
 */
import { outputLayerStatus, type LayerRunStatus } from '/utils/checkLayers';
import type { ValidateResponse } from '/utils/openapiTypes';
import { DecodePanel } from './DecodePanel';

/** Plain result for XML schema or Schematron. */
function layerPhrase(name: string, status: LayerRunStatus): string {
  if (status === 'passed') return `${name}: passed`;
  if (status === 'failed') return `${name}: failed`;
  return `${name}: not run`;
}

type ValidateIwxxmReportProps = {
  report: ValidateResponse;
};

/**
 * Structured pass/fail panel for POST /api/v1/validate responses.
 *
 * @param props.report - ValidateResponse from the API
 * @example
 * const _ = true;
 */
export function ValidateIwxxmReport({ report }: ValidateIwxxmReportProps) {
  const failed = report.layers_failed ?? [];
  const passed = report.layers_passed ?? [];
  const schema = outputLayerStatus('schema', report, []);
  const schematron = outputLayerStatus('schematron', report, []);
  const issues = report.package_issues ?? report.issues ?? [];
  const segments = report.segments ?? [];
  const summary = report.summary ?? '';

  return (
    <div
      className="rounded-md border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-900"
      data-testid="validate-iwxxm-report"
      role="region"
      aria-label="IWXXM validation results"
    >
      <p
        className={`text-sm font-semibold ${
          report.is_valid
            ? 'text-green-700 dark:text-green-400'
            : 'text-red-700 dark:text-red-400'
        }`}
        data-testid="validate-iwxxm-status"
      >
        {report.is_valid ? 'Valid' : 'Invalid'} — IWXXM {report.version}
      </p>
      <ul className="mt-2 space-y-1 text-sm" aria-label="Schema and Schematron">
        <li data-testid="validate-iwxxm-schema">{layerPhrase('XML schema', schema)}</li>
        <li data-testid="validate-iwxxm-schematron">
          {layerPhrase('Schematron', schematron)}
        </li>
      </ul>
      {passed.length > 0 && (
        <p className="mt-2 text-xs text-gray-600 dark:text-gray-400">
          Passed: {passed.join(', ')}
        </p>
      )}
      {failed.length > 0 && (
        <p
          className="mt-1 text-xs text-red-700 dark:text-red-400"
          data-testid="validate-iwxxm-failed-layers"
        >
          Failed: {failed.join(', ')}
        </p>
      )}
      {issues.length > 0 ? (
        <ul
          className="mt-3 max-h-48 list-disc space-y-1 overflow-y-auto pl-5 text-sm text-gray-800 dark:text-gray-200"
          data-testid="validate-iwxxm-issues"
        >
          {issues.map((issue, index) => {
            const message =
              typeof issue === 'object' && issue !== null && 'message' in issue
                ? String((issue as { message?: string }).message ?? 'Issue')
                : String(issue);
            const code =
              typeof issue === 'object' && issue !== null && 'code' in issue
                ? String((issue as { code?: string }).code ?? '')
                : '';
            return (
              <li key={`${code}-${index}`}>
                {code ? <span className="font-mono text-xs">{code}: </span> : null}
                {message}
              </li>
            );
          })}
        </ul>
      ) : (
        <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">
          No package issues reported.
        </p>
      )}
      {segments.length > 0 || summary.trim() ? (
        <DecodePanel
          segments={segments}
          residuals={[]}
          summary={summary}
          product="IWXXM"
          defaultOpen
        />
      ) : null}
    </div>
  );
}

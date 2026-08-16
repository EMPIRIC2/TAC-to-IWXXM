/**
 * Display F2 validate results for validate-only IWXXM mode (F7.s / #838).
 */
import type { ValidateResponse } from '/utils/openapiTypes';

type ValidateIwxxmReportProps = {
  report: ValidateResponse;
};

/**
 * Structured pass/fail panel for POST /api/v1/validate responses.
 *
 * @param props.report - ValidateResponse from the API
 */
export function ValidateIwxxmReport({ report }: ValidateIwxxmReportProps) {
  const failed = report.layers_failed ?? [];
  const passed = report.layers_passed ?? [];
  const issues = report.package_issues ?? report.issues ?? [];

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
    </div>
  );
}

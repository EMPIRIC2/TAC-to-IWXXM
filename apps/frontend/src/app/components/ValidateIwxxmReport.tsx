/**
 * Display F2 validate results for validate-only IWXXM mode (F7.s / #838).
 */
import { useState } from 'react';
import { outputLayerStatus, type LayerRunStatus } from '/utils/checkLayers';
import type { LintIssueCatalogEntry } from '@/utils/api';
import { IssueDetailDialog } from '@/app/components/IssueDetailDialog';
import { buildIssueDetail, type IssueDetailModel } from '@/utils/issueDetail';
import { ISSUE_DETAIL_OPEN } from '@/utils/issueDetailCopy';
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
  /** Loaded rules catalog, keyed by code. */
  catalogByCode?: Map<string, LintIssueCatalogEntry>;
};

/**
 * Structured pass/fail panel for POST /api/v1/validate responses.
 *
 * @param props.report - ValidateResponse from the API
 * @example
 * const _ = true;
 */
export function ValidateIwxxmReport({
  report,
  catalogByCode,
}: ValidateIwxxmReportProps) {
  const [detail, setDetail] = useState<IssueDetailModel | null>(null);
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
            const record =
              typeof issue === 'object' && issue !== null
                ? (issue as Record<string, unknown>)
                : null;
            const hint = record && typeof record.hint === 'string' ? record.hint : null;
            const location =
              record && typeof record.location === 'string' ? record.location : null;
            const start =
              record && typeof record.start === 'number' ? record.start : null;
            const end = record && typeof record.end === 'number' ? record.end : null;
            const severity =
              record && typeof record.severity === 'string' ? record.severity : null;
            return (
              <li key={`${code}-${index}`}>
                <button
                  type="button"
                  className="text-left"
                  data-testid={`issue-detail-open-${index}`}
                  aria-label={ISSUE_DETAIL_OPEN}
                  onClick={() =>
                    setDetail(
                      buildIssueDetail({
                        code: code || null,
                        severity,
                        message,
                        hint,
                        location,
                        start,
                        end,
                        catalog: code ? catalogByCode?.get(code) : null,
                      }),
                    )
                  }
                >
                  {code ? <span className="font-mono text-xs">{code}: </span> : null}
                  {message}
                </button>
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
      <IssueDetailDialog detail={detail} onClose={() => setDetail(null)} />
    </div>
  );
}

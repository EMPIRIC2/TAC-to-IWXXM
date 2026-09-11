import { useMemo, useState } from 'react';
import { ChevronDown, ChevronUp, AlertCircle } from 'lucide-react';
import type { ConversionIssue } from '/utils/api';
import {
  issueLevelPasses,
  issueSeverityRank,
  type ConvertLogLevel,
} from '/utils/convertParams';

export interface ConversionLog {
  errors: string[];
  issues: ConversionIssue[];
}

interface ErrorLogPanelProps {
  log: ConversionLog;
  /** Operator log level — filters conversion/validation/lint issues. */
  minLogLevel?: ConvertLogLevel;
}

/** Internal codes that must not appear in the operator Conversion/Validation log. */
const HIDDEN_OPERATOR_ISSUE_CODES = new Set(['DEPRECATED_PROFILE_ALIAS']);

/**
 * Collapsible panel showing conversion errors and filtered validation issues.
 *
 * Respects the operator minimum log level when rendering issues. Info-only
 * content uses neutral chrome (not amber/red).
 */
export function ErrorLogPanel({ log, minLogLevel = 'INFO' }: ErrorLogPanelProps) {
  const [expanded, setExpanded] = useState(true);
  const visibleErrors = log.errors;
  const suppressedByCode = log.issues.filter((issue) =>
    HIDDEN_OPERATOR_ISSUE_CODES.has(String(issue.code ?? '')),
  );
  const levelHiddenIssues = log.issues.filter(
    (issue) =>
      !HIDDEN_OPERATOR_ISSUE_CODES.has(String(issue.code ?? '')) &&
      !issueLevelPasses(issue.severity, minLogLevel),
  );
  const filteredIssues = log.issues.filter(
    (issue) =>
      !HIDDEN_OPERATOR_ISSUE_CODES.has(String(issue.code ?? '')) &&
      issueLevelPasses(issue.severity, minLogLevel),
  );
  const totalCount = visibleErrors.length + filteredIssues.length;
  const levelHiddenCount = levelHiddenIssues.length;
  const hiddenCount = suppressedByCode.length + levelHiddenCount;

  const tone = useMemo(() => {
    if (visibleErrors.length > 0) {
      return 'alert' as const;
    }
    const maxRank = filteredIssues.reduce(
      (acc, issue) => Math.max(acc, issueSeverityRank(issue.severity)),
      0,
    );
    if (maxRank >= 2) {
      return 'alert' as const;
    }
    return 'neutral' as const;
  }, [visibleErrors.length, filteredIssues]);

  if (log.errors.length + log.issues.length === 0) {
    return null;
  }

  // Still hide the panel when everything was filtered (e.g. only deprecated infos).
  if (totalCount === 0 && hiddenCount === log.errors.length + log.issues.length) {
    const onlyHiddenCodes =
      log.errors.length === 0 &&
      log.issues.length > 0 &&
      log.issues.every((issue) =>
        HIDDEN_OPERATOR_ISSUE_CODES.has(String(issue.code ?? '')),
      );
    if (onlyHiddenCodes) {
      return null;
    }
  }

  const shell =
    tone === 'alert'
      ? 'mb-8 rounded-lg border-2 border-amber-300 bg-amber-50 dark:border-amber-700 dark:bg-amber-900/20'
      : 'mb-8 rounded-lg border border-gray-200 bg-transparent dark:border-gray-700';
  const titleClass =
    tone === 'alert'
      ? 'flex items-center gap-2 font-semibold text-amber-900 dark:text-amber-100'
      : 'flex items-center gap-2 font-semibold text-gray-800 dark:text-gray-100';
  const bodyBorder =
    tone === 'alert'
      ? 'space-y-4 border-t border-amber-200 px-4 pb-4 pt-3 dark:border-amber-800'
      : 'space-y-4 border-t border-gray-200 px-4 pb-4 pt-3 dark:border-gray-700';
  const headingClass =
    tone === 'alert'
      ? 'mb-2 text-sm font-semibold text-amber-900 dark:text-amber-100'
      : 'mb-2 text-sm font-semibold text-gray-800 dark:text-gray-100';
  const textClass =
    tone === 'alert'
      ? 'text-sm text-amber-950 dark:text-amber-50'
      : 'text-sm text-gray-800 dark:text-gray-100';
  const issueCard =
    tone === 'alert'
      ? 'rounded border border-amber-200 bg-white/60 p-2 dark:border-amber-800 dark:bg-black/20'
      : 'rounded border border-gray-200 bg-transparent p-2 dark:border-gray-700';
  const hintClass =
    tone === 'alert'
      ? 'mt-1 text-amber-800 dark:text-amber-200'
      : 'mt-1 text-gray-600 dark:text-gray-300';
  const codeClass =
    tone === 'alert'
      ? 'mt-1 text-xs text-amber-700 dark:text-amber-300'
      : 'mt-1 text-xs text-gray-500 dark:text-gray-400';

  return (
    <section
      className={shell}
      aria-label="Conversion error log"
      data-testid="conversion-error-log"
      data-tone={tone}
    >
      <button
        type="button"
        className="flex w-full items-center justify-between gap-3 p-4 text-left"
        onClick={() => setExpanded((prev) => !prev)}
        aria-expanded={expanded}
        aria-controls="conversion-error-log-content"
      >
        <span className={titleClass}>
          <AlertCircle className="h-5 w-5 flex-shrink-0" aria-hidden="true" />
          Conversion / validation log ({totalCount}
          {levelHiddenCount > 0 ? ` · ${levelHiddenCount} hidden by log level` : ''})
        </span>
        {expanded ? (
          <ChevronUp className="h-5 w-5" aria-hidden="true" />
        ) : (
          <ChevronDown className="h-5 w-5" aria-hidden="true" />
        )}
      </button>
      {expanded && (
        <div id="conversion-error-log-content" className={bodyBorder}>
          {totalCount === 0 ? (
            <p className={textClass}>
              No messages at {minLogLevel} or above. Lower Log Level to see
              info/warnings.
            </p>
          ) : null}
          {visibleErrors.length > 0 && (
            <div>
              <h3 className={headingClass}>Errors</h3>
              <ul className={`list-disc space-y-1 pl-5 ${textClass}`}>
                {visibleErrors.map((error, index) => (
                  <li key={`error-${index}`}>{error}</li>
                ))}
              </ul>
            </div>
          )}
          {filteredIssues.length > 0 && (
            <div>
              <h3 className={headingClass}>Issues</h3>
              <ul className={`space-y-2 ${textClass}`}>
                {filteredIssues.map((issue, index) => (
                  <li key={`issue-${index}`} className={issueCard}>
                    <p className="font-medium">
                      [{issue.severity ?? 'error'}] {issue.source}: {issue.message}
                    </p>
                    {issue.hint && <p className={hintClass}>{issue.hint}</p>}
                    {issue.code && <p className={codeClass}>Code: {issue.code}</p>}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </section>
  );
}

import { useState } from 'react';
import { ChevronDown, ChevronUp, AlertCircle } from 'lucide-react';
import type { ConversionIssue } from '/utils/api';
import { issueLevelPasses, type ConvertLogLevel } from '/utils/convertParams';

export interface ConversionLog {
  errors: string[];
  issues: ConversionIssue[];
}

interface ErrorLogPanelProps {
  log: ConversionLog;
  /** Operator log level — filters conversion/validation/lint issues. */
  minLogLevel?: ConvertLogLevel;
}

export function ErrorLogPanel({ log, minLogLevel = 'INFO' }: ErrorLogPanelProps) {
  const [expanded, setExpanded] = useState(true);
  const showErrors = issueLevelPasses('error', minLogLevel);
  const filteredIssues = log.issues.filter((issue) =>
    issueLevelPasses(issue.severity, minLogLevel),
  );
  const visibleErrors = showErrors ? log.errors : [];
  const totalCount = visibleErrors.length + filteredIssues.length;
  const hiddenCount = log.errors.length + log.issues.length - totalCount;

  if (log.errors.length + log.issues.length === 0) {
    return null;
  }

  return (
    <section
      className="mb-8 rounded-lg border-2 border-amber-300 bg-amber-50 dark:border-amber-700 dark:bg-amber-900/20"
      aria-label="Conversion error log"
      data-testid="conversion-error-log"
    >
      <button
        type="button"
        className="flex w-full items-center justify-between gap-3 p-4 text-left"
        onClick={() => setExpanded((prev) => !prev)}
        aria-expanded={expanded}
        aria-controls="conversion-error-log-content"
      >
        <span className="flex items-center gap-2 font-semibold text-amber-900 dark:text-amber-100">
          <AlertCircle className="h-5 w-5 flex-shrink-0" aria-hidden="true" />
          Conversion / validation log ({totalCount}
          {hiddenCount > 0 ? ` · ${hiddenCount} hidden by log level` : ''})
        </span>
        {expanded ? (
          <ChevronUp className="h-5 w-5" aria-hidden="true" />
        ) : (
          <ChevronDown className="h-5 w-5" aria-hidden="true" />
        )}
      </button>
      {expanded && (
        <div
          id="conversion-error-log-content"
          className="space-y-4 border-t border-amber-200 px-4 pb-4 pt-3 dark:border-amber-800"
        >
          {totalCount === 0 ? (
            <p className="text-sm text-amber-900 dark:text-amber-100">
              No messages at {minLogLevel} or above. Lower Log Level to see
              info/warnings.
            </p>
          ) : null}
          {visibleErrors.length > 0 && (
            <div>
              <h3 className="mb-2 text-sm font-semibold text-amber-900 dark:text-amber-100">
                Errors
              </h3>
              <ul className="list-disc space-y-1 pl-5 text-sm text-amber-950 dark:text-amber-50">
                {visibleErrors.map((error, index) => (
                  <li key={`error-${index}`}>{error}</li>
                ))}
              </ul>
            </div>
          )}
          {filteredIssues.length > 0 && (
            <div>
              <h3 className="mb-2 text-sm font-semibold text-amber-900 dark:text-amber-100">
                Issues
              </h3>
              <ul className="space-y-2 text-sm text-amber-950 dark:text-amber-50">
                {filteredIssues.map((issue, index) => (
                  <li
                    key={`issue-${index}`}
                    className="rounded border border-amber-200 bg-white/60 p-2 dark:border-amber-800 dark:bg-black/20"
                  >
                    <p className="font-medium">
                      [{issue.severity ?? 'error'}] {issue.source}: {issue.message}
                    </p>
                    {issue.hint && (
                      <p className="mt-1 text-amber-800 dark:text-amber-200">
                        {issue.hint}
                      </p>
                    )}
                    {issue.code && (
                      <p className="mt-1 text-xs text-amber-700 dark:text-amber-300">
                        Code: {issue.code}
                      </p>
                    )}
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

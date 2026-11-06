/**
 * Status, do-not-publish line, errors, and notes for one convert result.
 */

import {
  DO_NOT_PUBLISH_LABEL,
  type ResultCardAssessment,
  type ResultCardLine,
} from '/utils/resultCard';

/**
 * Type `ConvertResultStatusProps`.
 * @example
 * const _ = true;
 */
export interface ConvertResultStatusProps {
  assessment: ResultCardAssessment;
}

/**
 * One message, with the code under the sentence when a code exists.
 *
 * @param line - Error or note text
 * @example
 * const _ = true;
 */
function ResultLine({ line }: { line: ResultCardLine }) {
  return (
    <li>
      <p>{line.message}</p>
      {line.code ? (
        <p className="text-xs text-gray-600 dark:text-gray-300">Code: {line.code}</p>
      ) : null}
    </li>
  );
}

/**
 * Lead with the status. Errors and notes stay in separate lists.
 *
 * @param props.assessment - Status and lines for this result
 * @example
 * const _ = true;
 */
export function ConvertResultStatus({ assessment }: ConvertResultStatusProps) {
  return (
    <div className="space-y-2 px-4 pb-3" data-testid="result-card-status">
      <p
        className="text-sm font-semibold text-gray-900 dark:text-white"
        data-testid="result-status-label"
      >
        {assessment.statusLabel}
      </p>
      {assessment.publishBlocked ? (
        <p
          className="text-sm font-medium text-red-800 dark:text-red-200"
          data-testid="result-do-not-publish"
        >
          {DO_NOT_PUBLISH_LABEL}
        </p>
      ) : null}
      {assessment.errors.length > 0 ? (
        <section aria-label="Errors">
          <h3 className="text-sm font-semibold text-gray-900 dark:text-white">
            Errors
          </h3>
          <ul className="mt-1 space-y-1 text-sm text-gray-800 dark:text-gray-100">
            {assessment.errors.map((line, index) => (
              <ResultLine key={`error-${index}`} line={line} />
            ))}
          </ul>
        </section>
      ) : null}
      {assessment.notes.length > 0 ? (
        <section aria-label="Notes">
          <h3 className="text-sm font-semibold text-gray-900 dark:text-white">Notes</h3>
          <ul className="mt-1 space-y-1 text-sm text-gray-800 dark:text-gray-100">
            {assessment.notes.map((line, index) => (
              <ResultLine key={`note-${index}`} line={line} />
            ))}
          </ul>
        </section>
      ) : null}
    </div>
  );
}

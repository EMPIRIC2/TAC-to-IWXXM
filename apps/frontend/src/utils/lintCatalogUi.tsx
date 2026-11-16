/**
 * Lint catalog presentational helpers (JSX).
 */
import type { LintIssueCatalogEntry } from '@/utils/openapiTypes';
import {
  LINT_VALIDATION_CATALOG_COL_SOURCE,
  LINT_VALIDATION_CATALOG_COL_TYPE,
  LINT_VALIDATION_CATALOG_EXAMPLE_FAIL,
  LINT_VALIDATION_CATALOG_EXAMPLE_FAIL_UNAVAILABLE,
  LINT_VALIDATION_CATALOG_EXAMPLE_NOTE,
  LINT_VALIDATION_CATALOG_EXAMPLE_PASS,
  LINT_VALIDATION_CATALOG_EXAMPLE_PASS_UNAVAILABLE,
  LINT_VALIDATION_CATALOG_EXAMPLES,
  LINT_VALIDATION_CATALOG_EXAMPLES_UNAVAILABLE,
} from '@/utils/lintValidationCatalogCopy';
import {
  isInfoCatalogLevel,
  plainInfoExample,
  ruleExamplePair,
} from '@/utils/ruleCatalogExamples';

/**
 * Extra fields for the selected rule in the detailed catalog view.
 * @example
 * const _ = true;
 */
export function SelectedRuleFacts({ entry }: { entry: LintIssueCatalogEntry }) {
  return (
    <div
      className="mt-3 space-y-1 text-sm text-gray-700 dark:text-gray-300"
      data-testid="catalog-detail-facts"
    >
      <p>
        {LINT_VALIDATION_CATALOG_COL_TYPE}: {entry.issue_type ?? '—'}
      </p>
      <p>
        {LINT_VALIDATION_CATALOG_COL_SOURCE}: {entry.source_locator ?? '—'}
      </p>
    </div>
  );
}

/**
 * Reports for the selected rule.
 * Info rules use one unlabeled sample. Other levels keep pass and fail headings.
 * @example
 * const _ = true;
 */
export function RuleExamples({
  code,
  severity,
}: {
  code: string;
  severity?: string | null;
}) {
  const examples = ruleExamplePair(code);
  if (isInfoCatalogLevel(severity)) {
    const sample = plainInfoExample(examples);
    return (
      <section className="mt-4 space-y-3" aria-label={LINT_VALIDATION_CATALOG_EXAMPLES}>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          {LINT_VALIDATION_CATALOG_EXAMPLE_NOTE}
        </p>
        <div>
          <h3 className="text-sm font-semibold text-gray-800 dark:text-gray-200">
            {LINT_VALIDATION_CATALOG_EXAMPLES}
          </h3>
          {sample ? (
            <pre
              data-testid="catalog-rule-example"
              data-tone="example"
              className="mt-1 overflow-x-auto rounded-md border border-gray-300 bg-gray-50 p-2 font-mono text-xs whitespace-pre-wrap text-gray-950 dark:border-gray-600 dark:bg-gray-900 dark:text-gray-100"
            >
              {sample}
            </pre>
          ) : (
            <p
              data-testid="catalog-rule-example"
              data-tone="unavailable"
              className="mt-1 text-sm text-gray-600 dark:text-gray-400"
            >
              {LINT_VALIDATION_CATALOG_EXAMPLES_UNAVAILABLE}
            </p>
          )}
        </div>
      </section>
    );
  }
  return (
    <section className="mt-4 space-y-3" aria-label="Passing and failing examples">
      <p className="text-sm text-gray-600 dark:text-gray-400">
        {LINT_VALIDATION_CATALOG_EXAMPLE_NOTE}
      </p>
      <div>
        <h3 className="text-sm font-semibold text-emerald-800 dark:text-emerald-300">
          {LINT_VALIDATION_CATALOG_EXAMPLE_PASS}
        </h3>
        {examples?.pass ? (
          <pre
            data-testid="catalog-rule-example-pass"
            data-tone="pass"
            className="mt-1 overflow-x-auto rounded-md border border-emerald-300 bg-emerald-50 p-2 font-mono text-xs whitespace-pre-wrap text-emerald-950 dark:border-emerald-800 dark:bg-emerald-950 dark:text-emerald-100"
          >
            {examples.pass}
          </pre>
        ) : (
          <p
            data-testid="catalog-rule-example-pass"
            data-tone="unavailable"
            className="mt-1 text-sm text-gray-600 dark:text-gray-400"
          >
            {LINT_VALIDATION_CATALOG_EXAMPLE_PASS_UNAVAILABLE}
          </p>
        )}
      </div>
      <div>
        <h3 className="text-sm font-semibold text-red-800 dark:text-red-300">
          {LINT_VALIDATION_CATALOG_EXAMPLE_FAIL}
        </h3>
        {examples?.fail ? (
          <pre
            data-testid="catalog-rule-example-fail"
            data-tone="fail"
            className="mt-1 overflow-x-auto rounded-md border border-red-300 bg-red-50 p-2 font-mono text-xs whitespace-pre-wrap text-red-950 dark:border-red-800 dark:bg-red-950 dark:text-red-100"
          >
            {examples.fail}
          </pre>
        ) : (
          <p
            data-testid="catalog-rule-example-fail"
            data-tone="unavailable"
            className="mt-1 text-sm text-gray-600 dark:text-gray-400"
          >
            {LINT_VALIDATION_CATALOG_EXAMPLE_FAIL_UNAVAILABLE}
          </p>
        )}
      </div>
    </section>
  );
}

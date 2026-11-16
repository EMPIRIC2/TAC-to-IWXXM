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
import { GlossaryRichText } from '@/app/components/glossary/GlossaryRichText';

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
  if (isInfoCatalogLevel(severity)) {
    const note = plainInfoExample(ruleExamplePair(code));
    return (
      <div className="mt-3 space-y-1 text-sm" data-testid="catalog-rule-examples">
        <p className="font-medium text-gray-900 dark:text-white">
          {LINT_VALIDATION_CATALOG_EXAMPLES}
        </p>
        {note ? (
          <GlossaryRichText text={note} className="text-gray-700 dark:text-gray-300" />
        ) : (
          <p className="text-gray-500 dark:text-gray-400">
            {LINT_VALIDATION_CATALOG_EXAMPLES_UNAVAILABLE}
          </p>
        )}
      </div>
    );
  }

  const pair = ruleExamplePair(code);
  return (
    <div className="mt-3 space-y-2 text-sm" data-testid="catalog-rule-examples">
      <p className="font-medium text-gray-900 dark:text-white">
        {LINT_VALIDATION_CATALOG_EXAMPLES}
      </p>
      <div>
        <p className="text-gray-600 dark:text-gray-400">
          {LINT_VALIDATION_CATALOG_EXAMPLE_PASS}
        </p>
        {pair?.pass ? (
          <GlossaryRichText
            text={pair.pass}
            className="text-gray-700 dark:text-gray-300"
          />
        ) : (
          <p className="text-gray-500 dark:text-gray-400">
            {LINT_VALIDATION_CATALOG_EXAMPLE_PASS_UNAVAILABLE}
          </p>
        )}
      </div>
      <div>
        <p className="text-gray-600 dark:text-gray-400">
          {LINT_VALIDATION_CATALOG_EXAMPLE_FAIL}
        </p>
        {pair?.fail ? (
          <GlossaryRichText
            text={pair.fail}
            className="text-gray-700 dark:text-gray-300"
          />
        ) : (
          <p className="text-gray-500 dark:text-gray-400">
            {LINT_VALIDATION_CATALOG_EXAMPLE_FAIL_UNAVAILABLE}
          </p>
        )}
      </div>
      <p className="text-xs text-gray-500 dark:text-gray-400">
        {LINT_VALIDATION_CATALOG_EXAMPLE_NOTE}
      </p>
    </div>
  );
}

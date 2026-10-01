/**
 * Packaged pass and fail reports for a rules-catalog entry.
 *
 * Samples come from the tac-validate fixture pack. A missing side stays empty
 * so the catalog can say the example is not available.
 */

import examples from '@/data/ruleCatalogExamples.json';

/** One packaged report, or nothing when that side was not on file. */
export type RuleExampleText = string | null;

/**
 * Type `RuleExamplePair`.
 * @example
 * const _ = true;
 */
export type RuleExamplePair = {
  pass?: string;
  fail?: string;
};

/**
 * Keep a non-empty report. Blank text is treated as not available.
 *
 * @param value - Report text from the packaged map
 * @returns Trimmed report, or null
 * @example
 * const _ = true;
 */
function keptReport(value: string | undefined): RuleExampleText {
  if (value == null) return null;
  const text = value.trim();
  return text === '' ? null : text;
}

/**
 * Pass and fail reports for a rule code from a packaged map.
 *
 * @param code - Catalog rule code
 * @param source - Code to packaged reports
 * @returns Pass and fail text, each null when that side is not on file
 * @example
 * const _ = true;
 */
export function ruleExamplePairFrom(
  code: string,
  source: Readonly<Record<string, RuleExamplePair>>,
): { pass: RuleExampleText; fail: RuleExampleText } {
  const row = source[code];
  return {
    pass: keptReport(row?.pass),
    fail: keptReport(row?.fail),
  };
}

/**
 * Pass and fail reports for a rule code from the packaged catalog map.
 *
 * @param code - Catalog rule code
 * @returns Pass and fail text, each null when that side is not on file
 * @example
 * const _ = true;
 */
export function ruleExamplePair(code: string): {
  pass: RuleExampleText;
  fail: RuleExampleText;
} {
  return ruleExamplePairFrom(code, examples);
}

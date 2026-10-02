/**
 * Operator-visible Validation Issues Catalog copy (plain language; no planning ids).
 */

/** Page title — primary shell tab. */
export const LINT_VALIDATION_CATALOG_PAGE_TITLE = 'Rule catalogs';

/** Page subtitle — plain-language purpose. */
export const LINT_VALIDATION_CATALOG_PAGE_SUBTITLE =
  'Inspect packaged rules for TAC validation, IWXXM validation, conversion, dissemination, and decoding.';

/** Empty list message. */
export const LINT_VALIDATION_CATALOG_EMPTY = 'No catalog entries for this filter.';

/** Loading indicator. */
export const LINT_VALIDATION_CATALOG_LOADING = 'Loading catalog…';

/** Search field label. */
export const LINT_VALIDATION_CATALOG_SEARCH = 'Search the catalog';

/** Detail pane heading for the selected rule. */
export const LINT_VALIDATION_CATALOG_DETAIL = 'Selected rule';

/** Filter labels. */
export const LINT_VALIDATION_CATALOG_FAMILY_LABEL = 'Family';
/** Family filter default. Covers every catalog, not only TAC and IWXXM. */
export const LINT_VALIDATION_CATALOG_FAMILY_ALL = 'All rules';
/** Shown when the catalog request fails. Never the raw fetch message. */
export const LINT_VALIDATION_CATALOG_LOAD_ERROR = 'The catalog could not be loaded.';
/** Button that runs the catalog request again. */
export const LINT_VALIDATION_CATALOG_RETRY = 'Try again';
/** Checkbox copy when Profile and Exchange are still All. */
export const LINT_VALIDATION_CATALOG_LISTED_PROFILE_NEEDS_PROFILE =
  'Choose a profile to show only rules that list it.';
export const LINT_VALIDATION_CATALOG_TYPE_LABEL = 'Type';
export const LINT_VALIDATION_CATALOG_LEVEL_LABEL = 'Level';
export const LINT_VALIDATION_CATALOG_ACCESS_LABEL = 'Access';
export const LINT_VALIDATION_CATALOG_SORT_LABEL = 'Sort';
export const LINT_VALIDATION_CATALOG_PROFILE_LABEL = 'Profile';
export const LINT_VALIDATION_CATALOG_EXCHANGE_LABEL = 'Exchange';
export const LINT_VALIDATION_CATALOG_PROFILE_ALL = 'All profiles';
export const LINT_VALIDATION_CATALOG_EXCHANGE_ALL = 'All exchange profiles';
/** Optional filter: hide unrestricted (all-profiles) rows when a profile is selected. */
export const LINT_VALIDATION_CATALOG_LISTED_PROFILE_ONLY =
  'Only rules that list this profile';

/** Column headers (table / list). */
export const LINT_VALIDATION_CATALOG_COL_CODE = 'Code';
export const LINT_VALIDATION_CATALOG_COL_TYPE = 'Type';
export const LINT_VALIDATION_CATALOG_COL_LEVEL = 'Level';
export const LINT_VALIDATION_CATALOG_COL_PROFILES = 'Profiles';
export const LINT_VALIDATION_CATALOG_COL_DESCRIPTION = 'Description';
export const LINT_VALIDATION_CATALOG_COL_SOURCE = 'Source';

/** Heading for the packaged report that does not raise the selected rule. */
export const LINT_VALIDATION_CATALOG_EXAMPLE_PASS = 'Passing example';

/** Heading for the packaged report that raises the selected rule. */
export const LINT_VALIDATION_CATALOG_EXAMPLE_FAIL = 'Failing example';

/** Shown when no packaged passing report is on file for this rule. */
export const LINT_VALIDATION_CATALOG_EXAMPLE_PASS_UNAVAILABLE =
  'No passing example is available for this rule yet.';

/** Shown when no packaged failing report is on file for this rule. */
export const LINT_VALIDATION_CATALOG_EXAMPLE_FAIL_UNAVAILABLE =
  'No failing example is available for this rule yet.';

/** Note that the samples are existing reports, not ones written for the screen. */
export const LINT_VALIDATION_CATALOG_EXAMPLE_NOTE =
  'Only a report already on file is shown here.';

/** Group label for compact and detailed catalog layout. */
export const LINT_VALIDATION_CATALOG_VIEW_LABEL = 'Catalog view';

/** Layout that shows more of each selected rule. */
export const LINT_VALIDATION_CATALOG_VIEW_DETAILED = 'Detailed';

/** Layout that shows more rules at once. */
export const LINT_VALIDATION_CATALOG_VIEW_COMPACT = 'Compact';

/** Plain labels for type-filter values. Option values stay the API codes. */
export const LINT_VALIDATION_CATALOG_TYPE_LABELS: Record<string, string> = {
  all: 'All',
  presence: 'Missing or extra',
  structure: 'Structure',
  content: 'Content',
  consistency: 'Consistency',
  iwxxm_schema: 'XML schema',
  profile: 'Profile',
  policy: 'Policy',
  other: 'Other',
};

/** Plain labels for access-filter values. Option values stay the API codes. */
export const LINT_VALIDATION_CATALOG_ACCESS_LABELS: Record<string, string> = {
  all: 'All',
  public: 'Public',
  paywall: 'Paid source',
  login: 'Sign-in required',
  semantic_only: 'No source document',
};

/**
 * Operator label for a type or access filter value.
 *
 * @param kind - Which filter the value belongs to
 * @param value - API option value
 * @returns Plain label, or the value with underscores as spaces
 * @example
 * const _ = true;
 */
export function catalogFilterLabel(kind: 'type' | 'access', value: string): string {
  const table =
    kind === 'type'
      ? LINT_VALIDATION_CATALOG_TYPE_LABELS
      : LINT_VALIDATION_CATALOG_ACCESS_LABELS;
  return table[value] ?? value.replaceAll('_', ' ');
}

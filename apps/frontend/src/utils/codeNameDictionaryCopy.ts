/**
 * Operator-facing copy for the Code names dictionary tab.
 */

export const CODE_NAME_DICTIONARY_PAGE_TITLE = 'Code names';

export const CODE_NAME_DICTIONARY_INTRO =
  'Look up TAC code names and filter by product, country, and WMO amendment.';

export const CODE_NAME_DICTIONARY_SEARCH_LABEL = 'Search';

export const CODE_NAME_DICTIONARY_SEARCH_PLACEHOLDER = 'Code or meaning';

export const CODE_NAME_DICTIONARY_PRODUCT_LABEL = 'Product';

export const CODE_NAME_DICTIONARY_COUNTRY_LABEL = 'Country';

export const CODE_NAME_DICTIONARY_AMENDMENT_LABEL = 'WMO amendment introduced in';

export const CODE_NAME_DICTIONARY_FILTER_ALL = 'All';

export const CODE_NAME_DICTIONARY_COL_CODE = 'Code';

export const CODE_NAME_DICTIONARY_COL_MEANING = 'Meaning';

export const CODE_NAME_DICTIONARY_COL_PRODUCTS = 'Products';

export const CODE_NAME_DICTIONARY_COL_COUNTRIES = 'Countries';

export const CODE_NAME_DICTIONARY_COL_AMENDMENT = 'WMO amendment';

export const CODE_NAME_DICTIONARY_EMPTY = 'No code names match these filters.';

export const CODE_NAME_DICTIONARY_LOAD_ERROR =
  'Could not load the code name dictionary. Try again.';

export const CODE_NAME_DICTIONARY_LOADING = 'Loading code names…';

export const CODE_NAME_DICTIONARY_COUNT = (n: number): string =>
  n === 1 ? '1 code name' : `${n} code names`;

/**
 * Operator Code names dictionary tab — tagged Decoding glossary lookup.
 */

import { useCallback, useEffect, useMemo, useState } from 'react';
import { fetchCodeNameDictionary, type CodeNameDictionaryItem } from '@/utils/api';
import {
  CODE_NAME_DICTIONARY_AMENDMENT_LABEL,
  CODE_NAME_DICTIONARY_COL_AMENDMENT,
  CODE_NAME_DICTIONARY_COL_CODE,
  CODE_NAME_DICTIONARY_COL_COUNTRIES,
  CODE_NAME_DICTIONARY_COL_MEANING,
  CODE_NAME_DICTIONARY_COL_PRODUCTS,
  CODE_NAME_DICTIONARY_COUNT,
  CODE_NAME_DICTIONARY_COUNTRY_LABEL,
  CODE_NAME_DICTIONARY_EMPTY,
  CODE_NAME_DICTIONARY_FILTER_ALL,
  CODE_NAME_DICTIONARY_INTRO,
  CODE_NAME_DICTIONARY_LOAD_ERROR,
  CODE_NAME_DICTIONARY_LOADING,
  CODE_NAME_DICTIONARY_PAGE_TITLE,
  CODE_NAME_DICTIONARY_PRODUCT_LABEL,
  CODE_NAME_DICTIONARY_SEARCH_LABEL,
  CODE_NAME_DICTIONARY_SEARCH_PLACEHOLDER,
} from '@/utils/codeNameDictionaryCopy';
import { shellFrameClass, useLiveConvertLayout } from '@/utils/liveConvertLayout';

/**
 * Drop the sentinel "all" filter value from API query params.
 *
 * @param value - Select value
 * @returns Undefined when the filter is All
 */
function optionalFilter(value: string): string | undefined {
  return value === 'all' ? undefined : value;
}

/**
 * Build GET /code-name-dictionary query params from page filter state.
 *
 * @param input - Search and tag filter state
 * @returns API query object
 */
function dictionaryQueryParams(input: {
  query: string;
  product: string;
  country: string;
  amendment: string;
}): {
  q?: string;
  product?: string;
  country?: string;
  wmo_amendment?: string;
} {
  return {
    q: input.query.trim() || undefined,
    product: optionalFilter(input.product),
    country: optionalFilter(input.country),
    wmo_amendment: optionalFilter(input.amendment),
  };
}

/**
 * Code names dictionary page with product / country / amendment filters.
 */
export function CodeNameDictionaryPage() {
  const { layout } = useLiveConvertLayout();
  const frame = shellFrameClass(layout.span);
  const [items, setItems] = useState<CodeNameDictionaryItem[]>([]);
  const [products, setProducts] = useState<string[]>([]);
  const [countries, setCountries] = useState<string[]>([]);
  const [amendments, setAmendments] = useState<string[]>([]);
  const [query, setQuery] = useState('');
  const [product, setProduct] = useState('all');
  const [country, setCountry] = useState('all');
  const [amendment, setAmendment] = useState('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetchCodeNameDictionary(
        dictionaryQueryParams({ query, product, country, amendment }),
      );
      setItems(response.items ?? []);
      setProducts(response.facets?.products ?? []);
      setCountries(response.facets?.countries ?? []);
      setAmendments(response.facets?.wmo_amendments ?? []);
    } catch {
      setError(CODE_NAME_DICTIONARY_LOAD_ERROR);
      setItems([]);
    } finally {
      setLoading(false);
    }
  }, [query, product, country, amendment]);

  /* eslint-disable react-hooks/set-state-in-effect -- refetch when filters change */
  useEffect(() => {
    void load();
  }, [load]);
  /* eslint-enable react-hooks/set-state-in-effect */

  const countLabel = useMemo(
    () => CODE_NAME_DICTIONARY_COUNT(items.length),
    [items.length],
  );

  return (
    <main
      className={`mx-auto w-full px-4 py-6 ${frame}`}
      data-testid="code-name-dictionary-page"
      aria-labelledby="code-name-dictionary-title"
    >
      <header className="mb-4 space-y-1">
        <h1
          id="code-name-dictionary-title"
          className="text-xl font-semibold text-gray-900 dark:text-gray-50"
        >
          {CODE_NAME_DICTIONARY_PAGE_TITLE}
        </h1>
        <p className="text-sm text-gray-600 dark:text-gray-300">
          {CODE_NAME_DICTIONARY_INTRO}
        </p>
      </header>

      <div
        className="mb-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4"
        data-testid="code-name-dictionary-filters"
      >
        <label className="flex flex-col gap-1 text-sm">
          <span className="font-medium text-gray-700 dark:text-gray-200">
            {CODE_NAME_DICTIONARY_SEARCH_LABEL}
          </span>
          <input
            type="search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder={CODE_NAME_DICTIONARY_SEARCH_PLACEHOLDER}
            className="rounded-md border border-gray-300 bg-white px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-900"
            data-testid="code-name-dictionary-search"
          />
        </label>
        <label className="flex flex-col gap-1 text-sm">
          <span className="font-medium text-gray-700 dark:text-gray-200">
            {CODE_NAME_DICTIONARY_PRODUCT_LABEL}
          </span>
          <select
            value={product}
            onChange={(event) => setProduct(event.target.value)}
            className="rounded-md border border-gray-300 bg-white px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-900"
            data-testid="code-name-dictionary-product"
          >
            <option value="all">{CODE_NAME_DICTIONARY_FILTER_ALL}</option>
            {products.map((value) => (
              <option key={value} value={value}>
                {value}
              </option>
            ))}
          </select>
        </label>
        <label className="flex flex-col gap-1 text-sm">
          <span className="font-medium text-gray-700 dark:text-gray-200">
            {CODE_NAME_DICTIONARY_COUNTRY_LABEL}
          </span>
          <select
            value={country}
            onChange={(event) => setCountry(event.target.value)}
            className="rounded-md border border-gray-300 bg-white px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-900"
            data-testid="code-name-dictionary-country"
          >
            <option value="all">{CODE_NAME_DICTIONARY_FILTER_ALL}</option>
            {countries.map((value) => (
              <option key={value} value={value}>
                {value}
              </option>
            ))}
          </select>
        </label>
        <label className="flex flex-col gap-1 text-sm">
          <span className="font-medium text-gray-700 dark:text-gray-200">
            {CODE_NAME_DICTIONARY_AMENDMENT_LABEL}
          </span>
          <select
            value={amendment}
            onChange={(event) => setAmendment(event.target.value)}
            className="rounded-md border border-gray-300 bg-white px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-900"
            data-testid="code-name-dictionary-amendment"
          >
            <option value="all">{CODE_NAME_DICTIONARY_FILTER_ALL}</option>
            {amendments.map((value) => (
              <option key={value} value={value}>
                {value}
              </option>
            ))}
          </select>
        </label>
      </div>

      <p
        className="mb-2 text-sm text-gray-600 dark:text-gray-300"
        data-testid="code-name-dictionary-count"
      >
        {loading ? CODE_NAME_DICTIONARY_LOADING : countLabel}
      </p>

      {error ? (
        <p
          className="text-sm text-red-700 dark:text-red-300"
          role="alert"
          data-testid="code-name-dictionary-error"
        >
          {error}
        </p>
      ) : null}

      {!loading && !error && items.length === 0 ? (
        <p
          className="text-sm text-gray-600 dark:text-gray-300"
          data-testid="code-name-dictionary-empty"
        >
          {CODE_NAME_DICTIONARY_EMPTY}
        </p>
      ) : null}

      {items.length > 0 ? (
        <div className="overflow-x-auto rounded-md border border-gray-200 dark:border-gray-700">
          <table
            className="min-w-full text-left text-sm"
            data-testid="code-name-dictionary-table"
          >
            <thead className="bg-gray-50 dark:bg-gray-900">
              <tr>
                <th className="px-3 py-2 font-medium">
                  {CODE_NAME_DICTIONARY_COL_CODE}
                </th>
                <th className="px-3 py-2 font-medium">
                  {CODE_NAME_DICTIONARY_COL_MEANING}
                </th>
                <th className="px-3 py-2 font-medium">
                  {CODE_NAME_DICTIONARY_COL_PRODUCTS}
                </th>
                <th className="px-3 py-2 font-medium">
                  {CODE_NAME_DICTIONARY_COL_COUNTRIES}
                </th>
                <th className="px-3 py-2 font-medium">
                  {CODE_NAME_DICTIONARY_COL_AMENDMENT}
                </th>
              </tr>
            </thead>
            <tbody>
              {items.map((row) => (
                <tr
                  key={row.id}
                  className="border-t border-gray-100 dark:border-gray-800"
                  data-testid={`code-name-row-${row.code}`}
                >
                  <td className="px-3 py-2 font-mono font-medium">{row.code}</td>
                  <td className="px-3 py-2">{row.meaning}</td>
                  <td className="px-3 py-2">{row.products.join(', ') || '—'}</td>
                  <td className="px-3 py-2">{row.countries.join(', ') || '—'}</td>
                  <td className="px-3 py-2">{row.wmo_amendment ?? '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}
    </main>
  );
}

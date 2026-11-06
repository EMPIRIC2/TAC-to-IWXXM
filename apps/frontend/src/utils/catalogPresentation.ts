/**
 * Presentation helpers for the rule catalog list and detail pane.
 */

/**
 * Family name written the way the catalog filters name it.
 *
 * @param family - Catalog family id, or blank
 * @returns Operator label, or an em dash when the family is missing
 * @example
 * const _ = true;
 */
export function catalogFamilyLabel(family: string | null | undefined): string {
  const raw = (family ?? '').trim();
  const key = raw.toLowerCase();
  if (key === 'lint') return 'TAC validation';
  if (key === 'iwxxm') return 'IWXXM validation';
  if (key === 'conversion') return 'Conversion';
  if (key === 'dissemination') return 'Dissemination';
  if (key === 'decoding') return 'Decoding';
  if (!key) return '—';
  return raw;
}

/**
 * Whether a catalog row matches a free-text search.
 *
 * @param code - Stable rule code
 * @param message - Plain-language description
 * @param query - Operator search text
 * @returns True when the query is blank or found in the code or description
 * @example
 * const _ = true;
 */
export function catalogEntryMatchesQuery(
  code: string | null | undefined,
  message: string | null | undefined,
  query: string,
): boolean {
  const needle = query.trim().toLowerCase();
  if (!needle) return true;
  return `${code ?? ''} ${message ?? ''}`.toLowerCase().includes(needle);
}

/**
 * Code to show in the detail pane.
 *
 * @param codes - Codes currently in the filtered list
 * @param selected - Last code the operator chose
 * @returns The chosen code when it is still listed, otherwise the first code
 * @example
 * const _ = true;
 */
export function selectedCatalogCode(
  codes: readonly string[],
  selected: string | null,
): string | null {
  if (codes.length === 0) return null;
  if (selected && codes.includes(selected)) return selected;
  const first = codes[0];
  return first ?? null;
}

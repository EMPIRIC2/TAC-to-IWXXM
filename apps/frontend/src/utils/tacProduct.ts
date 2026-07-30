/**
 * Detect TAC product keyword for F6.e auto product selection (UJ-005).
 *
 * Mirrors backend `_detect_product` for METAR/SPECI and extends to the seven
 * F6 products when an explicit keyword appears in the TAC body.
 */

export const TAC_PRODUCTS = [
  'AIRMET',
  'METAR',
  'SIGMET',
  'SPECI',
  'TAF',
  'VAA',
  'TCA',
] as const;

export type TacProduct = (typeof TAC_PRODUCTS)[number];

export type TacProductSelection = TacProduct | 'auto';

export type IwxxmProfile = 'annex3' | 'iwxxm_us';

const PRODUCT_RE =
  /\b(AIRMET|SIGMET|SPECI|METAR|TAF|VAA|TCA|VOLCANIC\s+ASH|TROPICAL\s+CYCLONE)\b/i;

/**
 * Detect a TAC product from text. Defaults to METAR when no keyword is found.
 *
 * @param tacText - Raw TAC or bulletin fragment
 * @param defaultProduct - Fallback when no keyword matches
 * @returns Uppercase product enum value
 */
export function detectTacProduct(
  tacText: string,
  defaultProduct: TacProduct = 'METAR',
): TacProduct {
  const match = tacText.match(PRODUCT_RE);
  if (!match) {
    return defaultProduct;
  }
  const token = match[1].toUpperCase().replace(/\s+/g, ' ');
  if (token.startsWith('VOLCANIC')) {
    return 'VAA';
  }
  if (token.startsWith('TROPICAL')) {
    return 'TCA';
  }
  if ((TAC_PRODUCTS as readonly string[]).includes(token)) {
    return token as TacProduct;
  }
  return defaultProduct;
}

/**
 * Resolve UI product selection to the multipart `product` value required by the API.
 *
 * @param selection - UI picker value (`auto` or explicit product)
 * @param tacText - TAC used for auto-detect
 */
export function resolveConvertProduct(
  selection: TacProductSelection,
  tacText: string,
): TacProduct {
  if (selection === 'auto') {
    return detectTacProduct(tacText);
  }
  return selection;
}

/** Products whose TAC is a multi-line template document (must not be line-split). */
const MULTILINE_TEMPLATE_PRODUCTS = new Set<TacProduct>(['VAA', 'TCA']);

/**
 * Split manual TAC input into conversion entries (mirrors backend
 * ``split_manual_entries``).
 *
 * METAR/SPECI/TAF/SIGMET/AIRMET: one entry per non-empty line.
 * VAA/TCA: entire buffer is one advisory document (F26/F27).
 *
 * @param manualText - Editor buffer
 * @param product - Resolved convert product
 * @returns Entry texts in convert order
 */
export function splitManualEntries(
  manualText: string,
  product: TacProduct | string,
): string[] {
  if (!manualText) {
    return [];
  }
  const productU = product.trim().toUpperCase();
  if (MULTILINE_TEMPLATE_PRODUCTS.has(productU as TacProduct)) {
    const text = manualText.trim();
    return text ? [text] : [];
  }
  return manualText
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean);
}

/**
 * Detect TAC product keyword for F6.e auto product selection (UJ-005).
 *
 * Mirrors backend `_detect_product` for METAR/SPECI and extends to F6 + F28/F32
 * products when an explicit keyword appears in the TAC body.
 */

export const TAC_PRODUCTS = [
  'AIRMET',
  'METAR',
  'SIGMET',
  'SPECI',
  'TAF',
  'VAA',
  'TCA',
  'SWXA',
  'VONA',
] as const;

/** Wire products including IWXXM pass-through (F7.t / EV-060 / #1003). */
export const CONVERT_PRODUCTS = [...TAC_PRODUCTS, 'IWXXM'] as const;

export type TacProduct = (typeof TAC_PRODUCTS)[number];

export type ConvertProduct = (typeof CONVERT_PRODUCTS)[number];

export type TacProductSelection = ConvertProduct | 'auto';

/**
 * Whether a stored/UI product string is a known convert selection (incl. auto).
 *
 * @param value - Candidate product string
 * @returns True when `value` is auto or a CONVERT_PRODUCTS member
 */
export function isConvertProductSelection(value: string): value is TacProductSelection {
  return value === 'auto' || (CONVERT_PRODUCTS as readonly string[]).includes(value);
}

export type IwxxmProfile = 'annex3' | 'iwxxm_us' | 'ca_eccc';

const IWXXM_PROFILES: readonly IwxxmProfile[] = ['annex3', 'iwxxm_us', 'ca_eccc'];

/**
 * Narrow stored/UI profile strings to a supported IWXXM emit profile.
 *
 * @param value - Candidate profile string
 * @returns Supported profile id
 */
export function coerceIwxxmProfile(value: unknown): IwxxmProfile {
  if (
    typeof value === 'string' &&
    (IWXXM_PROFILES as readonly string[]).includes(value)
  ) {
    return value as IwxxmProfile;
  }
  return 'annex3';
}

const PRODUCT_RE =
  /\b(AIRMET|SIGMET|SPECI|METAR|TAF|VAA|TCA|SWXA|VONA|SWX\s+ADVISORY|VOLCANIC\s+ASH|TROPICAL\s+CYCLONE)\b/i;

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
  const token = match[1]!.toUpperCase().replace(/\s+/g, ' ');
  if (token.startsWith('VOLCANIC')) {
    return 'VAA';
  }
  if (token.startsWith('TROPICAL')) {
    return 'TCA';
  }
  if (token.startsWith('SWX')) {
    return 'SWXA';
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
): ConvertProduct {
  if (selection === 'auto') {
    return detectTacProduct(tacText);
  }
  return selection;
}

/** Products whose TAC is a multi-line document (must not be line-split). */
const MULTILINE_TEMPLATE_PRODUCTS = new Set<string>([
  'SIGMET',
  'AIRMET',
  'VAA',
  'TCA',
  'SWXA',
  'VONA',
  'IWXXM',
]);

/**
 * Split manual TAC input into conversion entries (mirrors backend
 * ``split_manual_entries``).
 *
 * METAR/SPECI/TAF: one entry per non-empty line.
 * SIGMET/AIRMET/VAA/TCA/SWXA/VONA/IWXXM: entire buffer is one document.
 *
 * @param manualText - Editor buffer
 * @param product - Resolved convert product
 * @returns Entry texts in convert order
 */
export function splitManualEntries(
  manualText: string,
  product: ConvertProduct | string,
): string[] {
  if (!manualText) {
    return [];
  }
  const productU = product.trim().toUpperCase();
  if (MULTILINE_TEMPLATE_PRODUCTS.has(productU)) {
    const text = manualText.trim();
    return text ? [text] : [];
  }
  return manualText
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean);
}

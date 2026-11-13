/**
 * Parse live-map overlay fields from raw TAC. [Corpus: product] F37
 */

export type TacWindParse = {
  directionDeg: number | null;
  speedKt: number;
  gustKt: number | null;
  variable: boolean;
};

export type TacOverlayParse = {
  wind: TacWindParse | null;
  temperatureC: number | null;
  precipCodes: string[];
  hasThunder: boolean;
  hasIce: boolean;
};

const WIND_RE = /\b(VRB|\d{3})(\d{2,3})(?:G(\d{2,3}))?KT\b/;
/** METAR temp/dewpoint after the body; avoid RVR `R04/P1500` and time groups. */
const TEMP_RE = /(?:^|\s)(M?\d{2})\/(M?\d{2})(?:\s|$)/;
const PRECIP_RE =
  /(?:^|[\s+])((?:\+|-|VC|RE)?(?:SH|TS|FZ)?(?:RA|SN|DZ|SG|PL|GR|GS|UP|IC)+)\b/g;
const THUNDER_RE = /\b(?:VC)?TS[A-Z]*\b|\bTHUNDERSTORM\b/;
const ICE_RE = /\b(?:FZ[A-Z]+|ICING|ICE|IC)\b/;

/**
 * Decode a leading `M` cold mark into a signed Celsius value.
 *
 * @param raw - Two-digit temp token with optional M
 * @returns Celsius
 * @example
 * tempTokenToC('M05');
 */
export function tempTokenToC(raw: string): number {
  const cold = raw.startsWith('M');
  const digits = cold ? raw.slice(1) : raw;
  const value = Number(digits);
  return cold ? -value : value;
}

/**
 * Pull wind, temperature, precip, thunder, and ice signals from one TAC string.
 *
 * @param tac - Raw TAC
 * @returns Overlay fields (nulls/empty when absent)
 * @example
 * parseTacOverlayFields('METAR KJFK 18012KT 3SM -RA 12/08');
 */
export function parseTacOverlayFields(tac: string): TacOverlayParse {
  const text = tac.toUpperCase();
  const windMatch = text.match(WIND_RE);
  let wind: TacWindParse | null = null;
  if (windMatch) {
    const variable = windMatch[1] === 'VRB';
    wind = {
      directionDeg: variable ? null : Number(windMatch[1]),
      speedKt: Number(windMatch[2]),
      gustKt: windMatch[3] ? Number(windMatch[3]) : null,
      variable,
    };
  }
  const tempMatch = text.match(TEMP_RE);
  const tempToken = tempMatch?.[1];
  const temperatureC = tempToken ? tempTokenToC(tempToken) : null;
  const precipCodes: string[] = [];
  for (const match of text.matchAll(PRECIP_RE)) {
    const code = match[1];
    if (code && !precipCodes.includes(code)) {
      precipCodes.push(code);
    }
  }
  return {
    wind,
    temperatureC,
    precipCodes,
    hasThunder: THUNDER_RE.test(text),
    hasIce: ICE_RE.test(text),
  };
}

/**
 * Newest report TAC on a place, or empty string.
 *
 * @param reports - Ordered reports (index 0 = newest in live-map cache)
 * @returns TAC text
 * @example
 * newestTac([{ observed_at: 'a', tac: 'METAR' }]);
 */
export function newestTac(
  reports: ReadonlyArray<{ tac: string }>,
): string {
  return reports[0]?.tac ?? '';
}

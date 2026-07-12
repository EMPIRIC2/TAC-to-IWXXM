/**
 * Helpers for conversion-result input traceability (#655 / EV-007).
 *
 * Derives human-readable labels from TAC text for result cards while keeping
 * download filenames governed by {@link manualOutputName} (#664).
 */

/** Max characters for the TAC snippet shown in a result card header. */
export const TAC_SNIPPET_MAX_LEN = 72;

const TAC_HEADLINE_RE =
  /^(?:(METAR|SPECI|TAF|SIGMET|AIRMET|VAA|TCA)\s+)?([A-Z]{4})\s+(\d{6}Z)/i;

/**
 * Parse a short headline from the first line of TAC (product, station, time).
 */
export function parseTacHeadline(tac: string): {
  product: string | null;
  station: string | null;
  time: string | null;
} {
  const line = tac.trim().split(/\r?\n/)[0]?.trim() ?? '';
  const match = line.match(TAC_HEADLINE_RE);
  if (!match) {
    return { product: null, station: null, time: null };
  }
  return {
    product: (match[1] ?? 'METAR').toUpperCase(),
    station: match[2].toUpperCase(),
    time: match[3].toUpperCase(),
  };
}

/**
 * Build a TAC-derived card title (e.g. ``METAR KJFK 121251Z``).
 *
 * Falls back to ``downloadName`` when the TAC does not match a known headline.
 *
 * @param tac - Original TAC text for the result.
 * @param downloadName - Filename used for download (e.g. ``manual_input.txt``).
 */
export function deriveTacDisplayTitle(tac: string, downloadName: string): string {
  const { product, station, time } = parseTacHeadline(tac);
  if (station && time) {
    return `${product ?? 'METAR'} ${station} ${time}`;
  }
  const compact = tac.trim().replace(/\s+/g, ' ');
  if (compact.length > 0 && compact.length <= 48) {
    return compact;
  }
  return downloadName;
}

/**
 * Truncate TAC for inline display in a result card header.
 */
export function truncateTacSnippet(tac: string, maxLen = TAC_SNIPPET_MAX_LEN): string {
  const compact = tac.trim().replace(/\s+/g, ' ');
  if (compact.length <= maxLen) {
    return compact;
  }
  return `${compact.slice(0, maxLen - 1)}…`;
}

/**
 * Resolve the original TAC echoed for a conversion result.
 *
 * Prefers API ``tac_input``; falls back to manual line or uploaded file content.
 */
export function resolveOriginalTac(
  tacInput: string | undefined,
  manualLine: string | undefined,
  fileContent: string | undefined,
): string {
  const fromApi = tacInput?.trim();
  if (fromApi) {
    return fromApi;
  }
  const fromManual = manualLine?.trim();
  if (fromManual) {
    return fromManual;
  }
  return fileContent?.trim() ?? '';
}

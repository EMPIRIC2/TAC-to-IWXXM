/**
 * Build METAR/SPECI TAC from structured handbook-order fields.
 */

export type MetarSpeciFormState = {
  product: 'METAR' | 'SPECI';
  cor: boolean;
  auto: boolean;
  nil: boolean;
  cccc: string;
  dayTime: string;
  wind: string;
  visibility: string;
  rvr: string;
  weather: string;
  cloud: string;
  temperature: string;
  qnh: string;
  supplementary: string;
  rmk: string;
  includeRmk: boolean;
};

const BODY_KEYS = [
  'wind',
  'visibility',
  'rvr',
  'weather',
  'cloud',
  'temperature',
  'qnh',
  'supplementary',
] as const;

/**
 * Uppercase whitespace-separated TAC tokens from a raw field value.
 *
 * @param raw - Operator-entered group text
 * @returns Non-empty uppercase tokens
 */
function tokens(raw: string): string[] {
  return raw.trim().toUpperCase().split(/\s+/).filter(Boolean);
}

/**
 * Append product, COR, CCCC, and day/time groups.
 *
 * @param parts - Accumulated TAC parts
 * @param state - Form field values
 */
function appendIdentity(parts: string[], state: MetarSpeciFormState): void {
  parts.push(state.product);
  if (state.cor) {
    parts.push('COR');
  }
  const cccc = state.cccc.trim().toUpperCase();
  if (cccc) {
    parts.push(cccc);
  }
  let dayTime = state.dayTime.trim().toUpperCase();
  if (dayTime && !dayTime.endsWith('Z')) {
    dayTime = `${dayTime}Z`;
  }
  if (dayTime) {
    parts.push(dayTime);
  }
}

/**
 * Append surface body groups, skipping weather/cloud when CAVOK.
 *
 * @param parts - Accumulated TAC parts
 * @param state - Form field values
 */
function appendBody(parts: string[], state: MetarSpeciFormState): void {
  if (state.auto) {
    parts.push('AUTO');
  }
  const cavok = state.visibility.trim().toUpperCase() === 'CAVOK';
  for (const key of BODY_KEYS) {
    if (cavok && (key === 'weather' || key === 'cloud')) {
      continue;
    }
    parts.push(...tokens(state[key]));
  }
}

/**
 * Append RMK tokens when national remarks are enabled.
 *
 * @param parts - Accumulated TAC parts
 * @param state - Form field values
 */
function appendRemarks(parts: string[], state: MetarSpeciFormState): void {
  if (!state.includeRmk) {
    return;
  }
  const rmk = state.rmk.trim();
  if (!rmk) {
    return;
  }
  const upper = rmk.toUpperCase();
  if (upper.startsWith('RMK')) {
    parts.push(...tokens(rmk));
    return;
  }
  parts.push('RMK', ...tokens(rmk));
}

/**
 * Build METAR/SPECI TAC from structured fields in handbook order.
 *
 * @param state - Form field values
 * @returns TAC string ending with ``=``
 */
export function buildMetarSpeciTac(state: MetarSpeciFormState): string {
  const parts: string[] = [];
  appendIdentity(parts, state);
  if (state.nil) {
    parts.push('NIL');
    return `${parts.join(' ')}=`;
  }
  appendBody(parts, state);
  appendRemarks(parts, state);
  return `${parts.join(' ')}=`;
}

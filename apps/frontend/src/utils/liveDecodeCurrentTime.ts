/**
 * Format and persist "current time" for Live decode (local + UTC).
 *
 * [Corpus: product §F9] [Corpus: product §F10] [Corpus: ui-style]
 */

/** localStorage key for the Show current time toggle (default ON). */
export const LIVE_DECODE_SHOW_CURRENT_TIME_KEY =
  'tac-to-iwxxm.live-decode.show-current-time' as const;

/**
 * Read whether the Live decode current-time row should show.
 *
 * @returns true when unset or stored as on
 * @example
 * const _ = true;
 */
export function readShowLiveDecodeCurrentTime(): boolean {
  try {
    const raw = localStorage.getItem(LIVE_DECODE_SHOW_CURRENT_TIME_KEY);
    if (raw === null) {
      return true;
    }
    return raw !== 'false';
  } catch {
    return true;
  }
}

/**
 * Persist the Show current time toggle.
 *
 * @param show - next visibility
 * @example
 * const _ = true;
 */
export function writeShowLiveDecodeCurrentTime(show: boolean): void {
  try {
    localStorage.setItem(LIVE_DECODE_SHOW_CURRENT_TIME_KEY, show ? 'true' : 'false');
  } catch {
    // Quota / private mode — keep in-memory only.
  }
}

/**
 * Parts of the Live decode Now label (local + UTC).
 *
 * @example
 * const _ = true;
 */
export type LiveDecodeCurrentTimeParts = {
  /** Full operator string, e.g. `Now: 15:23 EST · 20:23 UTC` */
  label: string;
  /** Local clock HH:MM (24h) */
  localTime: string;
  /** Zone abbrev or offset, e.g. EST or GMT-5 */
  localZone: string;
  /** UTC clock HH:MM (24h) */
  utcTime: string;
};

/**
 * Pad hour/minute to two digits.
 *
 * @param value - hour or minute
 * @returns zero-padded string
 */
function pad2(value: number): string {
  return String(value).padStart(2, '0');
}

/**
 * Build the operator Now label from parts.
 *
 * @param localTime - local HH:MM
 * @param localZone - abbrev or offset
 * @param utcTime - UTC HH:MM
 * @returns STE-plain Now string
 */
function buildNowLabel(localTime: string, localZone: string, utcTime: string): string {
  const zoneLooksLikeAbbrev = /^[A-Za-z]{2,5}$/.test(localZone);
  const localDisplay = zoneLooksLikeAbbrev
    ? `${localTime} ${localZone}`
    : `${localTime} (${localZone})`;
  return `Now: ${localDisplay} · ${utcTime} UTC`;
}

/**
 * Manual local + UTC clocks when Intl is missing or throws.
 *
 * @param date - instant to format
 * @returns STE-plain Now label parts
 */
function formatFallback(date: Date): LiveDecodeCurrentTimeParts {
  const localTime = `${pad2(date.getHours())}:${pad2(date.getMinutes())}`;
  const offsetMin = -date.getTimezoneOffset();
  const sign = offsetMin >= 0 ? '+' : '-';
  const abs = Math.abs(offsetMin);
  const localZone = `UTC${sign}${pad2(Math.floor(abs / 60))}:${pad2(abs % 60)}`;
  const utcTime = `${pad2(date.getUTCHours())}:${pad2(date.getUTCMinutes())}`;
  return {
    localTime,
    localZone,
    utcTime,
    label: buildNowLabel(localTime, localZone, utcTime),
  };
}

/**
 * Read HH:MM from Intl formatToParts.
 *
 * @param parts - formatToParts result
 * @returns HH:MM or null
 */
function hhmmFromParts(parts: Intl.DateTimeFormatPart[]): string | null {
  const hour = parts.find((p) => p.type === 'hour')?.value;
  const minute = parts.find((p) => p.type === 'minute')?.value;
  if (!hour || !minute) {
    return null;
  }
  return `${hour}:${minute}`;
}

/**
 * Resolve a short zone name or offset for the local leg.
 *
 * @param date - instant
 * @param timeZone - optional IANA zone
 * @param fallbackZone - offset string if Intl omits the name
 * @returns zone label
 */
function resolveLocalZone(
  date: Date,
  timeZone: string | undefined,
  fallbackZone: string,
): string {
  const named = new Intl.DateTimeFormat(undefined, {
    timeZoneName: 'short',
    ...(timeZone ? { timeZone } : {}),
  })
    .formatToParts(date)
    .find((p) => p.type === 'timeZoneName')
    ?.value?.trim();
  if (named) {
    return named;
  }
  const offset = new Intl.DateTimeFormat(undefined, {
    timeZoneName: 'shortOffset',
    ...(timeZone ? { timeZone } : {}),
  })
    .formatToParts(date)
    .find((p) => p.type === 'timeZoneName')
    ?.value?.trim();
  return offset || fallbackZone;
}

/**
 * Format via Intl; returns null when parts are incomplete.
 *
 * @param date - instant
 * @param timeZone - optional IANA zone
 * @returns parts or null to trigger fallback
 */
function formatWithIntl(
  date: Date,
  timeZone?: string,
): LiveDecodeCurrentTimeParts | null {
  const localParts = new Intl.DateTimeFormat(undefined, {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
    timeZoneName: 'short',
    ...(timeZone ? { timeZone } : {}),
  }).formatToParts(date);
  const localTime = hhmmFromParts(localParts);
  if (!localTime) {
    return null;
  }

  const fallback = formatFallback(date);
  const localZone = resolveLocalZone(date, timeZone, fallback.localZone);

  const utcTime = hhmmFromParts(
    new Intl.DateTimeFormat('en-GB', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: false,
      timeZone: 'UTC',
    }).formatToParts(date),
  );
  if (!utcTime) {
    return null;
  }

  return {
    localTime,
    localZone,
    utcTime,
    label: buildNowLabel(localTime, localZone, utcTime),
  };
}

/**
 * Format the current instant for Live decode (local zone + UTC).
 *
 * Preferred shape: `Now: 15:23 EST · 20:23 UTC`.
 * Falls back to an offset zone when Intl short names are unavailable.
 *
 * @param date - instant to format (injectable for tests)
 * @param timeZone - optional IANA zone for local leg (defaults to runtime zone)
 * @returns label parts; never throws
 * @example
 * const _ = true;
 */
export function formatLiveDecodeCurrentTime(
  date: Date = new Date(),
  timeZone?: string,
): LiveDecodeCurrentTimeParts {
  if (typeof Intl === 'undefined' || typeof Intl.DateTimeFormat !== 'function') {
    return formatFallback(date);
  }
  try {
    return formatWithIntl(date, timeZone) ?? formatFallback(date);
  } catch {
    return formatFallback(date);
  }
}

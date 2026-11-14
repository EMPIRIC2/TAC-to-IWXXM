/**
 * Resolve report validity for the live-map Active reports filter.
 *
 * Prefer optional ``valid_from`` / ``valid_to`` on the report. When those are
 * missing, parse common TAC validity groups. Missing or bad times fail closed
 * for the active filter (exclude when the filter is on).
 *
 * Window: start inclusive, end exclusive.
 *
 * [Corpus: product] F37
 */

/**
 * Minimal report shape used for validity (avoids import cycles with liveMap).
 *
 * @example
 * const _ = true;
 */
export type ValidityReport = {
  observed_at: string;
  tac: string;
  valid_from?: string | null;
  valid_to?: string | null;
};

/**
 * Minimal place shape used for the active filter.
 *
 * @example
 * const _ = true;
 */
export type ValidityPlace = {
  reports: ValidityReport[];
};

export const LIVE_MAP_FILTER_ACTIVE = 'Active reports';
export const LIVE_MAP_ACTIVE_EMPTY =
  'No active reports in this view. Turn off Active reports to show all.';

/**
 * Inclusive start / exclusive end for one report, or null when unknown.
 *
 * @example
 * const _ = true;
 */
export type ReportValidity = {
  validFromMs: number;
  validToMs: number;
};

const TAF_PERIOD = /\b(\d{2})(\d{2})\/(\d{2})(\d{2})\b/;
const VALID_RANGE = /\bVALID\s+(\d{2})(\d{2})(\d{2})\/(\d{2})(\d{2})(\d{2})\b/i;
const VALID_UNTIL_DDHHMM = /\bVALID\s+UNTIL\s+(\d{2})(\d{2})(\d{2})\b/i;
const VALID_UNTIL_HHMMZ = /\bVALID\s+UNTIL\s+(\d{2})(\d{2})Z?\b/i;

/**
 * Parse an ISO-like stamp to epoch ms, or null when unreadable.
 *
 * @param value - Stamp text
 * @returns Epoch ms, or null
 * @example
 * const _ = true;
 */
export function parseValidityStamp(value: string | null | undefined): number | null {
  if (typeof value !== 'string' || !value.trim()) {
    return null;
  }
  const parsed = Date.parse(value.trim());
  if (!Number.isFinite(parsed)) {
    return null;
  }
  return parsed;
}

/**
 * True when day / hour / minute and the anchor clock are in range.
 *
 * @param day - Day of month (1–31)
 * @param hour - Hour (0–23)
 * @param minute - Minute (0–59)
 * @param anchorMs - Reference observation / issue time
 * @returns Whether the inputs can build a stamp
 */
function isValidDayHourMinute(
  day: number,
  hour: number,
  minute: number,
  anchorMs: number,
): boolean {
  return (
    Number.isFinite(anchorMs) &&
    day >= 1 &&
    day <= 31 &&
    hour >= 0 &&
    hour <= 23 &&
    minute >= 0 &&
    minute <= 59
  );
}

/**
 * Shift year / month when the TAC day wraps across a month boundary.
 *
 * @param day - Day of month from the TAC group
 * @param anchorDay - Day of month from the anchor stamp
 * @param year - Anchor year
 * @param month - Anchor month (0–11)
 * @returns Year and month after the wrap
 */
function yearMonthForTacDay(
  day: number,
  anchorDay: number,
  year: number,
  month: number,
): { year: number; month: number } {
  if (day - anchorDay > 15) {
    if (month === 0) {
      return { year: year - 1, month: 11 };
    }
    return { year, month: month - 1 };
  }
  if (anchorDay - day > 15) {
    if (month === 11) {
      return { year: year + 1, month: 0 };
    }
    return { year, month: month + 1 };
  }
  return { year, month };
}

/**
 * Build a UTC instant from day / hour / minute against an anchor stamp.
 *
 * @param day - Day of month (1–31)
 * @param hour - Hour (0–23)
 * @param minute - Minute (0–59)
 * @param anchorMs - Reference observation / issue time
 * @returns Epoch ms, or null when inputs are out of range
 * @example
 * const _ = true;
 */
export function stampFromDayHourMinute(
  day: number,
  hour: number,
  minute: number,
  anchorMs: number,
): number | null {
  if (!isValidDayHourMinute(day, hour, minute, anchorMs)) {
    return null;
  }
  const anchor = new Date(anchorMs);
  const shifted = yearMonthForTacDay(
    day,
    anchor.getUTCDate(),
    anchor.getUTCFullYear(),
    anchor.getUTCMonth(),
  );
  return Date.UTC(shifted.year, shifted.month, day, hour, minute, 0, 0);
}

/**
 * Keep start before end; null when either side is missing.
 *
 * @param fromMs - Start
 * @param toMs - End
 * @returns Ordered window, or null
 */
function orderedWindow(
  fromMs: number | null,
  toMs: number | null,
): ReportValidity | null {
  if (fromMs === null || toMs === null) {
    return null;
  }
  if (toMs <= fromMs) {
    return null;
  }
  return { validFromMs: fromMs, validToMs: toMs };
}

/**
 * Parse TAF ``ddhh/ddhh`` or SIGMET/AIRMET ``VALID ddhhmm/ddhhmm`` from TAC.
 *
 * @param tac - Raw report text
 * @param observedAt - Issue / observation stamp for month/year
 * @returns Validity window, or null
 * @example
 * const _ = true;
 */
export function validityFromTac(
  tac: string,
  observedAt: string,
): ReportValidity | null {
  const anchor = parseValidityStamp(observedAt);
  if (anchor === null) {
    return null;
  }
  const text = tac.replace(/\s+/g, ' ').trim();
  const range = VALID_RANGE.exec(text);
  if (range) {
    const fromMs = stampFromDayHourMinute(
      Number(range[1]),
      Number(range[2]),
      Number(range[3]),
      anchor,
    );
    const toMs = stampFromDayHourMinute(
      Number(range[4]),
      Number(range[5]),
      Number(range[6]),
      anchor,
    );
    return orderedWindow(fromMs, toMs);
  }
  const untilFull = VALID_UNTIL_DDHHMM.exec(text);
  if (untilFull) {
    const toMs = stampFromDayHourMinute(
      Number(untilFull[1]),
      Number(untilFull[2]),
      Number(untilFull[3]),
      anchor,
    );
    return orderedWindow(anchor, toMs);
  }
  const untilShort = VALID_UNTIL_HHMMZ.exec(text);
  if (untilShort) {
    const day = new Date(anchor).getUTCDate();
    const toMs = stampFromDayHourMinute(
      day,
      Number(untilShort[1]),
      Number(untilShort[2]),
      anchor,
    );
    return orderedWindow(anchor, toMs);
  }
  const taf = TAF_PERIOD.exec(text);
  if (taf) {
    const fromMs = stampFromDayHourMinute(Number(taf[1]), Number(taf[2]), 0, anchor);
    const toMs = stampFromDayHourMinute(Number(taf[3]), Number(taf[4]), 0, anchor);
    return orderedWindow(fromMs, toMs);
  }
  return null;
}

/**
 * Resolve validity from optional payload fields, then TAC.
 *
 * @param report - Cached report
 * @returns Validity window, or null when unknown / malformed
 * @example
 * const _ = true;
 */
export function resolveReportValidity(report: ValidityReport): ReportValidity | null {
  const fromField = parseValidityStamp(report.valid_from);
  const toField = parseValidityStamp(report.valid_to);
  if (fromField !== null && toField !== null) {
    return orderedWindow(fromField, toField);
  }
  if (report.valid_from != null || report.valid_to != null) {
    if (
      (typeof report.valid_from === 'string' && report.valid_from.trim()) ||
      (typeof report.valid_to === 'string' && report.valid_to.trim())
    ) {
      return null;
    }
  }
  return validityFromTac(report.tac, report.observed_at);
}

/**
 * True when ``now`` is inside [validFrom, validTo).
 *
 * @param validity - Window
 * @param nowMs - Clock
 * @returns Whether the report is active
 * @example
 * const _ = true;
 */
export function isReportActiveNow(
  validity: ReportValidity,
  nowMs = Date.now(),
): boolean {
  return nowMs >= validity.validFromMs && nowMs < validity.validToMs;
}

/**
 * True when the newest report on the place is active now.
 *
 * Missing validity → false (fail closed for the active filter).
 *
 * @param place - Place with reports
 * @param nowMs - Clock
 * @returns Whether the place stays when Active reports is on
 * @example
 * const _ = true;
 */
export function placeIsActiveNow(place: ValidityPlace, nowMs = Date.now()): boolean {
  const newest = place.reports[0];
  if (!newest) {
    return false;
  }
  const validity = resolveReportValidity(newest);
  if (!validity) {
    return false;
  }
  return isReportActiveNow(validity, nowMs);
}

/**
 * Default Active reports switch: on when any loaded report has a validity window.
 *
 * @param places - Places in the current view
 * @returns Default switch value
 * @example
 * const _ = true;
 */
export function defaultActiveReportsOn(places: readonly ValidityPlace[]): boolean {
  return places.some((place) =>
    place.reports.some((report) => resolveReportValidity(report) !== null),
  );
}

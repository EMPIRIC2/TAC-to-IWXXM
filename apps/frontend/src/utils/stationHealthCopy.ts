/**
 * Plain-language copy for the Station health shell tab.
 */

export const STATION_HEALTH_PAGE_TITLE = 'Station health';
export const STATION_HEALTH_INTRO =
  'Availability and quality grades for stations that send TAC reports. Grades cover the last 6 hours, 1 day, 1 month, and 3 months. Counts include maintenance tags, file formats, and lint or validation issue identifiers. Centennial recognition proxies use live data when available, or show insufficient data.';
export const STATION_HEALTH_LOADING = 'Loading station health…';
export const STATION_HEALTH_LOAD_ERROR =
  'Station health could not be loaded. Try again later.';
export const STATION_HEALTH_EMPTY =
  'No station grades yet. Grades appear after ingest or convert records arrive.';
export const STATION_HEALTH_WINDOW_LABEL = 'Time window';
export const STATION_HEALTH_PRODUCT_LABEL = 'Product';
export const STATION_HEALTH_GRADE_LABEL = 'Grade';
export const STATION_HEALTH_REGION_LABEL = 'WMO region';
export const STATION_HEALTH_FILTER_ALL = 'All';
export const STATION_HEALTH_UNKNOWN_REGION = 'Unknown region';
export const STATION_HEALTH_COL_STATION = 'Station';
export const STATION_HEALTH_COL_REGION = 'WMO region';
export const STATION_HEALTH_COL_GRADE = 'Grade';
export const STATION_HEALTH_COL_AVAILABILITY = 'Availability';
export const STATION_HEALTH_COL_SOLIDUS = 'Solidus rate';
export const STATION_HEALTH_COL_MISSING = 'Missing digits';
export const STATION_HEALTH_COL_LINT = 'Lint severity';
export const STATION_HEALTH_COL_PRODUCTS = 'Products';
export const STATION_HEALTH_COL_MAINTENANCE = 'Maintenance tags';
export const STATION_HEALTH_COL_FORMATS = 'Formats';
export const STATION_HEALTH_COL_ISSUES = 'Issue ids';
export const STATION_HEALTH_COL_CENTENNIAL = 'Centennial proxies';
export const STATION_HEALTH_METRICS_HEADING = 'Metrics';
export const STATION_HEALTH_SUMMARY_HEADING = 'Summary';
export const STATION_HEALTH_SCORE_HELP_HEADING = 'How grades are built';
export const STATION_HEALTH_SCORE_HELP =
  'Numbers below use the time window you selected. Availability is the share of expected reports received. Solidus rate and missing-digit rate measure incomplete TAC groups. Lint severity scores stored lint errors and warnings (higher is better). The letter grade blends those parts: availability 50 percent, solidus quality 25 percent, missing-digit quality 15 percent, and lint severity 10 percent. Maintenance tags, formats, and issue ids are counts for the same window. Centennial proxies use live data when possible; otherwise they show insufficient data. WMO region is a location group, not a score.';
export const STATION_HEALTH_INSUFFICIENT = 'Insufficient data';
export const STATION_HEALTH_NONE = 'None';
export const STATION_HEALTH_NA = '-';

/** Operator labels for WMO Regional Association ids. */
export const STATION_HEALTH_REGION_OPTIONS: ReadonlyArray<{
  value: string;
  label: string;
}> = [
  { value: 'I', label: 'Region I - Africa' },
  { value: 'II', label: 'Region II - Asia' },
  { value: 'III', label: 'Region III - South America' },
  {
    value: 'IV',
    label: 'Region IV - North America, Central America and the Caribbean',
  },
  { value: 'V', label: 'Region V - South-West Pacific' },
  { value: 'VI', label: 'Region VI - Europe' },
  { value: 'unknown', label: STATION_HEALTH_UNKNOWN_REGION },
];

/**
 * Format a WMO region id for table display.
 *
 * @param region - Region id from the API
 * @returns Plain-language label
 * @example
 * const _ = true;
 */
export function formatStationHealthRegion(region: string | null | undefined): string {
  const key = (region ?? '').trim() || 'unknown';
  const match = STATION_HEALTH_REGION_OPTIONS.find((row) => row.value === key);
  return match?.label ?? STATION_HEALTH_UNKNOWN_REGION;
}

/**
 * Format a count map as compact operator text.
 *
 * @param counts - Tag or format counts
 * @returns Display string
 * @example
 * const _ = true;
 */
export function formatCountMap(
  counts: Record<string, number> | null | undefined,
): string {
  if (!counts) {
    return STATION_HEALTH_NONE;
  }
  const entries = Object.entries(counts).filter(([, value]) => value > 0);
  if (entries.length === 0) {
    return STATION_HEALTH_NONE;
  }
  return entries.map(([key, value]) => `${key} ${value}`).join(', ');
}

/**
 * Format a numeric component for the selected window, or a dash when missing.
 *
 * @param value - Score or rate
 * @param digits - Fraction digits
 * @returns Display string
 * @example
 * const _ = true;
 */
export function formatComponentScore(
  value: number | null | undefined,
  digits = 1,
): string {
  if (value == null || Number.isNaN(value)) {
    return STATION_HEALTH_NA;
  }
  return value.toFixed(digits);
}

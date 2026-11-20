/** Live map operator-visible string constants. */

/**
 * LIVE_MAP_NOTICE.
 */
export const LIVE_MAP_NOTICE =
  'These reports are not validated for operational use. They come from the Aviation Weather Center.';

/**
 * LIVE_MAP_CANVAS.
 */
export const LIVE_MAP_CANVAS = 'Live weather map';
/**
 * LIVE_MAP_ZOOM_HINT.
 */
export const LIVE_MAP_ZOOM_HINT =
  'Open a point or outlined area to load it above. The map shows the station and the report.';

/**
 * LIVE_MAP_LOADING.
 */
export const LIVE_MAP_LOADING = 'Loading reports for this view.';
/**
 * LIVE_MAP_REFRESHING.
 */
export const LIVE_MAP_REFRESHING = 'Refreshing this view.';
/**
 * LIVE_MAP_EMPTY.
 */
export const LIVE_MAP_EMPTY = 'No reports in this view.';
/**
 * LIVE_MAP_NO_TIME.
 */
export const LIVE_MAP_NO_TIME = 'Reports in this view have no observation time.';
/**
 * LIVE_MAP_LAYERS_OFF.
 */
export const LIVE_MAP_LAYERS_OFF = 'Turn a layer on to see reports.';
/**
 * LIVE_MAP_SPACE.
 */
export const LIVE_MAP_SPACE = 'Space weather has no map location.';
/**
 * LIVE_MAP_ERROR.
 */
export const LIVE_MAP_ERROR = 'The live map could not be loaded.';
/**
 * LIVE_MAP_PENDING.
 */
export const LIVE_MAP_PENDING = 'Translation is pending.';
/**
 * LIVE_MAP_AREA.
 */
export const LIVE_MAP_AREA = 'Area';
/**
 * LIVE_MAP_LATEST.
 */
export const LIVE_MAP_LATEST = 'Latest';
/**
 * LIVE_MAP_IWXXM.
 */
export const LIVE_MAP_IWXXM = 'IWXXM';
/**
 * LIVE_MAP_TAC.
 */
export const LIVE_MAP_TAC = 'TAC';
/**
 * LIVE_MAP_SEND_TO_CONVERTER.
 */
export const LIVE_MAP_SEND_TO_CONVERTER = 'Send to converter';
/**
 * LIVE_MAP_ISSUE_COPY.
 */
export const LIVE_MAP_ISSUE_COPY = 'Observation time';
/**
 * LIVE_MAP_ALL_COUNTRIES.
 */
export const LIVE_MAP_ALL_COUNTRIES = 'All countries';
/**
 * LIVE_MAP_ALL_REGIONS.
 */
export const LIVE_MAP_ALL_REGIONS = 'All regions';
/**
 * LIVE_MAP_LAST_HOUR.
 */
export const LIVE_MAP_LAST_HOUR = 'Last hour';
/**
 * LIVE_MAP_LAST_3_HOURS.
 */
export const LIVE_MAP_LAST_3_HOURS = 'Last 3 hours';
/**
 * LIVE_MAP_LAST_6_HOURS.
 */
export const LIVE_MAP_LAST_6_HOURS = 'Last 6 hours';
/**
 * LIVE_MAP_LAST_12_HOURS.
 */
export const LIVE_MAP_LAST_12_HOURS = 'Last 12 hours';
/**
 * LIVE_MAP_FULL_WINDOW.
 */
export const LIVE_MAP_FULL_WINDOW = 'Full';
/**
 * LIVE_MAP_FILTER_COUNTRY.
 */
export const LIVE_MAP_FILTER_COUNTRY = 'Country';
/**
 * LIVE_MAP_FILTER_REGION.
 */
export const LIVE_MAP_FILTER_REGION = 'Region';
/**
 * LIVE_MAP_FILTER_TIME.
 */
export const LIVE_MAP_FILTER_TIME = 'Issue time';
/**
 * LIVE_MAP_FILTER_PHENOMENON.
 */
export const LIVE_MAP_FILTER_PHENOMENON = 'Phenomenon';

/**
 * LIVE_MAP_PHENOMENA.
 */
export const LIVE_MAP_PHENOMENA = [
  { id: 'ifr', label: 'IFR' },
  { id: 'turb', label: 'Turbulence' },
  { id: 'ice', label: 'Icing' },
  { id: 'ts', label: 'Thunderstorms' },
] as const;

/**
 * How far back the loaded view keeps reports. `full` is the shared 24-hour set.
 * @example
 * const _ = true;
 */
export type { MapTimePreset } from '@/models/liveMap';
/**
 * LIVE_MAP_DECODE.
 */
export const LIVE_MAP_DECODE = 'Decode';
/**
 * LIVE_MAP_PANEL.
 */
export const LIVE_MAP_PANEL = 'Weather map';
/**
 * LIVE_MAP_REFRESH_MS.
 */
export const LIVE_MAP_REFRESH_MS = 60_000;

/** Canvas padding. Shapes bring their own slack, so this stays at zero. */
/**
 * LIVE_MAP_CANVAS_TOLERANCE.
 */
export const LIVE_MAP_CANVAS_TOLERANCE = 0;

/**
 * Extra pixels on a station dot.
 *
 * The dot radius is 6, so the pointer target is 24 pixels across.
 */
/**
 * LIVE_MAP_POINT_SLACK.
 */
export const LIVE_MAP_POINT_SLACK = 6;

/**
 * Pixels from a line, polygon edge, or circle outline that still count.
 *
 * The band is 24 pixels thick.
 */
/**
 * LIVE_MAP_EDGE_SLACK.
 */
export const LIVE_MAP_EDGE_SLACK = 12;

/**
 * Pointer slack for one drawn shape.
 *
 * A station dot stays a small target. A line, polygon, or circle uses a band
 * along its edge so the shaded inside does not take the pointer.
 *
 * @param kind - Point, line, polygon, or circle
 * @returns Slack in pixels
 * @example
 * const _ = true;
 */

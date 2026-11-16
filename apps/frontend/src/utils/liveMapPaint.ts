/**
 * Live map geometry, paint, and filter helpers.
 */
import type { LivePlace } from '@/models/liveMap';
import {
  LIVE_MAP_AREA,
  LIVE_MAP_EDGE_SLACK,
  LIVE_MAP_EMPTY,
  LIVE_MAP_LOADING,
  LIVE_MAP_NO_TIME,
  LIVE_MAP_POINT_SLACK,
  LIVE_MAP_REFRESHING,
} from './liveMapCopy';

/**
 * pointerSlack.
 */
export function pointerSlack(kind: 'point' | 'line' | 'polygon' | 'circle'): number {
  if (kind === 'point') {
    return LIVE_MAP_POINT_SLACK;
  }
  return LIVE_MAP_EDGE_SLACK;
}

const PRODUCT_LABELS: Record<string, string> = {
  metar: 'METAR',
  speci: 'SPECI',
  taf: 'TAF',
  airmet: 'AIRMET',
  gairmet: 'G-AIRMET',
  sigmet: 'SIGMET',
  vaa: 'Volcanic ash',
  tca: 'Tropical cyclone',
  vona: 'Volcano notice',
};

const PRODUCT_COLORS: Record<string, string> = {
  metar: '#1d4ed8',
  speci: '#0369a1',
  taf: '#0f766e',
  airmet: '#c2410c',
  gairmet: '#a16207',
  sigmet: '#b91c1c',
  vaa: '#6d28d9',
  tca: '#be185d',
  vona: '#4338ca',
};

/** Cyan for the space-weather list when that list has rows. Not a map pin. */
/**
 * SPACE_WEATHER_LIST_COLOR.
 */
export const SPACE_WEATHER_LIST_COLOR = '#0e7490';

const MONTHS = [
  'Jan',
  'Feb',
  'Mar',
  'Apr',
  'May',
  'Jun',
  'Jul',
  'Aug',
  'Sep',
  'Oct',
  'Nov',
  'Dec',
];

/**
 * Plain name for a map layer.
 *
 * @param product - Layer id
 * @returns Operator label
 * @example
 * const _ = true;
 */
/**
 * productLabel.
 */
export function productLabel(product: string): string {
  return PRODUCT_LABELS[product] ?? product.toUpperCase();
}

/**
 * Pin color for one product.
 *
 * @param product - Layer id
 * @returns CSS color
 * @example
 * const _ = true;
 */
/**
 * pinColor.
 */
export function pinColor(product: string): string {
  return PRODUCT_COLORS[product] ?? '#1d4ed8';
}

/**
 * Fill and outline for a product shape. The outline stays white so it is not the fill.
 *
 * @param product - Layer id
 * @returns Leaflet path options
 * @example
 * const _ = true;
 */
/**
 * shapePaint.
 */
export function shapePaint(product: string): {
  color: string;
  weight: number;
  fillColor: string;
  fillOpacity: number;
} {
  return {
    color: '#ffffff',
    weight: 2,
    fillColor: pinColor(product),
    fillOpacity: 0.45,
  };
}

/**
 * List color when space-weather rows exist. An empty list keeps the surrounding text color.
 *
 * @param rowCount - Rows in the side list
 * @returns Cyan, or undefined when the list is empty
 * @example
 * const _ = true;
 */
/**
 * spaceWeatherListColor.
 */
export function spaceWeatherListColor(rowCount: number): string | undefined {
  if (rowCount > 0) {
    return SPACE_WEATHER_LIST_COLOR;
  }
  return undefined;
}

/**
 * Place name, or Area when the key is not an airport identifier.
 *
 * @param placeKey - Station or area id
 * @param airportName - Known airport name
 * @returns Name to show
 * @example
 * const _ = true;
 */
/**
 * placeTitle.
 */
export function placeTitle(placeKey: string, airportName: string | undefined): string {
  if (/^[A-Z][A-Z0-9]{3}$/.test(placeKey)) {
    return airportName ?? placeKey;
  }
  return LIVE_MAP_AREA;
}

/**
 * Clock time in UTC, or the original text when it is not a time.
 *
 * @param value - Observation stamp
 * @returns Readable UTC time
 * @example
 * const _ = true;
 */
/**
 * formatObservedAt.
 */
export function formatObservedAt(value: string): string {
  const parsed = Date.parse(value);
  if (Number.isNaN(parsed)) {
    return value;
  }
  const date = new Date(parsed);
  const day = String(date.getUTCDate()).padStart(2, '0');
  const hours = String(date.getUTCHours()).padStart(2, '0');
  const minutes = String(date.getUTCMinutes()).padStart(2, '0');
  return `${day} ${MONTHS[date.getUTCMonth()]} ${hours}:${minutes} UTC`;
}

/**
 * How long ago an observation was.
 *
 * @param value - Observation stamp
 * @param now - Clock to compare
 * @returns Short age, or an empty string when the stamp is not a time
 * @example
 * const _ = true;
 */
/**
 * observationAge.
 */
export function observationAge(value: string, now = Date.now()): string {
  const parsed = Date.parse(value);
  if (Number.isNaN(parsed)) {
    return '';
  }
  const minutes = Math.max(0, Math.round((now - parsed) / 60_000));
  if (minutes < 1) {
    return 'just now';
  }
  if (minutes === 1) {
    return '1 min ago';
  }
  if (minutes < 60) {
    return `${minutes} min ago`;
  }
  const hours = Math.round(minutes / 60);
  if (hours === 1) {
    return '1 hour ago';
  }
  if (hours < 48) {
    return `${hours} hours ago`;
  }
  return `${Math.round(hours / 24)} days ago`;
}

/**
 * Latest observation stamp in the loaded places.
 *
 * @param places - Places in the current view
 * @returns Stamp, or null when none parse
 * @example
 * const _ = true;
 */
/**
 * newestObservedAt.
 */
export function newestObservedAt(places: LivePlace[]): string | null {
  let best: string | null = null;
  let bestMs = Number.NEGATIVE_INFINITY;
  for (const place of places) {
    for (const report of place.reports) {
      const parsed = Date.parse(report.observed_at);
      if (!Number.isNaN(parsed) && parsed > bestMs) {
        bestMs = parsed;
        best = report.observed_at;
      }
    }
  }
  return best;
}

/**
 * One line that says whether the view is loading, empty, or current.
 *
 * @param places - Places in the current view
 * @param loading - True before the first response
 * @param refreshing - True while a later response is on the way
 * @param now - Clock for the age
 * @returns Status sentence
 * @example
 * const _ = true;
 */
/**
 * viewStatus.
 */
export function viewStatus(
  places: LivePlace[],
  loading: boolean,
  refreshing: boolean,
  now = Date.now(),
): string {
  if (loading) {
    return LIVE_MAP_LOADING;
  }
  if (refreshing) {
    return LIVE_MAP_REFRESHING;
  }
  if (places.length === 0) {
    return LIVE_MAP_EMPTY;
  }
  const newest = newestObservedAt(places);
  if (!newest) {
    return LIVE_MAP_NO_TIME;
  }
  return `Newest observation in this view: ${formatObservedAt(newest)} (${observationAge(newest, now)}).`;
}

/**
 * Popup width that stays on a narrow screen.
 *
 * @param viewWidth - Map width in pixels
 * @returns Popup width
 * @example
 * const _ = true;
 */
/**
 * popupWidth.
 */
export function popupWidth(viewWidth: number): number {
  return Math.min(320, Math.max(180, viewWidth - 32));
}

/**
 * Side-by-side card on a wide map, stacked on a narrow one.
 *
 * @param viewWidth - Map width in pixels
 * @returns Card layout
 * @example
 * const _ = true;
 */
/**
 * cardLayout.
 */
export function cardLayout(viewWidth: number): 'side' | 'stack' {
  if (viewWidth >= 768) {
    return 'side';
  }
  return 'stack';
}

/**
 * Opacity for one stored copy. The newest is solid. Earlier copies fade.
 *
 * @param index - 0 is the newest report
 * @returns Fill opacity
 * @example
 * const _ = true;
 */
/**
 * copyOpacity.
 */
export function copyOpacity(index: number): number {
  if (index <= 0) {
    return 1;
  }
  if (index === 1) {
    return 0.45;
  }
  return 0.25;
}

/**
 * Shift co-located airport dots sideways so each one stays clickable.
 *
 * @param slot - Index among dots at the same airport
 * @param total - How many dots share that airport
 * @returns Latitude and longitude deltas in degrees
 * @example
 * const _ = true;
 */
/**
 * pointNudge.
 */
export function pointNudge(
  slot: number,
  total: number,
): { latitude: number; longitude: number } {
  if (total < 2) {
    return { latitude: 0, longitude: 0 };
  }
  const step = 0.08;
  return {
    latitude: 0,
    longitude: (slot - (total - 1) / 2) * step,
  };
}

/**
 * Longitude offsets for Leaflet world copies when tiles wrap (±360°).
 *
 * Vector layers project once; tiles repeat. Paint the same overlay at these
 * offsets so SIGMET polygons and station markers appear on looped globe copies.
 */
/**
 * WORLD_COPY_LNG_OFFSETS.
 */
export const WORLD_COPY_LNG_OFFSETS = [-360, 0, 360] as const;

/**
 * Shift a point by a world-copy longitude offset.
 *
 * @param latitude - Degrees north
 * @param longitude - Degrees east on the primary copy
 * @param lngOffset - Degrees to add (−360, 0, or 360)
 * @returns Latitude and shifted longitude
 * @example
 * const _ = true;
 */
/**
 * shiftLatLng.
 */
export function shiftLatLng(
  latitude: number,
  longitude: number,
  lngOffset: number,
): [number, number] {
  return [latitude, longitude + lngOffset];
}

/**
 * Shift every vertex of a line or polygon by a world-copy longitude offset.
 *
 * @param positions - Latitude/longitude pairs on the primary copy
 * @param lngOffset - Degrees to add (−360, 0, or 360)
 * @returns Positions on that world copy
 * @example
 * const _ = true;
 */
/**
 * shiftPositions.
 */
export function shiftPositions(
  positions: [number, number][],
  lngOffset: number,
): [number, number][] {
  return positions.map(([latitude, longitude]) => [latitude, longitude + lngOffset]);
}

/**
 * Move the report the card is showing to the front of the list.
 *
 * @param place - Cached place
 * @param tac - TAC text on the card
 * @returns Place whose first report is that copy
 * @example
 * const _ = true;
 */
/**
 * placeShowingReport.
 */
export function placeShowingReport(place: LivePlace, tac: string): LivePlace {
  const chosen = place.reports.find((report) => report.tac === tac);
  if (!chosen || place.reports[0] === chosen) {
    return place;
  }
  return {
    ...place,
    reports: [chosen, ...place.reports.filter((report) => report !== chosen)],
  };
}

/**
 * Keep places that pass the country, region, time, and phenomenon choices.
 *
 * @param places - Places already loaded for the view
 * @param filters - Current choices. Country and region use `all` for no narrowing
 * @returns Places still drawn
 * @example
 * const _ = true;
 */

/**
 * Live map views, wind text, and the cache read.
 */

import { apiUrl } from '@/utils/apiBase';

/**
 * One stored report.
 * @example
 * const _ = true;
 */
export type LiveReport = {
  observed_at: string;
  tac: string;
  iwxxm?: string | null;
  issues?: string[];
};

/**
 * Shape drawn for one place.
 * @example
 * const _ = true;
 */
export type LiveGeometry = {
  kind: 'point' | 'polygon' | 'line' | 'circle';
  coordinates?: [number, number][];
  radius_m?: number;
};

/**
 * One place returned for the current map view.
 * @example
 * const _ = true;
 */
export type LivePlace = {
  place_key: string;
  product: string;
  latitude: number;
  longitude: number;
  geometry?: LiveGeometry;
  reports: LiveReport[];
};

/**
 * Map edges in degrees.
 * @example
 * const _ = true;
 */
export const LIVE_MAP_NOTICE =
  'These reports are not validated for operational use. They come from the Aviation Weather Center.';

export const LIVE_MAP_CANVAS = 'Live weather map';
export const LIVE_MAP_ZOOM_HINT =
  'Zoom in to go from continents to regions to each station. The number is how many current reports are in that area.';

export const LIVE_MAP_LOADING = 'Loading reports for this view.';
export const LIVE_MAP_REFRESHING = 'Refreshing this view.';
export const LIVE_MAP_EMPTY = 'No reports in this view.';
export const LIVE_MAP_NO_TIME = 'Reports in this view have no observation time.';
export const LIVE_MAP_LAYERS_OFF = 'Turn a layer on to see reports.';
export const LIVE_MAP_SPACE = 'Space weather has no map location.';
export const LIVE_MAP_ERROR = 'The live map could not be loaded.';
export const LIVE_MAP_PENDING = 'Translation is pending.';
export const LIVE_MAP_AREA = 'Area';
export const LIVE_MAP_LATEST = 'Latest';
export const LIVE_MAP_IWXXM = 'IWXXM';
export const LIVE_MAP_REFRESH_MS = 60_000;

const PRODUCT_LABELS: Record<string, string> = {
  metar: 'METAR',
  speci: 'SPECI',
  taf: 'TAF',
  airmet: 'AIRMET',
  sigmet: 'SIGMET',
  vaa: 'Volcanic ash',
  tca: 'Tropical cyclone',
  vona: 'Volcano notice',
};

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
export function productLabel(product: string): string {
  return PRODUCT_LABELS[product] ?? product.toUpperCase();
}

/**
 * Pin color for a product family.
 *
 * @param product - Layer id
 * @returns CSS color
 * @example
 * const _ = true;
 */
export function pinColor(product: string): string {
  if (product === 'taf') {
    return '#0f766e';
  }
  if (product === 'airmet' || product === 'sigmet') {
    return '#c2410c';
  }
  if (product === 'vaa' || product === 'tca' || product === 'vona') {
    return '#6d28d9';
  }
  return '#1d4ed8';
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
export function popupWidth(viewWidth: number): number {
  return Math.min(320, Math.max(180, viewWidth - 32));
}

export type MapBounds = {
  west: number;
  south: number;
  east: number;
  north: number;
};

/**
 * Read the edges of a Leaflet map.
 *
 * @param map - Map with a geographic bounds box
 * @returns West, south, east, and north
 * @example
 * const _ = true;
 */
export function boundsOf(map: {
  getBounds: () => {
    getWest: () => number;
    getSouth: () => number;
    getEast: () => number;
    getNorth: () => number;
  };
}): MapBounds {
  const box = map.getBounds();
  let west = box.getWest();
  let east = box.getEast();
  const south = Math.min(90, Math.max(-90, box.getSouth()));
  const north = Math.min(90, Math.max(-90, box.getNorth()));
  if (west < -180 || east > 180 || east - west >= 360) {
    west = -180;
    east = 180;
  }
  return { west, south, east, north };
}

/**
 * Named views. Observations is the one that starts on.
 * @example
 * const _ = true;
 */
export const LIVE_MAP_VIEWS = [
  { id: 'observations', label: 'Observations', products: ['metar', 'speci'] },
  { id: 'forecasts', label: 'Forecasts', products: ['taf'] },
  { id: 'hazards', label: 'Hazards', products: ['airmet', 'sigmet'] },
  { id: 'advisories', label: 'Advisories', products: ['vaa', 'tca', 'vona'] },
] as const;

const PRODUCT_FORM: Record<string, string> = {
  metar: 'METAR',
  speci: 'SPECI',
  taf: 'TAF',
  airmet: 'AIRMET',
  sigmet: 'SIGMET',
  vaa: 'VAA',
  tca: 'TCA',
  vona: 'VONA',
};

/**
 * The named view, or Observations when the id is unknown.
 *
 * @param viewId - View id
 * @returns View definition
 * @example
 * const _ = true;
 */
export function viewById(viewId: string): (typeof LIVE_MAP_VIEWS)[number] {
  return LIVE_MAP_VIEWS.find((item) => item.id === viewId) ?? LIVE_MAP_VIEWS[0];
}

/**
 * Products still switched on for a view.
 *
 * @param viewId - View id, or anything else for Observations
 * @param off - Layer ids the operator turned off
 * @returns Comma-separated products, or an empty string when every layer is off
 * @example
 * const _ = true;
 */
export function layerQuery(viewId: string, off: ReadonlySet<string>): string {
  return viewById(viewId)
    .products.filter((product) => !off.has(product))
    .join(',');
}

/**
 * Every geographically located layer, in view order.
 * @example
 * const _ = true;
 */
export const LIVE_MAP_PRODUCTS = LIVE_MAP_VIEWS.flatMap((item) => [...item.products]);

/**
 * Layers still switched on. All of them start on.
 *
 * @param off - Layer ids the operator turned off
 * @returns Comma-separated products, or an empty string when every layer is off
 * @example
 * const _ = true;
 */
export function selectedLayerQuery(off: ReadonlySet<string>): string {
  return LIVE_MAP_PRODUCTS.filter((product) => !off.has(product)).join(',');
}

/**
 * A short wind sentence from a TAC wind group.
 *
 * @param tac - Raw report
 * @returns Wind sentence, or a note when the group is missing
 * @example
 * const _ = true;
 */
export function windFromTac(tac: string): string {
  const match = tac.match(/\b(VRB|\d{3})(\d{2,3})KT\b/);
  if (!match) {
    return 'No wind group in this report.';
  }
  const speed = Number(match[2]);
  if (match[1] === 'VRB') {
    return `Variable wind at ${speed} knots.`;
  }
  return `Wind from ${Number(match[1])} degrees at ${speed} knots.`;
}

/**
 * Keep rows that have a place, a product, coordinates, and a report list.
 *
 * @param value - One JSON row
 * @returns Whether the row can be drawn
 * @example
 * const _ = true;
 */
function isLivePlace(value: unknown): value is LivePlace {
  if (!value || typeof value !== 'object') {
    return false;
  }
  const row = value as Partial<LivePlace>;
  return (
    typeof row.place_key === 'string' &&
    typeof row.product === 'string' &&
    typeof row.latitude === 'number' &&
    typeof row.longitude === 'number' &&
    Array.isArray(row.reports)
  );
}

/**
 * Cached reports for a map box.
 *
 * @param bounds - Edges of the view
 * @param products - Comma-separated layers
 * @param signal - Cancel when the view changes
 * @returns Places with coordinates
 * @example
 * const _ = true;
 */
export async function fetchLivePlaces(
  bounds: MapBounds,
  products: string,
  signal: AbortSignal,
): Promise<LivePlace[]> {
  const params = new URLSearchParams({
    west: String(bounds.west),
    south: String(bounds.south),
    east: String(bounds.east),
    north: String(bounds.north),
    products,
  });
  const response = await fetch(apiUrl(`/api/v1/live-map?${params.toString()}`), {
    signal,
  });
  if (!response.ok) {
    throw new Error('The live map could not be loaded.');
  }
  const body = (await response.json()) as { places?: unknown };
  if (!Array.isArray(body.places)) {
    return [];
  }
  return body.places.filter(isLivePlace).map((place) => ({
    ...place,
    reports: place.reports.filter(
      (report) =>
        typeof report?.tac === 'string' && typeof report.observed_at === 'string',
    ),
  }));
}

/**
 * IWXXM for one cached report, using this app's conversion.
 *
 * @param tac - Raw report
 * @param product - Map layer id
 * @param signal - Cancel when another report is opened
 * @returns XML text
 * @example
 * const _ = true;
 */
export async function iwxxmForReport(
  tac: string,
  product: string,
  signal: AbortSignal,
): Promise<string> {
  const body = new FormData();
  body.set('manual_text', tac);
  body.set('product', PRODUCT_FORM[product] ?? 'METAR');
  body.set('validate_output', 'false');
  const response = await fetch(apiUrl('/api/v1/convert'), {
    method: 'POST',
    body,
    signal,
  });
  if (!response.ok) {
    throw new Error('IWXXM is not available for this report.');
  }
  const payload = (await response.json()) as { results?: { content?: string }[] };
  const xml = payload.results?.[0]?.content;
  if (!xml) {
    throw new Error('IWXXM is not available for this report.');
  }
  return xml;
}

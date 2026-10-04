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

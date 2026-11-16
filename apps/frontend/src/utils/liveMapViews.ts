/**
 * Live map views, bounds, and network fetch.
 */
import { apiUrl } from '@/utils/apiBase';
import type { LivePlace, MapBounds } from '@/models/liveMap';

export type { MapBounds } from '@/models/liveMap';

/**
 * World box used when Leaflet reports a collapsed or inverted view
 * (common on first paint before the map host has a non-zero size).
 * @example
 * const _ = true;
 */
/**
 * DEFAULT_LIVE_MAP_BOUNDS.
 */
export const DEFAULT_LIVE_MAP_BOUNDS: MapBounds = {
  west: -180,
  south: -80,
  east: 180,
  north: 80,
};

/**
 * Whether west is left of east and south is below north (positive area).
 *
 * @param bounds - Candidate edges
 * @returns True when the API will accept the box
 * @example
 * const _ = true;
 */
/**
 * isUsableMapBounds.
 */
export function isUsableMapBounds(bounds: MapBounds): boolean {
  return bounds.west < bounds.east && bounds.south < bounds.north;
}

/**
 * Keep a positive-area box; otherwise use the default world view.
 *
 * @param bounds - Candidate edges
 * @returns Edges safe to send to `/api/v1/live-map`
 * @example
 * const _ = true;
 */
/**
 * sanitizeMapBounds.
 */
export function sanitizeMapBounds(bounds: MapBounds): MapBounds {
  return isUsableMapBounds(bounds) ? bounds : DEFAULT_LIVE_MAP_BOUNDS;
}

/**
 * Read the edges of a Leaflet map.
 *
 * @param map - Map with a geographic bounds box
 * @returns West, south, east, and north (never a zero-area box)
 * @example
 * const _ = true;
 */
/**
 * boundsOf.
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
  return sanitizeMapBounds({ west, south, east, north });
}

/**
 * Named views. Observations is the one that starts on.
 * @example
 * const _ = true;
 */
/**
 * LIVE_MAP_VIEWS.
 */
export const LIVE_MAP_VIEWS = [
  { id: 'observations', label: 'Observations', products: ['metar', 'speci'] },
  { id: 'forecasts', label: 'Forecasts', products: ['taf'] },
  { id: 'hazards', label: 'Hazards', products: ['airmet', 'gairmet', 'sigmet'] },
  { id: 'advisories', label: 'Advisories', products: ['vaa', 'tca', 'vona'] },
] as const;

const PRODUCT_FORM: Record<string, string> = {
  metar: 'METAR',
  speci: 'SPECI',
  taf: 'TAF',
  airmet: 'AIRMET',
  gairmet: 'AIRMET',
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
/**
 * viewById.
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
/**
 * layerQuery.
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
/**
 * LIVE_MAP_PRODUCTS.
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
/**
 * selectedLayerQuery.
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
/**
 * windFromTac.
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
/**
 * fetchLivePlaces.
 */
export async function fetchLivePlaces(
  bounds: MapBounds,
  products: string,
  signal: AbortSignal,
): Promise<LivePlace[]> {
  const box = sanitizeMapBounds(bounds);
  const params = new URLSearchParams({
    west: String(box.west),
    south: String(box.south),
    east: String(box.east),
    north: String(box.north),
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
/**
 * iwxxmForReport.
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

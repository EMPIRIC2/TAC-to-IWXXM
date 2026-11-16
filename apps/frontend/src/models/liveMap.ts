/** Live map place/report/geometry wire shapes. */

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
  valid_from?: string | null;
  valid_to?: string | null;
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

export type MapTimePreset = '1h' | '3h' | '6h' | '12h' | 'full';

/**
 * Geographic edges of the current map view.
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
 * World box used when Leaflet reports a collapsed or inverted view
 * (common on first paint before the map host has a non-zero size).
 * @example
 * const _ = true;
 */

/**
 * Station coordinate lookup and map binding (F7 / F9).
 */

import L from 'leaflet';
import { apiUrl } from '@/utils/apiBase';

/**
 * Type `StationPoint`.
 * @example
 * const _ = true;
 */
export type StationPoint = {
  icao: string;
  name: string;
  latitude: number;
  longitude: number;
};

/**
 * One station from the airport lookup, or null when the code is unknown.
 *
 * @param icao - Four-letter station ID
 * @param signal - Cancel the request when the ID changes
 * @returns Coordinates, or null on a miss
 * @example
 * const _ = true;
 */
export async function fetchStationPoint(
  icao: string,
  signal: AbortSignal,
): Promise<StationPoint | null> {
  const response = await fetch(apiUrl(`/api/v1/stations/${icao}`), { signal });
  if (response.status === 404) {
    return null;
  }
  if (!response.ok) {
    throw new Error('Station lookup failed');
  }
  const body = (await response.json()) as Partial<StationPoint>;
  if (typeof body.latitude !== 'number' || typeof body.longitude !== 'number') {
    return null;
  }
  return {
    icao,
    name: typeof body.name === 'string' && body.name.trim() ? body.name : icao,
    latitude: body.latitude,
    longitude: body.longitude,
  };
}

/**
 * Attach a tile map and marker to a host element.
 *
 * @param node - Map container
 * @param point - Station coordinates
 * @returns Cleanup that removes the map
 * @example
 * const _ = true;
 */
export function bindStationMap(
  node: HTMLDivElement | null,
  point: StationPoint | null | undefined,
): (() => void) | undefined {
  if (!point || !node) {
    return undefined;
  }
  const map = L.map(node, { scrollWheelZoom: true }).setView(
    [point.latitude, point.longitude],
    8,
  );
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap',
    maxZoom: 16,
  }).addTo(map);
  const icon = L.divIcon({
    className: '',
    html: '<span data-testid="station-map-blip" style="display:block;width:14px;height:14px;border-radius:9999px;background:#0369a1;border:2px solid #ffffff"></span>',
    iconSize: [14, 14],
    iconAnchor: [7, 7],
  });
  L.marker([point.latitude, point.longitude], { icon }).addTo(map);
  return () => {
    map.remove();
  };
}

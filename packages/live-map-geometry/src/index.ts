/**
 * Choose how one cached place is drawn. The app paints the result.
 */

export type MapDraw =
  | { kind: 'point'; latitude: number; longitude: number }
  | { kind: 'line'; positions: [number, number][] }
  | { kind: 'polygon'; positions: [number, number][] }
  | { kind: 'circle'; latitude: number; longitude: number; radiusM: number };

export type MapGeometryInput = {
  latitude: number;
  longitude: number;
  geometry?: {
    kind?: string;
    coordinates?: readonly [number, number][];
    radius_m?: number;
  };
};

/**
 * Pick a point, line, polygon, or circle from a stored place.
 *
 * @param place - Station coordinate and optional stored shape.
 * @returns The shape the map should paint.
 * @example
 * drawForPlace({ latitude: 1, longitude: 2 });
 */
export function drawForPlace(place: MapGeometryInput): MapDraw {
  const kind = place.geometry?.kind;
  const positions = positionsOf(place.geometry?.coordinates);
  if (positions && (kind === 'polygon' || kind === 'line')) {
    return { kind, positions };
  }
  const radiusM = place.geometry?.radius_m;
  if (kind === 'circle' && typeof radiusM === 'number' && radiusM > 0) {
    return {
      kind: 'circle',
      latitude: place.latitude,
      longitude: place.longitude,
      radiusM,
    };
  }
  return {
    kind: 'point',
    latitude: place.latitude,
    longitude: place.longitude,
  };
}

/**
 * Copy a ring or path when it has at least two positions.
 *
 * @param coordinates - Stored latitude and longitude pairs.
 * @returns A mutable copy, or null when the path is too short.
 * @example
 * positionsOf([[1, 2], [3, 4]]);
 */
function positionsOf(
  coordinates: readonly [number, number][] | undefined,
): [number, number][] | null {
  if (!coordinates || coordinates.length < 2) {
    return null;
  }
  return coordinates.map((pair) => [pair[0], pair[1]]);
}

/**
 * Fixed continent and sub-region markers for the live map.
 */

import type { LivePlace } from '@/utils/liveMap';

/**
 * How far the map is zoomed: continents, sub-regions, or stations.
 * @example
 * const _ = true;
 */
export type PlotLevel = 'continent' | 'subregion' | 'station';

type MapRegion = {
  name: string;
  continent: string;
  west: number;
  south: number;
  east: number;
  north: number;
  anchor: [number, number];
};

/**
 * One continent or sub-region marker.
 * @example
 * const _ = true;
 */
export type MapCluster = {
  name: string;
  count: number;
  anchor: [number, number];
  points: [number, number][];
};

const SUBREGIONS: MapRegion[] = [
  {
    name: 'Central America',
    continent: 'North America',
    west: -93,
    south: 7,
    east: -77,
    north: 18,
    anchor: [14, -86],
  },
  {
    name: 'Caribbean',
    continent: 'North America',
    west: -85,
    south: 10,
    east: -59,
    north: 27,
    anchor: [18, -72],
  },
  {
    name: 'North America',
    continent: 'North America',
    west: -170,
    south: 15,
    east: -50,
    north: 84,
    anchor: [45, -100],
  },
  {
    name: 'South America',
    continent: 'South America',
    west: -82,
    south: -56,
    east: -34,
    north: 13,
    anchor: [-15, -60],
  },
  {
    name: 'Europe',
    continent: 'Europe',
    west: -25,
    south: 35,
    east: 40,
    north: 72,
    anchor: [50, 10],
  },
  {
    name: 'Middle East',
    continent: 'Asia',
    west: 26,
    south: 12,
    east: 63,
    north: 42,
    anchor: [28, 45],
  },
  {
    name: 'South Asia',
    continent: 'Asia',
    west: 60,
    south: 5,
    east: 95,
    north: 36,
    anchor: [22, 78],
  },
  {
    name: 'Southeast Asia',
    continent: 'Asia',
    west: 95,
    south: -11,
    east: 141,
    north: 23,
    anchor: [5, 115],
  },
  {
    name: 'North Asia',
    continent: 'Asia',
    west: 40,
    south: 36,
    east: 180,
    north: 80,
    anchor: [55, 90],
  },
  {
    name: 'Africa',
    continent: 'Africa',
    west: -18,
    south: -35,
    east: 52,
    north: 38,
    anchor: [5, 20],
  },
  {
    name: 'Oceania',
    continent: 'Oceania',
    west: 110,
    south: -48,
    east: 180,
    north: 0,
    anchor: [-25, 135],
  },
  {
    name: 'Pacific',
    continent: 'Oceania',
    west: -180,
    south: -50,
    east: -120,
    north: 10,
    anchor: [-15, -150],
  },
];

const CONTINENT_ANCHORS: Record<string, [number, number]> = {
  'North America': [45, -100],
  'South America': [-15, -60],
  Europe: [50, 10],
  Africa: [5, 20],
  Asia: [45, 90],
  Oceania: [-25, 135],
  Antarctica: [-75, 0],
};

/**
 * World, sub-region, or station drawing for a Leaflet zoom.
 *
 * @param zoom - Current map zoom
 * @returns Which markers to draw
 * @example
 * const _ = true;
 */
export function plotLevel(zoom: number): PlotLevel {
  if (zoom < 4) {
    return 'continent';
  }
  if (zoom < 7) {
    return 'subregion';
  }
  return 'station';
}

/**
 * Anchor for a continent cluster.
 *
 * @param continent - Continent name
 * @returns Fixed latitude and longitude
 * @example
 * const _ = true;
 */
export function continentAnchor(continent: string): [number, number] {
  return CONTINENT_ANCHORS[continent] ?? [0, 0];
}

/**
 * Whether a coordinate sits inside a region box.
 *
 * @param region - Fixed box
 * @param latitude - Latitude in degrees
 * @param longitude - Longitude in degrees
 * @returns True when the point is inside the box
 * @example
 * const _ = true;
 */
function inside(region: MapRegion, latitude: number, longitude: number): boolean {
  return (
    latitude >= region.south &&
    latitude <= region.north &&
    longitude >= region.west &&
    longitude <= region.east
  );
}

/**
 * Sub-region and continent for one coordinate.
 *
 * @param latitude - Latitude in degrees
 * @param longitude - Longitude in degrees
 * @returns Names and the marker anchor
 * @example
 * const _ = true;
 */
export function placeRegion(
  latitude: number,
  longitude: number,
): { name: string; continent: string; anchor: [number, number] } {
  const match = SUBREGIONS.find((region) => inside(region, latitude, longitude));
  if (match) {
    return { name: match.name, continent: match.continent, anchor: match.anchor };
  }
  if (latitude < -60) {
    return { name: 'Antarctica', continent: 'Antarctica', anchor: [-75, 0] };
  }
  if (longitude < -30) {
    if (latitude >= 13) {
      return {
        name: 'North America',
        continent: 'North America',
        anchor: [latitude, longitude],
      };
    }
    return {
      name: 'South America',
      continent: 'South America',
      anchor: [latitude, longitude],
    };
  }
  if (longitude < 60) {
    if (latitude >= 36) {
      return { name: 'Europe', continent: 'Europe', anchor: [latitude, longitude] };
    }
    return { name: 'Africa', continent: 'Africa', anchor: [latitude, longitude] };
  }
  if (latitude >= 0) {
    return { name: 'Asia', continent: 'Asia', anchor: [latitude, longitude] };
  }
  return { name: 'Oceania', continent: 'Oceania', anchor: [latitude, longitude] };
}

/**
 * Group places into continent or sub-region clusters.
 *
 * @param places - Places already loaded for the view
 * @param level - Continent or sub-region
 * @returns One cluster per name that has places
 * @example
 * const _ = true;
 */
export function clusterPlaces(
  places: LivePlace[],
  level: 'continent' | 'subregion',
): MapCluster[] {
  const groups = new Map<string, MapCluster>();
  for (const place of places) {
    const region = placeRegion(place.latitude, place.longitude);
    const name = level === 'continent' ? region.continent : region.name;
    const anchor =
      level === 'continent' ? continentAnchor(region.continent) : region.anchor;
    const point: [number, number] = [place.latitude, place.longitude];
    const current = groups.get(name);
    if (current) {
      current.count += 1;
      current.points.push(point);
    } else {
      groups.set(name, { name, count: 1, anchor, points: [point] });
    }
  }
  return [...groups.values()];
}

import { describe, expect, it } from 'vitest';
import {
  clusterPlaces,
  continentAnchor,
  placeRegion,
  plotLevel,
  regionFilterNames,
  type MapCluster,
} from './liveMapRegions';
import type { LivePlace } from './liveMap';

/**
 * One cached place at a coordinate.
 *
 * @param latitude - Latitude in degrees
 * @param longitude - Longitude in degrees
 * @returns Place with no reports
 * @example
 * const _ = true;
 */
function place(latitude: number, longitude: number): LivePlace {
  return {
    place_key: `${latitude},${longitude}`,
    product: 'metar',
    latitude,
    longitude,
    reports: [],
  };
}

describe('live map regions', () => {
  it('switches plot level with zoom', () => {
    expect(plotLevel(2)).toBe('continent');
    expect(plotLevel(3)).toBe('continent');
    expect(plotLevel(4)).toBe('subregion');
    expect(plotLevel(6)).toBe('subregion');
    expect(plotLevel(7)).toBe('station');
    expect(plotLevel(8)).toBe('station');
    expect(regionFilterNames()).toContain('Europe');
    expect(regionFilterNames()).toContain('Caribbean');
    expect(regionFilterNames()).toContain('Antarctica');
  });

  it('names continents and sub-regions', () => {
    expect(placeRegion(40.6, -73.7)).toMatchObject({
      name: 'North America',
      continent: 'North America',
    });
    expect(placeRegion(15, -86).name).toBe('Central America');
    expect(placeRegion(18, -70).name).toBe('Caribbean');
    expect(placeRegion(-15, -60).continent).toBe('South America');
    expect(placeRegion(50, 10).name).toBe('Europe');
    expect(placeRegion(30, 45).name).toBe('Middle East');
    expect(placeRegion(22, 78).name).toBe('South Asia');
    expect(placeRegion(5, 115).name).toBe('Southeast Asia');
    expect(placeRegion(55, 90).name).toBe('North Asia');
    expect(placeRegion(5, 20).continent).toBe('Africa');
    expect(placeRegion(-25, 135).name).toBe('Oceania');
    expect(placeRegion(-20, -150)).toMatchObject({
      name: 'Pacific',
      continent: 'Oceania',
    });
  });

  it('falls back when a coordinate is outside the boxes', () => {
    expect(placeRegion(-70, 10).continent).toBe('Antarctica');
    expect(placeRegion(14, -40)).toMatchObject({
      name: 'North America',
      anchor: [14, -40],
    });
    expect(placeRegion(0, -100).name).toBe('South America');
    expect(placeRegion(80, 0).name).toBe('Europe');
    expect(placeRegion(-40, 10).name).toBe('Africa');
    expect(placeRegion(2, 170).name).toBe('Asia');
    expect(placeRegion(-10, 70).name).toBe('Oceania');
    expect(continentAnchor('Nowhere')).toEqual([0, 0]);
    expect(continentAnchor('Europe')).toEqual([50, 10]);
  });

  it('groups places by continent and by sub-region', () => {
    const places = [
      place(40.6, -73.7),
      place(15, -86),
      place(-25, 135),
      place(-20, -150),
    ];
    const continents = clusterPlaces(places, 'continent');
    const north = continents.find(
      (item) => item.name === 'North America',
    ) as MapCluster;
    expect(north.count).toBe(2);
    expect(north.anchor).toEqual([45, -100]);
    const regions = clusterPlaces(places, 'subregion');
    expect(regions.find((item) => item.name === 'Central America')?.count).toBe(1);
    expect(regions.find((item) => item.name === 'Oceania')?.count).toBe(1);
    expect(regions.find((item) => item.name === 'Pacific')?.count).toBe(1);
  });
});

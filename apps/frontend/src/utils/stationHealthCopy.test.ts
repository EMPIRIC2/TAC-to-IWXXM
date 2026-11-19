/**
 * Station health operator copy helpers.
 */
import { describe, expect, it } from 'vitest';
import {
  STATION_HEALTH_NONE,
  formatCountMap,
  formatComponentScore,
  formatStationHealthRegion,
} from './stationHealthCopy';

describe('formatCountMap', () => {
  it('returns none for null, empty, and zero-only maps', () => {
    expect(formatCountMap(null)).toBe(STATION_HEALTH_NONE);
    expect(formatCountMap(undefined)).toBe(STATION_HEALTH_NONE);
    expect(formatCountMap({})).toBe(STATION_HEALTH_NONE);
    expect(formatCountMap({ a: 0 })).toBe(STATION_HEALTH_NONE);
  });

  it('joins positive counts for the table cells', () => {
    expect(formatCountMap({ AUTO: 2, COR: 1, skip: 0 })).toBe('AUTO 2, COR 1');
  });
});

describe('formatComponentScore', () => {
  it('formats numbers and blanks missing values', () => {
    expect(formatComponentScore(12.34, 1)).toBe('12.3');
    expect(formatComponentScore(null)).toBe('-');
    expect(formatComponentScore(Number.NaN)).toBe('-');
  });
});

describe('formatStationHealthRegion', () => {
  it('labels known regions and fails closed for unknown', () => {
    expect(formatStationHealthRegion('IV')).toMatch(/Region IV/);
    expect(formatStationHealthRegion(null)).toBe('Unknown region');
    expect(formatStationHealthRegion('')).toBe('Unknown region');
    expect(formatStationHealthRegion('VII')).toBe('Unknown region');
  });
});

import { describe, expect, it } from 'vitest';
import { drawForPlace } from '../src/index';

const ring: [number, number][] = [
  [1, 2],
  [3, 4],
];

describe('drawForPlace', () => {
  it('keeps a polygon and a line that have a path', () => {
    expect(
      drawForPlace({
        latitude: 0,
        longitude: 0,
        geometry: { kind: 'polygon', coordinates: ring },
      }),
    ).toEqual({ kind: 'polygon', positions: ring });
    expect(
      drawForPlace({
        latitude: 0,
        longitude: 0,
        geometry: { kind: 'line', coordinates: ring },
      }),
    ).toEqual({ kind: 'line', positions: ring });
  });

  it('keeps a circle that has a radius', () => {
    expect(
      drawForPlace({
        latitude: 12,
        longitude: 22,
        geometry: { kind: 'circle', radius_m: 5000 },
      }),
    ).toEqual({ kind: 'circle', latitude: 12, longitude: 22, radiusM: 5000 });
  });

  it('falls back to the station point', () => {
    expect(drawForPlace({ latitude: 40.6, longitude: -73.7 })).toEqual({
      kind: 'point',
      latitude: 40.6,
      longitude: -73.7,
    });
    expect(
      drawForPlace({
        latitude: 1,
        longitude: 2,
        geometry: { kind: 'polygon', coordinates: [[1, 2]] },
      }),
    ).toEqual({ kind: 'point', latitude: 1, longitude: 2 });
    expect(
      drawForPlace({
        latitude: 1,
        longitude: 2,
        geometry: { kind: 'circle', radius_m: 0 },
      }),
    ).toEqual({ kind: 'point', latitude: 1, longitude: 2 });
    expect(
      drawForPlace({
        latitude: 1,
        longitude: 2,
        geometry: { kind: 'circle' },
      }),
    ).toEqual({ kind: 'point', latitude: 1, longitude: 2 });
    expect(
      drawForPlace({
        latitude: 1,
        longitude: 2,
        geometry: { kind: 'point', coordinates: ring },
      }),
    ).toEqual({ kind: 'point', latitude: 1, longitude: 2 });
  });
});

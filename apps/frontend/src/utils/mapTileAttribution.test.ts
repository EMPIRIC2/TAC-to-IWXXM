/**
 * OSM tile URL + Leaflet corner attribution (UX-2026-10-30-map-data-attribution).
 */
import { afterEach, describe, expect, it, vi } from 'vitest';
import L from 'leaflet';
import { findInternalDocRefs } from '@/utils/internalDocRefGuard';
import { OSM_TILE_ATTRIBUTION, OSM_TILE_URL } from '@/utils/mapTileAttribution';
import { bindStationMap } from '@/utils/stationMap';

vi.mock('leaflet', () => ({
  default: {
    map: vi.fn(() => {
      const map = {
        setView: vi.fn(),
        remove: vi.fn(),
      };
      map.setView.mockReturnValue(map);
      return map;
    }),
    tileLayer: vi.fn(() => ({ addTo: vi.fn() })),
    divIcon: vi.fn(() => ({})),
    marker: vi.fn(() => ({ addTo: vi.fn() })),
  },
}));

describe('mapTileAttribution', () => {
  afterEach(() => {
    vi.mocked(L.tileLayer).mockClear();
  });

  it('names OpenStreetMap contributors and the ODbL with a copyright link', () => {
    expect(OSM_TILE_URL).toBe('https://tile.openstreetmap.org/{z}/{x}/{y}.png');
    expect(OSM_TILE_ATTRIBUTION).toMatch(/OpenStreetMap/i);
    expect(OSM_TILE_ATTRIBUTION).toMatch(/contributors/i);
    expect(OSM_TILE_ATTRIBUTION).toMatch(/Open Database License|\bODbL\b/i);
    expect(OSM_TILE_ATTRIBUTION).toContain('https://www.openstreetmap.org/copyright');
    expect(findInternalDocRefs(OSM_TILE_ATTRIBUTION)).toEqual([]);
    // Pre-fix bare credit must not satisfy the shared constant.
    expect(OSM_TILE_ATTRIBUTION).not.toBe('© OpenStreetMap');
  });

  it('passes the shared attribution into the station minimap tile layer', () => {
    bindStationMap(document.createElement('div'), {
      icao: 'KJFK',
      name: 'Kennedy',
      latitude: 40.64,
      longitude: -73.78,
    });
    expect(L.tileLayer).toHaveBeenCalledWith(
      OSM_TILE_URL,
      expect.objectContaining({ attribution: OSM_TILE_ATTRIBUTION }),
    );
  });
});

/**
 * Leaflet overlay painters for TAC weather layers.
 */

import { afterEach, describe, expect, it, vi } from 'vitest';
import L from 'leaflet';
import type { LivePlace } from '@/utils/liveMap';
import { paintTacOverlays, paintTemperatureMarkers } from '@/utils/liveMapOverlayPaint';
import { clusterByStation } from '@/utils/liveMapStationCluster';
import {
  defaultTacOverlayVisibility,
  toggleTacOverlay,
  type TacOverlayVisibility,
} from '@/utils/liveMapTacLayers';

const mapStub = {
  addLayer: vi.fn(),
} as unknown as L.Map;

const layerStub = {
  addTo: vi.fn(function addTo(this: unknown) {
    return this;
  }),
};

vi.mock('leaflet', () => ({
  default: {
    divIcon: vi.fn(() => ({})),
    marker: vi.fn(() => layerStub),
    circleMarker: vi.fn(() => layerStub),
  },
}));

const storm: LivePlace = {
  place_key: 'KJFK',
  product: 'metar',
  latitude: 40.6,
  longitude: -73.8,
  reports: [
    {
      observed_at: '2026-11-13T12:00:00Z',
      tac: 'METAR KJFK 131200Z 18025G35KT 1SM TSRA FZDZ BR BKN015 12/08',
    },
  ],
};

const calm: LivePlace = {
  place_key: 'KAAA',
  product: 'metar',
  latitude: 1,
  longitude: 2,
  reports: [
    {
      observed_at: '2026-11-13T12:00:00Z',
      tac: 'METAR KAAA 131200Z CAVOK',
    },
  ],
};

const vrb: LivePlace = {
  place_key: 'KVRB',
  product: 'metar',
  latitude: 3,
  longitude: 4,
  reports: [
    {
      observed_at: '2026-11-13T12:00:00Z',
      tac: 'METAR KVRB 131200Z VRB03KT 10SM FEW040 15/07',
    },
  ],
};

/**
 * Turn every overlay on.
 *
 * @returns Full visibility map
 * @example
 * const _ = true;
 */
function allOverlaysOn(): TacOverlayVisibility {
  let visibility = defaultTacOverlayVisibility();
  for (const id of Object.keys(visibility) as Array<keyof TacOverlayVisibility>) {
    visibility = toggleTacOverlay(visibility, id);
  }
  return visibility;
}

describe('paintTacOverlays', () => {
  afterEach(() => {
    vi.mocked(L.marker).mockClear();
    vi.mocked(L.circleMarker).mockClear();
    vi.mocked(L.divIcon).mockClear();
    layerStub.addTo.mockClear();
  });

  it('skips painting when every overlay is off', () => {
    const cluster = clusterByStation([storm])[0];
    expect(cluster).toBeDefined();
    if (!cluster) {
      return;
    }
    const layers = paintTacOverlays(mapStub, cluster, defaultTacOverlayVisibility());
    expect(layers).toEqual([]);
    expect(L.marker).not.toHaveBeenCalled();
    expect(L.circleMarker).not.toHaveBeenCalled();
  });

  it('paints weather, wind vector (scaled), and wind intensity when TAC feeds them', () => {
    const cluster = clusterByStation([storm])[0];
    expect(cluster).toBeDefined();
    if (!cluster) {
      return;
    }
    const layers = paintTacOverlays(mapStub, cluster, allOverlaysOn(), {
      magnitudeScale: 1.5,
    });
    expect(layers.length).toBeGreaterThan(0);
    expect(L.divIcon).toHaveBeenCalled();
    expect(L.marker).toHaveBeenCalled();
    expect(L.circleMarker).toHaveBeenCalledWith(
      expect.any(Array),
      expect.objectContaining({
        className: 'tac-overlay-icon-wind-intensity',
      }),
    );
  });

  it('paints temperature badges in C or F for temperatures mode', () => {
    const cluster = clusterByStation([storm])[0];
    expect(cluster).toBeDefined();
    if (!cluster) {
      return;
    }
    vi.mocked(L.divIcon).mockClear();
    const cLayers = paintTemperatureMarkers(mapStub, cluster, 'C');
    expect(cLayers.length).toBeGreaterThan(0);
    expect(L.divIcon).toHaveBeenCalledWith(
      expect.objectContaining({
        html: expect.stringContaining('°C'),
      }),
    );
    vi.mocked(L.divIcon).mockClear();
    paintTemperatureMarkers(mapStub, cluster, 'F');
    expect(L.divIcon).toHaveBeenCalledWith(
      expect.objectContaining({
        html: expect.stringContaining('°F'),
      }),
    );
  });

  it('skips temperature badges when no member reports a temperature', () => {
    const cluster = clusterByStation([calm])[0];
    expect(cluster).toBeDefined();
    if (!cluster) {
      return;
    }
    vi.mocked(L.divIcon).mockClear();
    vi.mocked(L.marker).mockClear();
    const layers = paintTemperatureMarkers(mapStub, cluster, 'C');
    expect(layers).toEqual([]);
    expect(L.marker).not.toHaveBeenCalled();
  });

  it('returns null painters when the station TAC does not feed the overlay', () => {
    const cluster = clusterByStation([calm])[0];
    expect(cluster).toBeDefined();
    if (!cluster) {
      return;
    }
    const layers = paintTacOverlays(mapStub, cluster, allOverlaysOn());
    expect(layers).toEqual([]);
  });

  it('skips wind vector when direction is variable', () => {
    const cluster = clusterByStation([vrb])[0];
    expect(cluster).toBeDefined();
    if (!cluster) {
      return;
    }
    const visibility = toggleTacOverlay(defaultTacOverlayVisibility(), 'windVector');
    const layers = paintTacOverlays(mapStub, cluster, visibility);
    expect(layers).toEqual([]);
    expect(L.marker).not.toHaveBeenCalled();
  });
});

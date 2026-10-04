/**
 * World map layers and the report popup.
 */
import { afterEach, describe, expect, it, vi } from 'vitest';
import { act, cleanup, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import L from 'leaflet';
import { boundsOf, LIVE_MAP_PRODUCTS } from '@/utils/liveMap';
import { LiveWorldMap } from './LiveWorldMap';

const clicks: Array<() => void> = [];
const map = {
  setView: vi.fn(),
  flyTo: vi.fn(),
  remove: vi.fn(),
  on: vi.fn(),
  getBounds: () => ({
    getWest: () => -80,
    getSouth: () => 40,
    getEast: () => -70,
    getNorth: () => 41,
  }),
};
map.setView.mockReturnValue(map);

const marker = {
  addTo: vi.fn(),
  on: vi.fn((event: string, handler: () => void) => {
    if (event === 'click') {
      clicks.push(handler);
    }
  }),
  remove: vi.fn(),
};
marker.addTo.mockReturnValue(marker);

vi.mock('leaflet', () => ({
  default: {
    map: vi.fn(() => map),
    tileLayer: vi.fn(() => ({ addTo: vi.fn() })),
    marker: vi.fn(() => marker),
    divIcon: vi.fn(() => ({})),
    polygon: vi.fn(() => marker),
    polyline: vi.fn(() => marker),
    circle: vi.fn(() => marker),
  },
}));

vi.mock('leaflet/dist/leaflet.css', () => ({}));

const place = {
  place_key: 'KJFK',
  product: 'metar',
  latitude: 40.6,
  longitude: -73.7,
  geometry: { kind: 'point' },
  reports: [
    {
      observed_at: 'newest',
      tac: 'METAR KJFK 031200Z 18012KT',
      iwxxm: '<iwxxm/>',
      issues: [],
    },
    {
      observed_at: 'older',
      tac: 'METAR KJFK 031100Z VRB03KT',
      iwxxm: null,
      issues: [],
    },
  ],
};

const hazard = {
  place_key: 'sigmet-abc',
  product: 'sigmet',
  latitude: 40,
  longitude: -74,
  geometry: {
    kind: 'polygon',
    coordinates: [
      [40, -74],
      [41, -73],
      [40, -72],
    ],
  },
  reports: [
    {
      observed_at: 'hazard',
      tac: 'SIGMET',
      iwxxm: null,
      issues: ['Translation failed.'],
    },
  ],
};

describe('LiveWorldMap', () => {
  afterEach(() => {
    cleanup();
    clicks.length = 0;
    vi.mocked(L.polygon).mockClear();
    vi.mocked(L.polyline).mockClear();
    vi.mocked(L.circle).mockClear();
    vi.mocked(L.marker).mockClear();
    vi.unstubAllGlobals();
  });

  it('reads bounds from the map', () => {
    expect(boundsOf(map as never)).toEqual({
      west: -80,
      south: 40,
      east: -70,
      north: 41,
    });
  });

  it('loads every layer, draws a polygon, and opens stored text', async () => {
    const user = userEvent.setup();
    vi.stubGlobal(
      'fetch',
      vi.fn().mockImplementation(async (url: string) => {
        const target = new URL(String(url), 'http://localhost');
        const products = target.searchParams.get('products') ?? '';
        if (products === '') {
          return { ok: true, json: async () => ({ places: [] }) };
        }
        if (!products.includes('metar')) {
          throw new DOMException('aborted', 'AbortError');
        }
        return {
          ok: true,
          json: async () => ({
            places: [
              place,
              hazard,
              {
                place_key: 'ZZZZ',
                product: 'metar',
                latitude: 10,
                longitude: 20,
                geometry: { kind: 'point' },
                reports: [
                  {
                    observed_at: 'z',
                    tac: 'METAR ZZZZ',
                    iwxxm: null,
                    issues: [],
                  },
                ],
              },
              {
                place_key: 'line-1',
                product: 'airmet',
                latitude: 11,
                longitude: 21,
                geometry: {
                  kind: 'line',
                  coordinates: [
                    [1, 2],
                    [3, 4],
                  ],
                },
                reports: [
                  {
                    observed_at: 'line',
                    tac: 'AIRMET LINE',
                    iwxxm: null,
                    issues: [],
                  },
                ],
              },
              {
                place_key: 'BARE',
                product: 'speci',
                latitude: 1,
                longitude: 2,
                reports: [
                  {
                    observed_at: 'bare',
                    tac: 'SPECI BARE',
                    iwxxm: null,
                    issues: [],
                  },
                ],
              },
              {
                place_key: 'circle-1',
                product: 'airmet',
                latitude: 12,
                longitude: 22,
                geometry: { kind: 'circle', radius_m: 5000 },
                reports: [
                  {
                    observed_at: 'circle',
                    tac: 'AIRMET CIRCLE',
                    iwxxm: null,
                    issues: [],
                  },
                ],
              },
            ],
          }),
        };
      }),
    );
    render(<LiveWorldMap />);
    expect(screen.getByTestId('live-map-beta')).toHaveTextContent('Beta');
    await waitFor(() => expect(L.polygon).toHaveBeenCalled());
    expect(L.polyline).toHaveBeenCalled();
    expect(L.circle).toHaveBeenCalled();
    expect(L.marker).toHaveBeenCalledWith([10, 20], expect.anything());
    expect(L.marker).toHaveBeenCalledWith([1, 2], expect.anything());
    await waitFor(() => expect(clicks.length).toBeGreaterThan(0));
    act(() => {
      clicks[0]?.();
    });
    expect(screen.getByTestId('live-map-detail')).toHaveTextContent('Kennedy');
    expect(screen.getByTestId('live-map-tac')).toHaveTextContent('18012KT');
    expect(screen.getByTestId('live-map-xml')).toHaveTextContent('<iwxxm/>');
    await user.click(screen.getByTestId('live-map-report-1'));
    expect(screen.getByTestId('live-map-pending')).toHaveTextContent(
      'Translation is pending.',
    );
    act(() => {
      clicks[1]?.();
    });
    expect(screen.getByTestId('live-map-issues')).toHaveTextContent(
      'Translation failed.',
    );
    act(() => {
      clicks[2]?.();
    });
    expect(screen.getByTestId('live-map-detail')).toHaveTextContent('ZZZZ');
    for (const product of LIVE_MAP_PRODUCTS) {
      await user.click(screen.getByTestId(`layer-${product}`));
    }
    await user.click(screen.getByTestId('layer-metar'));
    expect(screen.queryByTestId('live-map-error')).not.toBeInTheDocument();
  });

  it('moves the map to a searched station and skips an unknown one', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ places: [place] }),
      }),
    );
    const view = render(<LiveWorldMap focusStation="KJFK" />);
    await waitFor(() => expect(map.flyTo).toHaveBeenCalledWith([40.6, -73.7], 8));
    expect(screen.getByTestId('live-map-detail')).toHaveTextContent('Kennedy');
    map.flyTo.mockClear();
    view.rerender(<LiveWorldMap focusStation="NONE" />);
    expect(map.flyTo).not.toHaveBeenCalled();
  });

  it('shows an error when the cache cannot be read', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: false }));
    render(<LiveWorldMap />);
    expect(await screen.findByTestId('live-map-error')).toBeInTheDocument();
  });
});

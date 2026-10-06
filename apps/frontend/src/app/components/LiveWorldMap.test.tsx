/**
 * World map layers and the report popup.
 */
import { afterEach, describe, expect, it, vi } from 'vitest';
import { act, cleanup, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import L from 'leaflet';
import { boundsOf, LIVE_MAP_PRODUCTS, type LivePlace } from '@/utils/liveMap';
import { LiveWorldMap, StationPopup } from './LiveWorldMap';

const clicks: Array<() => void> = [];
const hovers: Array<() => void> = [];
const leaves: Array<() => void> = [];
const keys: Array<
  (event: { originalEvent?: { key?: string; preventDefault?: () => void } }) => void
> = [];
const originalSetTimeout = window.setTimeout.bind(window);
const popupEl = document.createElement('div');
const mapPane = document.createElement('div');
const canvasUpdate = vi.fn();
const map = {
  setView: vi.fn(),
  flyTo: vi.fn(),
  flyToBounds: vi.fn(),
  remove: vi.fn(),
  on: vi.fn(),
  invalidateSize: vi.fn(),
  getZoom: vi.fn(() => 8),
  getSize: vi.fn(() => ({ x: 800, y: 600 })),
  getContainer: vi.fn(() => mapPane),
  panBy: vi.fn(),
  eachLayer: vi.fn((handler: (item: typeof marker) => void) => {
    handler({ closePopup: vi.fn() } as unknown as typeof marker);
    handler(marker);
  }),
  getBounds: () => ({
    getWest: () => -80,
    getSouth: () => 40,
    getEast: () => -70,
    getNorth: () => 41,
  }),
  options: {} as { renderer?: { _update: () => void } },
  _renderer: undefined as { _update: () => void } | undefined,
};
map.setView.mockReturnValue(map);

const marker = {
  addTo: vi.fn(),
  on: vi.fn((event: string, handler: () => void) => {
    if (event === 'click') {
      clicks.push(handler);
    }
    if (event === 'mouseover') {
      hovers.push(handler);
    }
    if (event === 'mouseout') {
      leaves.push(handler);
    }
    if (event === 'keydown') {
      keys.push(handler);
    }
  }),
  remove: vi.fn(),
  bindPopup: vi.fn((node: HTMLElement) => {
    document.querySelectorAll('[data-testid="live-map-detail"]').forEach((el) => {
      el.parentElement?.remove();
    });
    document.body.append(node);
    return marker;
  }),
  openPopup: vi.fn(),
  closePopup: vi.fn(),
  getPopup: vi.fn(() => ({ getElement: () => popupEl, update: vi.fn() })),
  getElement: vi.fn(() => document.createElement('div')),
};
marker.addTo.mockReturnValue(marker);

vi.mock('leaflet', () => ({
  default: {
    map: vi.fn(() => map),
    tileLayer: vi.fn(() => ({ addTo: vi.fn() })),
    marker: vi.fn(() => marker),
    circleMarker: vi.fn(() => marker),
    divIcon: vi.fn(() => ({})),
    polygon: vi.fn(() => marker),
    polyline: vi.fn(() => marker),
    circle: vi.fn(() => marker),
    canvas: vi.fn(() => ({ _update: canvasUpdate, _map: map })),
    latLngBounds: vi.fn((points: unknown) => points),
  },
}));

vi.mock('leaflet/dist/leaflet.css', () => ({}));

const place: LivePlace = {
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
      issues: ['Also noted.'],
    },
    {
      observed_at: 'older',
      tac: 'METAR KJFK 031100Z VRB03KT',
      iwxxm: null,
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
  beforeEach(() => {
    map.getSize.mockReturnValue({ x: 800, y: 600 });
    map._renderer = { _update: canvasUpdate };
    canvasUpdate.mockClear();
    vi.spyOn(window, 'setTimeout').mockImplementation(((
      handler: TimerHandler,
      timeout?: number,
      ...args: unknown[]
    ) => {
      if (timeout === 50 && typeof handler === 'function') {
        handler();
        return 0 as unknown as ReturnType<typeof setTimeout>;
      }
      return originalSetTimeout(handler, timeout, ...args);
    }) as typeof setTimeout);
    vi.spyOn(window, 'setInterval').mockImplementation(((
      handler: TimerHandler,
      timeout?: number,
    ) => {
      if (timeout === 60_000 && typeof handler === 'function') {
        handler();
      }
      return 0 as unknown as ReturnType<typeof setInterval>;
    }) as unknown as typeof setInterval);
    mapPane.replaceChildren();
    const stray = document.createElement('div');
    stray.className = 'leaflet-popup';
    const keep = document.createElement('div');
    keep.className = 'leaflet-popup';
    keep.append(popupEl);
    mapPane.append(stray, keep);
    marker.getElement.mockReset();
    marker.getElement.mockReturnValueOnce(null as unknown as HTMLDivElement);
    marker.getElement.mockReturnValue(document.createElement('div'));
  });

  afterEach(() => {
    vi.mocked(window.setTimeout).mockRestore();
    vi.mocked(window.setInterval).mockRestore();
    cleanup();
    document.querySelectorAll('[data-testid="live-map-detail"]').forEach((el) => {
      el.parentElement?.remove();
    });
    clicks.length = 0;
    hovers.length = 0;
    map.panBy.mockClear();
    map.flyToBounds.mockClear();
    leaves.length = 0;
    keys.length = 0;
    map.getZoom.mockReturnValue(8);
    marker.getPopup.mockReset();
    marker.getPopup.mockReturnValue({ getElement: () => popupEl, update: vi.fn() });
    marker.closePopup.mockClear();
    vi.mocked(L.polygon).mockClear();
    vi.mocked(L.polyline).mockClear();
    vi.mocked(L.circle).mockClear();
    vi.mocked(L.circleMarker).mockClear();
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
                place_key: 'empty-1',
                product: 'metar',
                latitude: 3,
                longitude: 4,
                reports: [],
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
    const onOpenPlace = vi.fn();
    render(<LiveWorldMap onOpenPlace={onOpenPlace} />);
    expect(screen.getByTestId('live-map-beta')).toHaveTextContent('Beta');
    await waitFor(() => expect(L.polygon).toHaveBeenCalled());
    expect(L.polyline).toHaveBeenCalled();
    expect(L.circle).toHaveBeenCalled();
    expect(L.circleMarker).toHaveBeenCalledWith([10, 20], expect.anything());
    expect(L.circleMarker).toHaveBeenCalledWith([1, 2], expect.anything());
    expect(L.canvas).toHaveBeenCalledWith({ tolerance: 18 });
    expect(canvasUpdate).toHaveBeenCalled();
    await waitFor(() => expect(clicks.length).toBeGreaterThan(0));
    act(() => {
      clicks[0]?.();
    });
    expect(screen.getByTestId('live-map-notice')).toHaveTextContent(
      'not validated for operational use',
    );
    expect(screen.getByTestId('live-map-product')).toHaveTextContent('METAR');
    expect(screen.getByTestId('live-map-issued')).toHaveTextContent('newest');
    expect(screen.getByTestId('live-map-station')).toHaveTextContent('Kennedy');
    expect(screen.getByTestId('live-map-card')).toHaveAttribute('data-layout', 'side');
    expect(screen.getByTestId('live-map-detail')).toHaveTextContent('Kennedy');
    expect(screen.queryByTestId('live-map-decode')).not.toBeInTheDocument();
    expect(screen.queryByTestId('live-map-xml')).not.toBeInTheDocument();
    expect(screen.getByTestId('live-map-tac')).toHaveTextContent('18012KT');
    expect(onOpenPlace).not.toHaveBeenCalled();
    act(() => {
      clicks[0]?.();
    });
    expect(onOpenPlace).toHaveBeenCalledWith(place);
    expect(map.panBy).not.toHaveBeenCalled();
    expect(map.flyToBounds).not.toHaveBeenCalled();
    expect(map.invalidateSize).toHaveBeenCalled();
    act(() => {
      clicks[1]?.();
    });
    expect(screen.getByTestId('live-map-tac')).toHaveTextContent('SIGMET');
    expect(screen.getByTestId('live-map-station')).toHaveTextContent('Area');
    expect(onOpenPlace).toHaveBeenCalledTimes(1);
    act(() => {
      clicks[1]?.();
    });
    expect(onOpenPlace).toHaveBeenCalledWith(hazard);
    act(() => {
      clicks[2]?.();
    });
    expect(screen.getByTestId('live-map-detail')).toHaveTextContent('ZZZZ');
    for (const product of LIVE_MAP_PRODUCTS) {
      await user.click(screen.getByTestId(`layer-${product}`));
    }
    await user.click(screen.getByTestId('layer-metar'));
    expect(screen.queryByTestId('live-map-error')).not.toBeInTheDocument();
    act(() => {
      clicks[5]?.();
    });
    const opened = onOpenPlace.mock.calls.length;
    act(() => {
      clicks[5]?.();
    });
    expect(onOpenPlace).toHaveBeenCalledTimes(opened);
    marker.getPopup.mockReturnValueOnce(undefined as never);
    act(() => {
      clicks[0]?.();
    });
    const preventDefault = vi.fn();
    act(() => {
      keys[0]?.({ originalEvent: { key: 'Enter', preventDefault } });
      keys[0]?.({ originalEvent: { key: ' ', preventDefault } });
      keys[0]?.({ originalEvent: { key: 'x', preventDefault } });
      keys[0]?.({});
    });
    expect(preventDefault).toHaveBeenCalled();
  });

  it('draws route polygons at world zoom and opens the report', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ places: [place, hazard] }),
      }),
    );
    render(<LiveWorldMap />);
    await waitFor(() => expect(L.polygon).toHaveBeenCalled());
    expect(L.circleMarker).toHaveBeenCalled();
    expect(screen.getByTestId('live-map-canvas').className).toContain('min-h-[100dvh]');
    act(() => {
      clicks[1]?.();
    });
    expect(screen.getByTestId('live-map-tac')).toHaveTextContent('SIGMET');
    expect(map.flyToBounds).not.toHaveBeenCalled();
    expect(map.panBy).not.toHaveBeenCalled();
  });

  it('shows the station and the TAC without a decode pane', () => {
    render(<StationPopup place={place} />);
    expect(screen.getByTestId('live-map-station')).toHaveTextContent('Kennedy');
    expect(screen.getByTestId('live-map-tac')).toHaveTextContent('18012KT');
    expect(screen.queryByTestId('live-map-decode')).not.toBeInTheDocument();
  });

  it('renders nothing when a station has no reports', () => {
    render(
      <StationPopup
        place={{
          place_key: 'EMPTY',
          product: 'metar',
          latitude: 1,
          longitude: 2,
          reports: [],
        }}
      />,
    );
    expect(screen.queryByTestId('live-map-detail')).not.toBeInTheDocument();
  });

  it('moves the map to a searched station and skips an unknown one', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ places: [place, { ...place, product: 'taf' }] }),
      }),
    );
    const onOpenPlace = vi.fn();
    const view = render(<LiveWorldMap focusStation="KJFK" onOpenPlace={onOpenPlace} />);
    await waitFor(() => expect(map.flyTo).toHaveBeenCalledWith([40.6, -73.7], 8));
    expect(screen.getByTestId('live-map-detail')).toHaveTextContent('Kennedy');
    expect(onOpenPlace).not.toHaveBeenCalled();
    map.flyTo.mockClear();
    view.rerender(<LiveWorldMap focusStation="NONE" />);
    expect(map.flyTo).not.toHaveBeenCalled();
  });

  it('opens the card on hover and loads the earlier copy from the card', async () => {
    const user = userEvent.setup();
    map.getSize.mockReturnValue({ x: 400, y: 600 });
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ places: [place, hazard] }),
      }),
    );
    const onOpenPlace = vi.fn();
    render(<LiveWorldMap onOpenPlace={onOpenPlace} />);
    await waitFor(() => expect(hovers.length).toBeGreaterThan(1));
    act(() => {
      hovers[0]?.();
    });
    act(() => {
      hovers[0]?.();
    });
    expect(screen.getByTestId('live-map-card')).toHaveAttribute('data-layout', 'stack');
    expect(screen.getByTestId('live-map-product')).toHaveTextContent('METAR');
    expect(screen.getByTestId('live-map-issued')).toHaveTextContent('newest');
    expect(onOpenPlace).not.toHaveBeenCalled();
    await user.click(screen.getByTestId('live-map-newer'));
    await user.click(screen.getByTestId('live-map-earlier'));
    await user.click(screen.getByTestId('live-map-earlier'));
    expect(screen.getByTestId('live-map-tac')).toHaveTextContent('VRB03KT');
    expect(onOpenPlace).not.toHaveBeenCalled();
    await user.click(screen.getByTestId('live-map-newer'));
    expect(screen.getByTestId('live-map-tac')).toHaveTextContent('18012KT');
    await user.click(screen.getByTestId('live-map-earlier'));
    await user.click(screen.getByTestId('live-map-card'));
    expect(onOpenPlace).toHaveBeenCalledWith(
      expect.objectContaining({
        reports: [
          expect.objectContaining({ tac: 'METAR KJFK 031100Z VRB03KT' }),
          expect.objectContaining({ tac: 'METAR KJFK 031200Z 18012KT' }),
        ],
      }),
    );
    const preventDefault = vi.fn();
    act(() => {
      keys[1]?.({ originalEvent: { key: 'Enter', preventDefault } });
    });
    expect(preventDefault).toHaveBeenCalled();
    expect(screen.getByTestId('live-map-station')).toHaveTextContent('Area');
    expect(onOpenPlace).toHaveBeenCalledTimes(1);
  });

  it('shows an error when the cache cannot be read', async () => {
    vi.mocked(L.canvas).mockReturnValueOnce({ _update: canvasUpdate } as never);
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: false }));
    render(<LiveWorldMap />);
    expect(await screen.findByTestId('live-map-error')).toBeInTheDocument();
  });
});

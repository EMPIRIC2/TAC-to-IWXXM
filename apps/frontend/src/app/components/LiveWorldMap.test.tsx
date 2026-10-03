/**
 * World map views, layers, and the report popup.
 */
import { afterEach, describe, expect, it, vi } from 'vitest';
import { act, cleanup, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { boundsOf } from '@/utils/liveMap';
import { LiveWorldMap } from './LiveWorldMap';

const clicks: Array<() => void> = [];
const map = {
  setView: vi.fn(),
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
  },
}));

vi.mock('leaflet/dist/leaflet.css', () => ({}));

const place = {
  place_key: 'KJFK',
  product: 'metar',
  latitude: 40.6,
  longitude: -73.7,
  reports: [
    { observed_at: 'newest', tac: 'METAR KJFK 031200Z 18012KT' },
    { observed_at: 'older', tac: 'METAR KJFK 031100Z VRB03KT' },
  ],
};

describe('LiveWorldMap', () => {
  afterEach(() => {
    cleanup();
    clicks.length = 0;
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

  it('loads observations, switches views, and opens a report', async () => {
    const user = userEvent.setup();
    let converts = 0;
    vi.stubGlobal(
      'fetch',
      vi.fn().mockImplementation(async (url: string) => {
        const target = new URL(String(url), 'http://localhost');
        if (target.pathname.endsWith('/convert')) {
          converts += 1;
          if (converts > 1) {
            return { ok: false };
          }
          return {
            ok: true,
            json: async () => ({ results: [{ content: '<iwxxm/>' }] }),
          };
        }
        const products = target.searchParams.get('products');
        if (products === 'taf') {
          return { ok: false };
        }
        if (products === 'speci') {
          throw new DOMException('aborted', 'AbortError');
        }
        if (products === 'airmet,sigmet') {
          throw new DOMException('offline', 'NetworkError');
        }
        return {
          ok: true,
          json: async () => ({
            places: [
              place,
              {
                place_key: 'NONE',
                product: 'metar',
                latitude: 1,
                longitude: 2,
                reports: [],
              },
            ],
          }),
        };
      }),
    );
    render(<LiveWorldMap />);
    await waitFor(() => expect(clicks.length).toBeGreaterThan(0));
    act(() => {
      clicks[0]?.();
    });
    expect(screen.getByTestId('live-map-tac')).toHaveTextContent('18012KT');
    await user.click(screen.getByTestId('live-map-report-1'));
    expect(screen.getByTestId('live-map-wind')).toHaveTextContent('Variable wind');
    await user.click(screen.getByTestId('live-map-iwxxm'));
    expect(await screen.findByTestId('live-map-xml')).toHaveTextContent('<iwxxm/>');
    act(() => {
      clicks[1]?.();
    });
    expect(screen.queryByTestId('live-map-detail')).not.toBeInTheDocument();
    await user.click(screen.getByTestId('layer-metar'));
    await user.click(screen.getByTestId('layer-speci'));
    expect(screen.queryByTestId('live-map-detail')).not.toBeInTheDocument();
    await user.click(screen.getByTestId('layer-metar'));
    await user.click(screen.getByTestId('view-forecasts'));
    expect(await screen.findByTestId('live-map-error')).toBeInTheDocument();
    await user.click(screen.getByTestId('view-hazards'));
    await user.click(screen.getByTestId('view-advisories'));
    await user.click(screen.getByTestId('view-observations'));
    act(() => {
      clicks[0]?.();
    });
    await user.click(screen.getByTestId('live-map-iwxxm'));
    await waitFor(() => {
      expect(screen.getByTestId('live-map-xml')).toHaveTextContent('not available');
    });
  });
});

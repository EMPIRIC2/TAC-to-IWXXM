/**
 * Station minimap lookup and marker.
 */
import { afterEach, describe, expect, it, vi } from 'vitest';
import { cleanup, render, screen, waitFor } from '@testing-library/react';
import { StationMinimap } from './StationMinimap';
import { bindStationMap, fetchStationPoint } from '@/utils/stationMap';

const map = {
  setView: vi.fn(),
  remove: vi.fn(),
};
map.setView.mockReturnValue(map);

vi.mock('leaflet', () => ({
  default: {
    map: vi.fn(() => map),
    tileLayer: vi.fn(() => ({ addTo: vi.fn() })),
    divIcon: vi.fn(() => ({})),
    marker: vi.fn(() => ({ addTo: vi.fn() })),
  },
}));

vi.mock('leaflet/dist/leaflet.css', () => ({}));

const pointResponse = {
  status: 200,
  ok: true,
  json: async () => ({
    name: 'John F Kennedy International Airport',
    latitude: 40.64,
    longitude: -73.78,
  }),
};

describe('fetchStationPoint', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('returns a point, a miss, or throws when the lookup fails', async () => {
    const signal = new AbortController().signal;
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValueOnce(pointResponse).mockResolvedValueOnce({
        status: 404,
        ok: false,
      }),
    );
    await expect(fetchStationPoint('KJFK', signal)).resolves.toMatchObject({
      icao: 'KJFK',
      latitude: 40.64,
    });
    await expect(fetchStationPoint('ZZ99', signal)).resolves.toBeNull();

    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        status: 200,
        ok: true,
        json: async () => ({ name: ' ', latitude: 1, longitude: 2 }),
      }),
    );
    await expect(fetchStationPoint('KJFK', signal)).resolves.toMatchObject({
      name: 'KJFK',
    });

    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        status: 200,
        ok: true,
        json: async () => ({ latitude: 'north' }),
      }),
    );
    await expect(fetchStationPoint('KJFK', signal)).resolves.toBeNull();

    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ status: 503, ok: false }));
    await expect(fetchStationPoint('KJFK', signal)).rejects.toThrow(
      'Station lookup failed',
    );
  });
});

describe('bindStationMap', () => {
  it('does nothing without a point or a host, and removes the map it creates', () => {
    expect(bindStationMap(null, undefined)).toBeUndefined();
    expect(bindStationMap(document.createElement('div'), null)).toBeUndefined();
    const cleanup = bindStationMap(document.createElement('div'), {
      icao: 'KJFK',
      name: 'Kennedy',
      latitude: 40.64,
      longitude: -73.78,
    });
    expect(cleanup).toEqual(expect.any(Function));
    cleanup?.();
    expect(map.remove).toHaveBeenCalled();
  });
});

describe('StationMinimap', () => {
  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
    map.setView.mockClear();
    map.remove.mockClear();
  });

  it('draws a marker when the station is known', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(pointResponse));
    const { unmount } = render(<StationMinimap icao="kjfk" />);
    expect(screen.getByTestId('station-map-loading')).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByTestId('station-map')).toHaveAttribute(
        'aria-label',
        'Map of John F Kennedy International Airport',
      );
    });
    expect(map.setView).toHaveBeenCalledWith([40.64, -73.78], 8);
    unmount();
    expect(map.remove).toHaveBeenCalled();
  });

  it('says there is no map for an unknown or incomplete station', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ status: 404, ok: false }));
    const { unmount } = render(<StationMinimap icao="ZZ99" />);
    await waitFor(() => {
      expect(screen.getByTestId('station-map-empty')).toHaveTextContent(
        'No map for this station.',
      );
    });
    unmount();
    render(<StationMinimap icao="T" />);
    expect(screen.getByTestId('station-map-empty')).toBeInTheDocument();
  });

  it('says there is no map when the lookup fails, and ignores a cancelled request', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ status: 500, ok: false }));
    const { unmount } = render(<StationMinimap icao="KJFK" />);
    await waitFor(() => {
      expect(screen.getByTestId('station-map-empty')).toBeInTheDocument();
    });
    unmount();

    let rejectFetch: (error: unknown) => void = () => undefined;
    vi.stubGlobal(
      'fetch',
      vi.fn(
        () =>
          new Promise((_resolve, reject) => {
            rejectFetch = reject;
          }),
      ),
    );
    const pending = render(<StationMinimap icao="EGLL" />);
    pending.unmount();
    rejectFetch(new DOMException('aborted', 'AbortError'));
    await Promise.resolve();
    expect(screen.queryByTestId('station-map-empty')).not.toBeInTheDocument();
  });
});

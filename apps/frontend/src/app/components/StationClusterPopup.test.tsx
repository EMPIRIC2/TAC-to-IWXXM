/**
 * Same-station cluster → report picker.
 */

import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import type { LivePlace } from '@/utils/liveMap';
import { clusterByStation } from '@/utils/liveMapStationCluster';
import { StationClusterPopup } from './StationClusterPopup';

vi.mock('@/utils/liveMapStationCluster', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@/utils/liveMapStationCluster')>();
  return {
    ...actual,
    placeWithReportIndex: vi.fn(actual.placeWithReportIndex),
  };
});

import { placeWithReportIndex } from '@/utils/liveMapStationCluster';

const metar: LivePlace = {
  place_key: 'KJFK',
  product: 'metar',
  latitude: 40.6,
  longitude: -73.8,
  reports: [
    { observed_at: '2026-11-13T12:00:00Z', tac: 'METAR KJFK 18012KT' },
    { observed_at: '2026-11-13T11:00:00Z', tac: 'METAR KJFK 17010KT' },
  ],
};

const speci: LivePlace = {
  place_key: 'KJFK',
  product: 'speci',
  latitude: 40.6,
  longitude: -73.8,
  reports: [{ observed_at: '2026-11-13T12:15:00Z', tac: 'SPECI KJFK 19008KT' }],
};

describe('StationClusterPopup', () => {
  beforeEach(() => {
    vi.mocked(placeWithReportIndex).mockImplementation((place, reportIndex) => {
      const report = place.reports[reportIndex];
      if (!report) {
        return null;
      }
      return { ...place, reports: [report] };
    });
  });

  it('lists cluster reports and loads the picked TAC into the converter', async () => {
    const user = userEvent.setup();
    const onLoad = vi.fn();
    const cluster = clusterByStation([metar, speci])[0];
    expect(cluster).toBeDefined();
    if (!cluster) {
      return;
    }
    render(<StationClusterPopup cluster={cluster} onLoad={onLoad} />);
    const pick = screen.getByTestId('live-map-cluster-pick');
    expect(pick).toBeInTheDocument();
    expect(screen.getByTestId('live-map-cluster')).toBeInTheDocument();
    const second = (pick as HTMLSelectElement).options[1]?.value;
    expect(second).toBeDefined();
    await user.selectOptions(pick, second ?? '');
    await user.click(screen.getByTestId('live-map-send-to-converter'));
    expect(onLoad).toHaveBeenCalled();
    const sent = String(onLoad.mock.calls[0]?.[0] ?? '');
    expect(sent.length).toBeGreaterThan(0);
  });

  it('shows a calm empty state when the cluster has no reports', () => {
    render(
      <StationClusterPopup
        cluster={{
          stationKey: 'KJFK',
          latitude: 40,
          longitude: -70,
          members: [
            {
              place_key: 'KJFK',
              product: 'metar',
              latitude: 40,
              longitude: -70,
              reports: [],
            },
          ],
        }}
      />,
    );
    expect(screen.getByTestId('live-map-cluster-empty')).toBeInTheDocument();
  });

  it('shows empty when narrowing the picked report fails', () => {
    vi.mocked(placeWithReportIndex).mockReturnValue(null);
    const cluster = clusterByStation([metar])[0];
    expect(cluster).toBeDefined();
    if (!cluster) {
      return;
    }
    render(<StationClusterPopup cluster={cluster} />);
    expect(screen.getByTestId('live-map-cluster-empty')).toBeInTheDocument();
  });

  it('skips the report picker when the station has one report', () => {
    const sole: LivePlace = {
      place_key: 'KBOS',
      product: 'metar',
      latitude: 42.3,
      longitude: -71,
      reports: [{ observed_at: '2026-11-13T12:00:00Z', tac: 'METAR KBOS 18010KT' }],
    };
    const cluster = clusterByStation([sole])[0];
    expect(cluster).toBeDefined();
    if (!cluster) {
      return;
    }
    render(<StationClusterPopup cluster={cluster} />);
    expect(screen.getByTestId('live-map-cluster')).toBeInTheDocument();
    expect(screen.queryByTestId('live-map-cluster-pick')).not.toBeInTheDocument();
    expect(screen.getByTestId('live-map-station')).toHaveTextContent('KBOS');
  });
});

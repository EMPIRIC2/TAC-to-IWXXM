/**
 * TAC overlay parse, toggle, and station-cluster helpers.
 */

import { describe, expect, it } from 'vitest';
import type { LivePlace } from '@/utils/liveMap';
import {
  clusterAriaLabel,
  clusterByStation,
  clusterReportChoices,
  placeWithReportIndex,
} from '@/utils/liveMapStationCluster';
import {
  defaultTacOverlayVisibility,
  overlayApplies,
  overlayMatchCount,
  placeFeedsOverlay,
  TAC_OVERLAY_LAYERS,
  toggleTacOverlay,
  windIntensityBand,
  windIntensityRadius,
} from '@/utils/liveMapTacLayers';
import {
  parseTacOverlayFields,
  tempTokenToC,
} from '@/utils/liveMapTacParse';

const metarTs: LivePlace = {
  place_key: 'KJFK',
  product: 'metar',
  latitude: 40.6,
  longitude: -73.8,
  reports: [
    {
      observed_at: '2026-11-13T12:00:00Z',
      tac: 'METAR KJFK 131200Z 18025G35KT 1SM TSRA BR BKN015 12/08',
    },
  ],
};

const metarIce: LivePlace = {
  place_key: 'CYYZ',
  product: 'metar',
  latitude: 43.7,
  longitude: -79.6,
  reports: [
    {
      observed_at: '2026-11-13T11:00:00Z',
      tac: 'METAR CYYZ 131100Z 01008KT 1/2SM FZDZ FG M05/M06',
    },
  ],
};

const speciSameStation: LivePlace = {
  place_key: 'KJFK',
  product: 'speci',
  latitude: 40.6,
  longitude: -73.8,
  reports: [
    {
      observed_at: '2026-11-13T12:15:00Z',
      tac: 'SPECI KJFK 131215Z 19010KT 3SM -RA 11/07',
    },
  ],
};

const areaSigmet: LivePlace = {
  place_key: 'area-1',
  product: 'sigmet',
  latitude: 40,
  longitude: -70,
  geometry: {
    kind: 'polygon',
    coordinates: [
      [40, -70],
      [41, -70],
      [41, -69],
    ],
  },
  reports: [{ observed_at: '2026-11-13T10:00:00Z', tac: 'SIGMET TS' }],
};

const thunderTac =
  metarTs.reports[0]?.tac ??
  'METAR KJFK 131200Z 18025G35KT 1SM TSRA BR BKN015 12/08';
const iceTac =
  metarIce.reports[0]?.tac ??
  'METAR CYYZ 131100Z 01008KT 1/2SM FZDZ FG M05/M06';

describe.each([
  {
    name: 'thunderstorm METAR',
    tac: thunderTac,
    expectThunder: true,
    expectIce: false,
    expectPrecip: true,
    temp: 12,
    windDir: 180,
    windKt: 25,
  },
  {
    name: 'freezing drizzle',
    tac: iceTac,
    expectThunder: false,
    expectIce: true,
    expectPrecip: true,
    temp: -5,
    windDir: 10,
    windKt: 8,
  },
  {
    name: 'empty / no weather',
    tac: 'METAR KAAA 131200Z CAVOK',
    expectThunder: false,
    expectIce: false,
    expectPrecip: false,
    temp: null,
    windDir: null,
    windKt: null,
  },
] as const)('parseTacOverlayFields ($name)', (row) => {
  it('extracts overlay fields from raw TAC', () => {
    const parsed = parseTacOverlayFields(row.tac);
    expect(parsed.hasThunder).toBe(row.expectThunder);
    expect(parsed.hasIce).toBe(row.expectIce);
    expect(parsed.precipCodes.length > 0).toBe(row.expectPrecip);
    expect(parsed.temperatureC).toBe(row.temp);
    if (row.windKt === null) {
      expect(parsed.wind).toBeNull();
    } else {
      expect(parsed.wind?.speedKt).toBe(row.windKt);
      expect(parsed.wind?.directionDeg).toBe(row.windDir);
    }
  });
});

describe('tempTokenToC', () => {
  it.each([
    ['12', 12],
    ['M05', -5],
    ['00', 0],
    ['M00', -0],
  ] as const)('maps %s → %s', (token, expected) => {
    expect(tempTokenToC(token)).toBe(expected);
  });
});

describe('TAC overlay visibility', () => {
  it('defaults every overlay off and toggles one id independently', () => {
    const initial = defaultTacOverlayVisibility();
    for (const layer of TAC_OVERLAY_LAYERS) {
      expect(initial[layer.id]).toBe(false);
    }
    const thunderOn = toggleTacOverlay(initial, 'thunder');
    expect(thunderOn.thunder).toBe(true);
    expect(thunderOn.ice).toBe(false);
    expect(thunderOn.precip).toBe(false);
    const thunderOff = toggleTacOverlay(thunderOn, 'thunder');
    expect(thunderOff.thunder).toBe(false);
  });

  it('reports empty match counts when no TAC feeds the overlay', () => {
    expect(overlayMatchCount([], 'thunder')).toBe(0);
    expect(
      overlayMatchCount(
        [{ reports: [{ tac: 'METAR KAAA 131200Z CAVOK' }] }],
        'thunder',
      ),
    ).toBe(0);
    expect(placeFeedsOverlay(metarTs.reports, 'thunder')).toBe(true);
    expect(placeFeedsOverlay(metarIce.reports, 'ice')).toBe(true);
    expect(overlayApplies(parseTacOverlayFields(thunderTac), 'windVector')).toBe(
      true,
    );
    expect(
      overlayApplies(parseTacOverlayFields('METAR KAAA VRB03KT'), 'windVector'),
    ).toBe(false);
    expect(
      overlayApplies(parseTacOverlayFields('METAR KAAA VRB03KT'), 'windIntensity'),
    ).toBe(true);
  });
});

describe('wind intensity encoding', () => {
  it.each([
    [0, 'calm', 4],
    [10, 'light', 6],
    [20, 'moderate', 8],
    [30, 'strong', 10],
    [40, 'gale', 12],
  ] as const)('speed %s → band %s radius %s', (kt, band, radius) => {
    expect(windIntensityBand(kt)).toBe(band);
    expect(windIntensityRadius(kt)).toBe(radius);
  });
});

describe('clusterByStation', () => {
  it('merges same-station products into one cluster and skips area shapes', () => {
    const clusters = clusterByStation([metarTs, speciSameStation, areaSigmet, metarIce]);
    expect(clusters).toHaveLength(2);
    const jfk = clusters.find((item) => item.stationKey === 'KJFK');
    expect(jfk).toBeDefined();
    if (!jfk) {
      return;
    }
    expect(jfk.members).toHaveLength(2);
    const choices = clusterReportChoices(jfk);
    expect(choices).toHaveLength(2);
    expect(choices[0]?.label).toMatch(/METAR|SPECI/);
    expect(clusterAriaLabel(jfk)).toContain('KJFK');
    expect(clusterAriaLabel(jfk)).toMatch(/2/);
    expect(placeWithReportIndex(metarTs, 0)?.reports).toHaveLength(1);
    expect(placeWithReportIndex(metarTs, 9)).toBeNull();
  });

  it('returns an empty list when there are no station points', () => {
    expect(clusterByStation([])).toEqual([]);
    expect(clusterByStation([areaSigmet])).toEqual([]);
  });
});

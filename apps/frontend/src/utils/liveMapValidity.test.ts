/**
 * Active reports validity filter — evolve-auto test matrix.
 *
 * Dimensions: success / mutation / failure / validation (±).
 * [Corpus: product] F37
 */
import { describe, expect, it } from 'vitest';
import { filterPlaces, type LivePlace } from './liveMap';
import {
  defaultActiveReportsOn,
  isReportActiveNow,
  parseValidityStamp,
  placeIsActiveNow,
  resolveReportValidity,
  stampFromDayHourMinute,
  validityFromTac,
} from './liveMapValidity';

const NOW = Date.parse('2026-11-13T15:00:00Z');

const identityFilters = {
  country: 'all',
  region: 'all',
  time: 'full' as const,
  phenomena: new Set<string>(),
  now: NOW,
  countryOf: () => undefined,
  regionOf: () => ({ name: 'North America', continent: 'North America' }),
  placeIsActiveNow,
};

function place(
  product: string,
  tac: string,
  observedAt = '2026-11-13T12:00:00Z',
  extra: Partial<LivePlace['reports'][0]> = {},
): LivePlace {
  return {
    place_key: product === 'metar' ? 'KJFK' : `${product}-1`,
    product,
    latitude: 40.64,
    longitude: -73.78,
    reports: [{ observed_at: observedAt, tac, ...extra }],
  };
}

describe('liveMapValidity — success paths', () => {
  it('S: active TAF inside validity shows when filter ON; all show when OFF', () => {
    const active = place(
      'taf',
      'TAF KJFK 131200Z 1312/1412 18010KT',
      '2026-11-13T12:00:00Z',
    );
    const expired = place(
      'taf',
      'TAF KJFK 131000Z 1300/1312 18010KT',
      '2026-11-13T10:00:00Z',
    );
    const on = filterPlaces([active, expired], {
      ...identityFilters,
      activeOnly: true,
    });
    expect(on).toEqual([active]);
    const off = filterPlaces([active, expired], {
      ...identityFilters,
      activeOnly: false,
    });
    expect(off).toEqual([active, expired]);
  });

  it('S: SIGMET VALID range active at now is kept', () => {
    const sigmet = place(
      'sigmet',
      'YUDD SIGMET 2 VALID 131200/131800 YUSO- YUDD OBSC TS FCST =',
      '2026-11-13T12:00:00Z',
    );
    expect(placeIsActiveNow(sigmet, NOW)).toBe(true);
  });

  it('S: payload valid_from/valid_to wins over TAC', () => {
    const report = place(
      'taf',
      'TAF KJFK 131200Z 1312/1412 18010KT',
      '2026-11-13T12:00:00Z',
      {
        valid_from: '2026-11-13T14:00:00Z',
        valid_to: '2026-11-13T16:00:00Z',
      },
    );
    const validity = resolveReportValidity(report.reports[0]!);
    expect(validity).toEqual({
      validFromMs: Date.parse('2026-11-13T14:00:00Z'),
      validToMs: Date.parse('2026-11-13T16:00:00Z'),
    });
    expect(placeIsActiveNow(report, NOW)).toBe(true);
  });
});

describe('liveMapValidity — validation success/failure', () => {
  it('V+: start inclusive — exactly now is active', () => {
    const validity = {
      validFromMs: NOW,
      validToMs: NOW + 3_600_000,
    };
    expect(isReportActiveNow(validity, NOW)).toBe(true);
  });

  it('V+: end exclusive — exactly end is inactive', () => {
    const validity = {
      validFromMs: NOW - 3_600_000,
      validToMs: NOW,
    };
    expect(isReportActiveNow(validity, NOW)).toBe(false);
  });

  it('V−: malformed valid_from/valid_to fail closed (exclude)', () => {
    const bad = place(
      'taf',
      'TAF KJFK 131200Z 1312/1412 18010KT',
      '2026-11-13T12:00:00Z',
      {
        valid_from: 'not-a-time',
        valid_to: '2026-11-13T16:00:00Z',
      },
    );
    expect(resolveReportValidity(bad.reports[0]!)).toBeNull();
    expect(placeIsActiveNow(bad, NOW)).toBe(false);
  });

  it('V−: missing validity on METAR excluded when filter ON', () => {
    const metar = place(
      'metar',
      'METAR KJFK 131451Z 18012KT 10SM FEW040=',
      '2026-11-13T14:51:00Z',
    );
    expect(resolveReportValidity(metar.reports[0]!)).toBeNull();
    const filtered = filterPlaces([metar], { ...identityFilters, activeOnly: true });
    expect(filtered).toEqual([]);
  });

  it('V−: one-sided valid_to without valid_from fails closed', () => {
    const one = place(
      'taf',
      'TAF KJFK 131200Z 1312/1412 18010KT',
      '2026-11-13T12:00:00Z',
      {
        valid_to: '2026-11-13T16:00:00Z',
      },
    );
    expect(resolveReportValidity(one.reports[0]!)).toBeNull();
  });

  it('V−: inverted window (to <= from) rejected', () => {
    expect(
      resolveReportValidity({
        observed_at: '2026-11-13T12:00:00Z',
        tac: 'x',
        valid_from: '2026-11-13T16:00:00Z',
        valid_to: '2026-11-13T14:00:00Z',
      }),
    ).toBeNull();
  });
});

describe('liveMapValidity — failure modes', () => {
  it('F: empty place reports → inactive, no crash', () => {
    const empty: LivePlace = {
      place_key: 'KJFK',
      product: 'taf',
      latitude: 1,
      longitude: 2,
      reports: [],
    };
    expect(placeIsActiveNow(empty, NOW)).toBe(false);
    expect(filterPlaces([empty], { ...identityFilters, activeOnly: true })).toEqual([]);
  });

  it('F: unreadable observed_at with TAC period → null', () => {
    expect(validityFromTac('TAF KJFK 131200Z 1312/1412 18010KT', 'bad')).toBeNull();
  });

  it('F: parseValidityStamp rejects empty / garbage', () => {
    expect(parseValidityStamp('')).toBeNull();
    expect(parseValidityStamp('   ')).toBeNull();
    expect(parseValidityStamp('garbage')).toBeNull();
    expect(parseValidityStamp(null)).toBeNull();
  });

  it('F: stampFromDayHourMinute rejects out-of-range', () => {
    expect(stampFromDayHourMinute(32, 0, 0, NOW)).toBeNull();
    expect(stampFromDayHourMinute(1, 24, 0, NOW)).toBeNull();
    expect(stampFromDayHourMinute(1, 0, 60, NOW)).toBeNull();
  });
});

describe('liveMapValidity — mutation modes', () => {
  it('M: toggle ON→OFF→ON restores active-only set', () => {
    const active = place(
      'taf',
      'TAF KJFK 131200Z 1312/1412 18010KT',
      '2026-11-13T12:00:00Z',
    );
    const metar = place('metar', 'METAR KJFK 131451Z 18012KT=', '2026-11-13T14:51:00Z');
    const set = [active, metar];
    expect(filterPlaces(set, { ...identityFilters, activeOnly: true })).toEqual([
      active,
    ]);
    expect(filterPlaces(set, { ...identityFilters, activeOnly: false })).toEqual(set);
    expect(filterPlaces(set, { ...identityFilters, activeOnly: true })).toEqual([
      active,
    ]);
  });

  it('M: load new report set changes defaultActiveReportsOn', () => {
    const metars = [
      place('metar', 'METAR KJFK 131451Z 18012KT=', '2026-11-13T14:51:00Z'),
    ];
    expect(defaultActiveReportsOn(metars)).toBe(false);
    const withTaf = [
      ...metars,
      place('taf', 'TAF KJFK 131200Z 1312/1412 18010KT', '2026-11-13T12:00:00Z'),
    ];
    expect(defaultActiveReportsOn(withTaf)).toBe(true);
  });

  it('M: clear reports → default off', () => {
    expect(defaultActiveReportsOn([])).toBe(false);
  });
});

describe('liveMapValidity — product × filter permutations', () => {
  const products: Array<{ product: string; tac: string; active: boolean }> = [
    {
      product: 'taf',
      tac: 'TAF KJFK 131200Z 1312/1412 18010KT',
      active: true,
    },
    {
      product: 'sigmet',
      tac: 'YUDD SIGMET 2 VALID 131200/131800 YUSO- TS =',
      active: true,
    },
    {
      product: 'airmet',
      tac: 'YUDD AIRMET 2 VALID 131200/131800 YUSO- IFR =',
      active: true,
    },
    {
      product: 'sigmet',
      tac: 'WSUS31 KKCI 131455\nCONVECTIVE SIGMET 27E\nVALID UNTIL 1655Z\n',
      active: true,
    },
    {
      product: 'metar',
      tac: 'METAR KJFK 131451Z 18012KT=',
      active: false,
    },
    {
      product: 'speci',
      tac: 'SPECI KJFK 131505Z 18012KT=',
      active: false,
    },
  ];

  it.each(products)(
    'permute $product active=$active × filter on/off',
    ({ product, tac, active }) => {
      const row = place(product, tac, '2026-11-13T12:00:00Z');
      expect(placeIsActiveNow(row, NOW)).toBe(active);
      const on = filterPlaces([row], { ...identityFilters, activeOnly: true });
      expect(on).toEqual(active ? [row] : []);
      const off = filterPlaces([row], { ...identityFilters, activeOnly: false });
      expect(off).toEqual([row]);
    },
  );

  it('permute empty list × filter on/off', () => {
    expect(filterPlaces([], { ...identityFilters, activeOnly: true })).toEqual([]);
    expect(filterPlaces([], { ...identityFilters, activeOnly: false })).toEqual([]);
  });

  it('permute with/without validity fields on same TAC', () => {
    const withFields = place(
      'taf',
      'TAF KJFK 131200Z 1312/1412 18010KT',
      '2026-11-13T12:00:00Z',
      {
        valid_from: '2026-11-13T14:30:00Z',
        valid_to: '2026-11-13T15:30:00Z',
      },
    );
    const without = place(
      'taf',
      'TAF KJFK 131200Z 1312/1412 18010KT',
      '2026-11-13T12:00:00Z',
    );
    expect(placeIsActiveNow(withFields, NOW)).toBe(true);
    expect(placeIsActiveNow(without, NOW)).toBe(true);
  });
});

import { describe, expect, it } from 'vitest';

import {
  CONVERSION_PROFILE_SHARE_BUNDLE_VERSION,
  createConversionProfileShareBundle,
  parseConversionProfileShareBundle,
} from './conversionProfileShare';

describe('createConversionProfileShareBundle', () => {
  it('exports only importable rule-pack and overlay fields', () => {
    const bundle = createConversionProfileShareBundle({
      rulePacks: [
        {
          id: 'pack-1',
          user_id: 'user-1',
          slug: 'metar-soft',
          profile: 'ICAO_2025',
          product: 'METAR',
          stage: 'lint',
          severity: 'warning',
          when: 'missing_terminator',
          message: 'Need =',
          standardReference: 'Annex 3',
          created_at: '2026-09-06T00:00:00Z',
          updated_at: '2026-09-06T00:00:00Z',
        },
      ],
      overlays: [
        {
          id: 'overlay-1',
          user_id: 'user-1',
          slug: 'icao-soft',
          baseProfileId: 'ICAO_2025',
          body: { lint: { severity: 'warning' } },
          signature: 'signed',
          shared: true,
          created_at: '2026-09-06T00:00:00Z',
          updated_at: '2026-09-06T00:00:00Z',
        },
      ],
    });

    expect(bundle).toEqual({
      schemaVersion: CONVERSION_PROFILE_SHARE_BUNDLE_VERSION,
      rulePacks: [
        {
          slug: 'metar-soft',
          profile: 'ICAO_2025',
          product: 'METAR',
          stage: 'lint',
          severity: 'warning',
          when: 'missing_terminator',
          message: 'Need =',
          standardReference: 'Annex 3',
        },
      ],
      overlays: [
        {
          slug: 'icao-soft',
          baseProfileId: 'ICAO_2025',
          body: { lint: { severity: 'warning' } },
          shared: true,
        },
      ],
    });
  });
});

describe('parseConversionProfileShareBundle', () => {
  it('parses a valid share bundle into create payloads', () => {
    const bundle = parseConversionProfileShareBundle(
      JSON.stringify({
        schemaVersion: CONVERSION_PROFILE_SHARE_BUNDLE_VERSION,
        rulePacks: [
          {
            slug: 'metar-soft',
            profile: 'ICAO_2025',
            product: 'METAR',
            stage: 'lint',
            severity: 'warning',
            when: 'missing_terminator',
            message: 'Need =',
            standardReference: 'Annex 3',
            user_id: 'ignored',
          },
        ],
        overlays: [
          {
            slug: 'icao-soft',
            baseProfileId: 'ICAO_2025',
            body: { lint: { severity: 'warning' } },
            shared: false,
            signature: 'ignored',
          },
        ],
      }),
    );

    expect(bundle.rulePacks[0]).toEqual({
      slug: 'metar-soft',
      profile: 'ICAO_2025',
      product: 'METAR',
      stage: 'lint',
      severity: 'warning',
      when: 'missing_terminator',
      message: 'Need =',
      standardReference: 'Annex 3',
    });
    expect(bundle.overlays[0]).toEqual({
      slug: 'icao-soft',
      baseProfileId: 'ICAO_2025',
      body: { lint: { severity: 'warning' } },
      shared: false,
    });
  });

  it('accepts omitted optional fields and defaults overlay body', () => {
    const bundle = parseConversionProfileShareBundle(
      JSON.stringify({
        schemaVersion: CONVERSION_PROFILE_SHARE_BUNDLE_VERSION,
        rulePacks: [
          {
            slug: 'metar-soft',
            profile: 'ICAO_2025',
            product: 'METAR',
            stage: 'lint',
            severity: 'warning',
          },
        ],
        overlays: [
          {
            slug: 'icao-soft',
            baseProfileId: 'ICAO_2025',
          },
        ],
      }),
    );

    expect(bundle.rulePacks[0]).toEqual({
      slug: 'metar-soft',
      profile: 'ICAO_2025',
      product: 'METAR',
      stage: 'lint',
      severity: 'warning',
      when: undefined,
      message: undefined,
      standardReference: undefined,
    });
    expect(bundle.overlays[0]).toEqual({
      slug: 'icao-soft',
      baseProfileId: 'ICAO_2025',
      body: {},
      shared: undefined,
    });
  });

  it('rejects malformed or unsupported bundles', () => {
    expect(() => parseConversionProfileShareBundle('{')).toThrow(
      'Share bundle must be valid JSON',
    );
    expect(() => parseConversionProfileShareBundle('[]')).toThrow(
      'Share bundle root must be an object',
    );
    expect(() =>
      parseConversionProfileShareBundle(
        JSON.stringify({ schemaVersion: 999, rulePacks: [], overlays: [] }),
      ),
    ).toThrow(/Unsupported share bundle schemaVersion/);
    expect(() =>
      parseConversionProfileShareBundle(
        JSON.stringify({ rulePacks: [], overlays: [] }),
      ),
    ).toThrow(/Unsupported share bundle schemaVersion: missing/);
    expect(() =>
      parseConversionProfileShareBundle(
        JSON.stringify({
          schemaVersion: CONVERSION_PROFILE_SHARE_BUNDLE_VERSION,
          overlays: [],
        }),
      ),
    ).toThrow('Share bundle rulePacks must be an array');
    expect(() =>
      parseConversionProfileShareBundle(
        JSON.stringify({
          schemaVersion: CONVERSION_PROFILE_SHARE_BUNDLE_VERSION,
          rulePacks: [],
        }),
      ),
    ).toThrow('Share bundle overlays must be an array');
    expect(() =>
      parseConversionProfileShareBundle(
        JSON.stringify({
          schemaVersion: CONVERSION_PROFILE_SHARE_BUNDLE_VERSION,
          rulePacks: [null],
          overlays: [],
        }),
      ),
    ).toThrow('Share bundle rule packs must be objects');
    expect(() =>
      parseConversionProfileShareBundle(
        JSON.stringify({
          schemaVersion: CONVERSION_PROFILE_SHARE_BUNDLE_VERSION,
          rulePacks: [
            {
              slug: '',
              profile: 'ICAO_2025',
              product: 'METAR',
              stage: 'lint',
              severity: 'warning',
            },
          ],
          overlays: [],
        }),
      ),
    ).toThrow(/rulePacks\[\]\.slug/);
    expect(() =>
      parseConversionProfileShareBundle(
        JSON.stringify({
          schemaVersion: CONVERSION_PROFILE_SHARE_BUNDLE_VERSION,
          rulePacks: [],
          overlays: [{ slug: 'ov', baseProfileId: 'ICAO_2025', body: [] }],
        }),
      ),
    ).toThrow('Share bundle overlay body must be an object');
    expect(() =>
      parseConversionProfileShareBundle(
        JSON.stringify({
          schemaVersion: CONVERSION_PROFILE_SHARE_BUNDLE_VERSION,
          rulePacks: [],
          overlays: [null],
        }),
      ),
    ).toThrow('Share bundle overlays must be objects');
    expect(() =>
      parseConversionProfileShareBundle(
        JSON.stringify({
          schemaVersion: CONVERSION_PROFILE_SHARE_BUNDLE_VERSION,
          rulePacks: [],
          overlays: [{ slug: 'ov', baseProfileId: 'ICAO_2025', shared: 'yes' }],
        }),
      ),
    ).toThrow('Share bundle overlay shared flag must be boolean when present');
    expect(() =>
      parseConversionProfileShareBundle(
        JSON.stringify({
          schemaVersion: CONVERSION_PROFILE_SHARE_BUNDLE_VERSION,
          rulePacks: [
            {
              slug: 'pack',
              profile: 'ICAO_2025',
              product: 'METAR',
              stage: 'lint',
              severity: 'warning',
              when: 123,
            },
          ],
          overlays: [],
        }),
      ),
    ).toThrow('Share bundle field must be a string when present: rulePacks[].when');
  });
});

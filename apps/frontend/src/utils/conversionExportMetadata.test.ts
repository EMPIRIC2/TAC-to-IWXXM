/**
 * conversionExportMetadata util tests (TC-EVPYL-005 / UJ-072h-export).
 */

import { afterEach, describe, expect, it, vi } from 'vitest';

import {
  CONVERSION_METADATA_PREFS_KEY,
  buildConversionExportMetadata,
  computeTacFingerprint,
  defaultConversionMetadataChecklist,
  defaultConversionMetadataPrefs,
  isConversionMetadataExportEnabled,
  jwtSubject,
  metaSidecarFileName,
  normalizeTacForFingerprint,
  readConversionMetadataPrefs,
  sanitizeMetadataForExport,
  serializeConversionMetadata,
  writeConversionMetadataPrefs,
} from './conversionExportMetadata';

const libraries = {
  conversionLibraryId: 'LIB.CONVERSION.ICAO_2025',
  tacValidationLibraryId: 'LIB.TAC_VALIDATION.ICAO_2025',
  iwxxmValidationLibraryId: 'LIB.IWXXM_VALIDATION.ICAO_2025',
  disseminationLibraryId: 'LIB.DISSEMINATION.ICAO_2025',
  decodingLibraryId: 'LIB.DECODING.ICAO_2025',
};

function b64urlJson(value: unknown): string {
  return btoa(JSON.stringify(value))
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/, '');
}

describe('conversionExportMetadata prefs', () => {
  afterEach(() => {
    localStorage.removeItem(CONVERSION_METADATA_PREFS_KEY);
  });

  it('defaults to opt-in off with full checklist', () => {
    expect(defaultConversionMetadataPrefs()).toEqual({
      enabled: false,
      checklist: defaultConversionMetadataChecklist(),
    });
    expect(readConversionMetadataPrefs()).toEqual(defaultConversionMetadataPrefs());
  });

  it('round-trips prefs through localStorage', () => {
    const prefs = {
      enabled: true,
      checklist: {
        ...defaultConversionMetadataChecklist(),
        operator: false,
      },
    };
    writeConversionMetadataPrefs(prefs);
    expect(readConversionMetadataPrefs()).toEqual(prefs);
  });

  it('falls back when storage is corrupt or partial', () => {
    localStorage.setItem(CONVERSION_METADATA_PREFS_KEY, '{not-json');
    expect(readConversionMetadataPrefs()).toEqual(defaultConversionMetadataPrefs());

    localStorage.setItem(
      CONVERSION_METADATA_PREFS_KEY,
      JSON.stringify('not-an-object'),
    );
    expect(readConversionMetadataPrefs()).toEqual(defaultConversionMetadataPrefs());

    localStorage.setItem(
      CONVERSION_METADATA_PREFS_KEY,
      JSON.stringify({ enabled: true, checklist: { libraries: false } }),
    );
    expect(readConversionMetadataPrefs()).toEqual({
      enabled: true,
      checklist: {
        ...defaultConversionMetadataChecklist(),
        libraries: false,
      },
    });

    localStorage.setItem(
      CONVERSION_METADATA_PREFS_KEY,
      JSON.stringify({ enabled: true, checklist: 'invalid' }),
    );
    expect(readConversionMetadataPrefs()).toEqual({
      enabled: true,
      checklist: defaultConversionMetadataChecklist(),
    });
  });

  it('ignores write failures without throwing', () => {
    vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => {
      throw new Error('quota');
    });
    expect(() =>
      writeConversionMetadataPrefs(defaultConversionMetadataPrefs()),
    ).not.toThrow();
    vi.restoreAllMocks();
  });

  it('reports enabled state from prefs', () => {
    expect(isConversionMetadataExportEnabled(defaultConversionMetadataPrefs())).toBe(
      false,
    );
    expect(
      isConversionMetadataExportEnabled({
        enabled: true,
        checklist: defaultConversionMetadataChecklist(),
      }),
    ).toBe(true);
  });
});

describe('metaSidecarFileName', () => {
  it('maps xml names to sibling meta.json', () => {
    expect(metaSidecarFileName('report.xml')).toBe('report.meta.json');
    expect(metaSidecarFileName('report_2.xml')).toBe('report_2.meta.json');
    expect(metaSidecarFileName('download')).toBe('download.meta.json');
    expect(metaSidecarFileName('')).toBe('download.meta.json');
  });
});

describe('jwtSubject', () => {
  it('extracts sub from a JWT payload', () => {
    const token = `header.${b64urlJson({ sub: 'user-123' })}.sig`;
    expect(jwtSubject(token)).toBe('user-123');
  });

  it('returns undefined for invalid tokens', () => {
    expect(jwtSubject(undefined)).toBeUndefined();
    expect(jwtSubject('')).toBeUndefined();
    expect(jwtSubject('not-a-jwt')).toBeUndefined();
    expect(jwtSubject(`bad.${b64urlJson('plain')}.sig`)).toBeUndefined();
    expect(jwtSubject(`bad.${b64urlJson({ sub: '   ' })}.sig`)).toBeUndefined();
    expect(jwtSubject('bad.%%%invalid-base64%%%.sig')).toBeUndefined();
    expect(jwtSubject(`bad.${b64urlJson(['not', 'record'])}.sig`)).toBeUndefined();
  });
});

describe('TAC fingerprint', () => {
  it('normalizes whitespace and case before hashing', () => {
    expect(normalizeTacForFingerprint('  metar   kjfk  ')).toBe('METAR KJFK');
    expect(computeTacFingerprint('METAR KJFK')).toBe(
      computeTacFingerprint('  metar   kjfk  '),
    );
  });

  it('returns stable fnv1a32 hex', () => {
    expect(computeTacFingerprint('METAR KJFK 121251Z')).toMatch(
      /^fnv1a32:[0-9a-f]{8}$/,
    );
  });
});

describe('buildConversionExportMetadata', () => {
  const baseInput = {
    tacContent: 'METAR KJFK 121251Z 28015KT 10SM FEW250',
    convertedAt: Date.parse('2026-09-15T12:00:00.000Z'),
    product: 'METAR',
    iwxxmVersion: '2025-2',
    reportVariant: '',
    libraries,
    checklist: defaultConversionMetadataChecklist(),
    isGuest: true,
    generatedAt: new Date('2026-09-15T12:01:00.000Z'),
  };

  it('includes all default groups for guests without operator identity', () => {
    const metadata = buildConversionExportMetadata(baseInput);
    expect(metadata.schemaVersion).toBe(1);
    expect(metadata.convert).toEqual({
      product: 'METAR',
      iwxxmVersion: '2025-2',
      convertedAt: '2026-09-15T12:00:00.000Z',
    });
    expect(metadata.libraries).toEqual(libraries);
    expect(metadata.libraryYamlHashes).toMatchObject({ status: 'placeholder' });
    expect(metadata.operator).toBeUndefined();
    expect(metadata.lintSummary).toMatchObject({ status: 'placeholder' });
    expect(metadata.tacFingerprint).toMatchObject({
      algorithm: 'fnv1a32-normalized-tac',
    });
    expect(metadata.mappingBridgeSummary).toMatchObject({ status: 'placeholder' });
  });

  it('includes operator identity when signed in and selected', () => {
    const token = `h.${b64urlJson({ sub: 'op-1' })}.s`;
    const metadata = buildConversionExportMetadata({
      ...baseInput,
      isGuest: false,
      userEmail: 'operator@example.com',
      accessToken: token,
    });
    expect(metadata.operator).toEqual({
      id: 'op-1',
      email: 'operator@example.com',
    });
  });

  it('includes operator email only when JWT sub is unavailable', () => {
    const metadata = buildConversionExportMetadata({
      ...baseInput,
      isGuest: false,
      userEmail: 'operator@example.com',
      accessToken: 'not-a-jwt',
    });
    expect(metadata.operator).toEqual({ email: 'operator@example.com' });
  });

  it('skips operator block when signed in but email is Guest placeholder', () => {
    const metadata = buildConversionExportMetadata({
      ...baseInput,
      isGuest: false,
      userEmail: 'Guest',
      accessToken: undefined,
    });
    expect(metadata.operator).toBeUndefined();
  });

  it('includes operator id only when email is unavailable', () => {
    const token = `h.${b64urlJson({ sub: 'op-only' })}.s`;
    const metadata = buildConversionExportMetadata({
      ...baseInput,
      isGuest: false,
      userEmail: 'Guest',
      accessToken: token,
    });
    expect(metadata.operator).toEqual({ id: 'op-only' });
  });

  it('defaults generatedAt when omitted', () => {
    const metadata = buildConversionExportMetadata({
      ...baseInput,
      generatedAt: undefined,
    });
    expect(typeof metadata.generatedAt).toBe('string');
  });

  it('omits operator when guest even if checklist operator is true', () => {
    const metadata = buildConversionExportMetadata({
      ...baseInput,
      isGuest: true,
      userEmail: 'operator@example.com',
      accessToken: 'token',
    });
    expect(metadata.operator).toBeUndefined();
  });

  it('respects unchecked checklist groups', () => {
    const metadata = buildConversionExportMetadata({
      ...baseInput,
      checklist: {
        libraries: false,
        libraryYamlHashes: false,
        convertContext: false,
        operator: false,
        lintSummary: false,
        tacFingerprint: false,
        mappingBridgeSummary: false,
      },
    });
    expect(metadata.convert).toBeUndefined();
    expect(metadata.libraries).toBeUndefined();
    expect(metadata.tacFingerprint).toBeUndefined();
  });

  it('includes lint counts when conversion log is present', () => {
    const metadata = buildConversionExportMetadata({
      ...baseInput,
      conversionLog: {
        errors: ['hard fail'],
        issues: [
          { code: 'W1', severity: 'warning', message: 'warn' },
          { code: 'I1', severity: 'info', message: 'info' },
          { code: 'E1', severity: 'error', message: 'err' },
        ],
      },
    });
    expect(metadata.lintSummary).toEqual({
      status: 'available',
      errorCount: 2,
      warningCount: 1,
      infoCount: 1,
      issueCount: 3,
    });
  });

  it('treats missing lint arrays as empty', () => {
    const metadata = buildConversionExportMetadata({
      ...baseInput,
      conversionLog: {},
    });
    expect(metadata.lintSummary).toEqual({
      status: 'available',
      errorCount: 0,
      warningCount: 0,
      infoCount: 0,
      issueCount: 0,
    });
  });

  it('includes report variant when set', () => {
    const metadata = buildConversionExportMetadata({
      ...baseInput,
      reportVariant: 'LWIS',
    });
    expect(metadata.convert).toMatchObject({ reportVariant: 'LWIS' });
  });
});

describe('sanitizeMetadataForExport', () => {
  it('strips forbidden keys and redacts suspicious string values', () => {
    const cleaned = sanitizeMetadataForExport({
      product: 'METAR',
      password: 'secret',
      nested: {
        token: 'abc',
        note: 'Bearer eyJhbGciOiJIUzI1NiJ9.test',
        safe: 'METAR KJFK',
      },
    });
    expect(cleaned).toEqual({
      product: 'METAR',
      nested: {
        note: '[redacted]',
        safe: 'METAR KJFK',
      },
    });
  });

  it('scrubs arrays and passes through primitives', () => {
    expect(
      sanitizeMetadataForExport({
        tags: ['ok', 'smtp://user:pass@host'],
        count: 2,
        enabled: true,
        empty: null,
      }),
    ).toEqual({
      tags: ['ok', '[redacted]'],
      count: 2,
      enabled: true,
      empty: null,
    });
  });
});

describe('serializeConversionMetadata', () => {
  it('pretty-prints JSON with trailing newline', () => {
    expect(serializeConversionMetadata({ a: 1 })).toBe('{\n  "a": 1\n}\n');
  });
});

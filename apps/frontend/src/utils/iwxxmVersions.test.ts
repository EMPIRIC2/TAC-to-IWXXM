import { describe, expect, it } from 'vitest';
import {
  CA_ECCC_IWXXM_VERSION,
  DEFAULT_IWXXM_VERSION,
  IWXXM_VERSION_OPTIONS,
  IWXXM_VERSIONS_SOT,
  coerceIwxxmVersion,
  coerceIwxxmVersionForProfile,
  isMscOperationalLine,
  iwxxmVersionOptionsForProfile,
  roleLabel,
  versionOptionLabel,
} from './iwxxmVersions';

describe('iwxxmVersions SoT (#851 / #854)', () => {
  it('exposes default and latest/previous roles from generated JSON', () => {
    expect(DEFAULT_IWXXM_VERSION).toBe(IWXXM_VERSIONS_SOT.default);
    expect(IWXXM_VERSIONS_SOT.versions.map((v) => v.role).sort()).toEqual([
      'latest',
      'previous',
    ]);
  });

  it('builds Latest / Previous option labels from roles', () => {
    const latest = IWXXM_VERSIONS_SOT.versions.find((v) => v.role === 'latest');
    const previous = IWXXM_VERSIONS_SOT.versions.find((v) => v.role === 'previous');
    expect(latest).toBeDefined();
    expect(previous).toBeDefined();
    expect(roleLabel('latest')).toBe('Latest');
    expect(roleLabel('previous')).toBe('Previous');
    expect(versionOptionLabel(latest!)).toBe(`${latest!.id} (Latest)`);
    expect(versionOptionLabel(previous!)).toBe(`${previous!.id} (Previous)`);
    expect(IWXXM_VERSION_OPTIONS.map((o) => o.label)).toEqual(
      IWXXM_VERSIONS_SOT.versions.map((v) => versionOptionLabel(v)),
    );
  });

  it('coerces unknown versions to SoT default', () => {
    expect(coerceIwxxmVersion('2023-1')).toBe('2023-1');
    expect(coerceIwxxmVersion('2.1')).toBe(DEFAULT_IWXXM_VERSION);
    expect(coerceIwxxmVersion(null)).toBe(DEFAULT_IWXXM_VERSION);
  });

  it('pins IWXXM 3.0.0 for Canadian operational lines', () => {
    const pinned = [
      {
        value: CA_ECCC_IWXXM_VERSION,
        label: '3.0.0 (CA MSC operational)',
        role: 'latest',
      },
    ];
    expect(iwxxmVersionOptionsForProfile('CA_ECCC')).toEqual(pinned);
    expect(iwxxmVersionOptionsForProfile('ca_eccc')).toEqual(pinned);
    expect(iwxxmVersionOptionsForProfile('CA_MSC_SIGMET')).toEqual(pinned);
    expect(iwxxmVersionOptionsForProfile('ca-msc-sigmet')).toEqual(pinned);
    expect(isMscOperationalLine('CA_ECCC')).toBe(true);
    expect(isMscOperationalLine('CA_MSC_SIGMET')).toBe(true);
    expect(isMscOperationalLine('ICAO_2025')).toBe(false);
    expect(coerceIwxxmVersionForProfile('CA_MSC_SIGMET', '2025-2')).toBe(
      CA_ECCC_IWXXM_VERSION,
    );
    expect(coerceIwxxmVersionForProfile('ICAO_2025', '2023-1')).toBe('2023-1');
    expect(iwxxmVersionOptionsForProfile('ICAO_2025')).toEqual(IWXXM_VERSION_OPTIONS);
  });
});

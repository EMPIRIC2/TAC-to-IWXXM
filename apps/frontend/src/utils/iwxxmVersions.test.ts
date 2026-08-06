import { describe, expect, it } from 'vitest';
import {
  DEFAULT_IWXXM_VERSION,
  IWXXM_VERSION_OPTIONS,
  IWXXM_VERSIONS_SOT,
  coerceIwxxmVersion,
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
});

/**
 * TC-EV093-001 / TC-EV093-003 — semantic profile catalog + coerce/hydrate (EV-093).
 *
 * [Corpus: tests] [Corpus: product §F35] [Corpus: adr/ADR-036]
 */
import { describe, expect, it } from 'vitest';
import {
  CANONICAL_SEMANTIC_PROFILES,
  DEFAULT_SEMANTIC_PROFILE,
  LEGACY_SEMANTIC_ALIASES,
  SEMANTIC_PROFILE_OPTIONS,
  coerceIwxxmProfile,
  hydrateSemanticProfile,
  isCaEcccProfile,
  wireSemanticProfile,
} from './semanticProfile';

describe('semanticProfile (TC-EV093-001 / TC-EV093-003)', () => {
  it('lists all canonicals plus legacy aliases with default ICAO_2025', () => {
    const values = SEMANTIC_PROFILE_OPTIONS.map((o) => o.value);
    for (const id of CANONICAL_SEMANTIC_PROFILES) {
      expect(values).toContain(id);
    }
    for (const alias of LEGACY_SEMANTIC_ALIASES) {
      expect(values).toContain(alias);
    }
    expect(DEFAULT_SEMANTIC_PROFILE).toBe('ICAO_2025');
    expect(values[0]).toBe('ICAO_2025');
  });

  it('coerces lowercase canonicals to uppercase OpenAPI ids', () => {
    expect(coerceIwxxmProfile('ca_eccc')).toBe('CA_ECCC');
    expect(coerceIwxxmProfile('au_bom')).toBe('AU_BOM');
    expect(coerceIwxxmProfile('ICAO_2025')).toBe('ICAO_2025');
  });

  it('keeps legacy aliases as distinct select values', () => {
    expect(coerceIwxxmProfile('annex3')).toBe('annex3');
    expect(coerceIwxxmProfile('iwxxm_us')).toBe('iwxxm_us');
    // Mixed / hyphenated forms miss the exact alias set but normalize to aliases.
    expect(coerceIwxxmProfile('ANNEX3')).toBe('annex3');
    expect(coerceIwxxmProfile('IWXXM-US')).toBe('iwxxm_us');
  });

  it('defaults unknown profile strings to ICAO_2025', () => {
    expect(coerceIwxxmProfile('not-a-profile')).toBe('ICAO_2025');
    expect(coerceIwxxmProfile('')).toBe('ICAO_2025');
    expect(coerceIwxxmProfile(null)).toBe('ICAO_2025');
  });

  it('hydrates aliases to canonical for prefs/sessions', () => {
    expect(hydrateSemanticProfile('annex3')).toBe('ICAO_2025');
    expect(hydrateSemanticProfile('iwxxm_us')).toBe('US_FAA_NWS');
    expect(hydrateSemanticProfile('ca_eccc')).toBe('CA_ECCC');
    expect(hydrateSemanticProfile(undefined)).toBe('ICAO_2025');
  });

  it('wires semantic_profile values for FormData', () => {
    expect(wireSemanticProfile('ICAO_2025')).toBe('ICAO_2025');
    expect(wireSemanticProfile('CA_ECCC')).toBe('CA_ECCC');
    expect(wireSemanticProfile('annex3')).toBe('annex3');
    expect(wireSemanticProfile(undefined)).toBe('ICAO_2025');
  });

  it('detects CA_ECCC for pin/metadata paths', () => {
    expect(isCaEcccProfile('CA_ECCC')).toBe(true);
    expect(isCaEcccProfile('ca_eccc')).toBe(true);
    expect(isCaEcccProfile('ICAO_2025')).toBe(false);
  });
});

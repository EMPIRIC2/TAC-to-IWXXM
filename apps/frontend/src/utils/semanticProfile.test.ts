/**
 * Semantic profile catalog after alias cutover (#1025) and national drop (M1).
 *
 * [Corpus: fr] epic #1688
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

describe('semanticProfile (#1025 alias removal)', () => {
  it('lists ICAO baseline only (no wire aliases)', () => {
    const values = SEMANTIC_PROFILE_OPTIONS.map((o) => o.value);
    expect(CANONICAL_SEMANTIC_PROFILES).toEqual(['ICAO_2025']);
    expect(LEGACY_SEMANTIC_ALIASES).toEqual([]);
    expect(values).toEqual(['ICAO_2025']);
    expect(DEFAULT_SEMANTIC_PROFILE).toBe('ICAO_2025');
  });

  it('coerces known ids and defaults dropped nationals to ICAO_2025', () => {
    expect(coerceIwxxmProfile('ICAO_2025')).toBe('ICAO_2025');
    expect(coerceIwxxmProfile('ca_eccc')).toBe('ICAO_2025');
    expect(coerceIwxxmProfile('au_bom')).toBe('ICAO_2025');
    expect(coerceIwxxmProfile('US_FAA_NWS')).toBe('ICAO_2025');
  });

  it('maps removed aliases annex3 / iwxxm_us to ICAO_2025', () => {
    expect(coerceIwxxmProfile('annex3')).toBe('ICAO_2025');
    expect(coerceIwxxmProfile('iwxxm_us')).toBe('ICAO_2025');
    expect(coerceIwxxmProfile('ANNEX3')).toBe('ICAO_2025');
    expect(coerceIwxxmProfile('IWXXM-US')).toBe('ICAO_2025');
  });

  it('defaults unknown profile strings to ICAO_2025', () => {
    expect(coerceIwxxmProfile('not-a-profile')).toBe('ICAO_2025');
    expect(coerceIwxxmProfile('')).toBe('ICAO_2025');
    expect(coerceIwxxmProfile(null)).toBe('ICAO_2025');
  });

  it('hydrates aliases and nationals to ICAO', () => {
    expect(hydrateSemanticProfile('annex3')).toBe('ICAO_2025');
    expect(hydrateSemanticProfile('iwxxm_us')).toBe('ICAO_2025');
    expect(hydrateSemanticProfile('ca_eccc')).toBe('ICAO_2025');
    expect(hydrateSemanticProfile(undefined)).toBe('ICAO_2025');
  });

  it('wires semantic_profile values for FormData', () => {
    expect(wireSemanticProfile('ICAO_2025')).toBe('ICAO_2025');
    expect(wireSemanticProfile('CA_ECCC')).toBe('ICAO_2025');
    expect(wireSemanticProfile('annex3')).toBe('ICAO_2025');
    expect(wireSemanticProfile(undefined)).toBe('ICAO_2025');
  });

  it('still detects CA_ECCC strings for leftover pin/metadata paths', () => {
    expect(isCaEcccProfile('CA_ECCC')).toBe(true);
    expect(isCaEcccProfile('ca_eccc')).toBe(true);
    expect(isCaEcccProfile('ICAO_2025')).toBe(false);
  });
});

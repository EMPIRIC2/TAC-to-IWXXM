/**
 * Semantic profile catalog + coerce/hydrate after national drop (FR-019..022 / M1).
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

describe('semanticProfile (M1 national drop)', () => {
  it('lists ICAO baseline plus annex3 alias only', () => {
    const values = SEMANTIC_PROFILE_OPTIONS.map((o) => o.value);
    expect(CANONICAL_SEMANTIC_PROFILES).toEqual(['ICAO_2025']);
    expect(LEGACY_SEMANTIC_ALIASES).toEqual(['annex3']);
    for (const id of CANONICAL_SEMANTIC_PROFILES) {
      expect(values).toContain(id);
    }
    for (const alias of LEGACY_SEMANTIC_ALIASES) {
      expect(values).toContain(alias);
    }
    expect(DEFAULT_SEMANTIC_PROFILE).toBe('ICAO_2025');
    expect(values[0]).toBe('ICAO_2025');
  });

  it('coerces known ids and defaults dropped nationals to ICAO_2025', () => {
    expect(coerceIwxxmProfile('ICAO_2025')).toBe('ICAO_2025');
    expect(coerceIwxxmProfile('ca_eccc')).toBe('ICAO_2025');
    expect(coerceIwxxmProfile('au_bom')).toBe('ICAO_2025');
    expect(coerceIwxxmProfile('US_FAA_NWS')).toBe('ICAO_2025');
  });

  it('keeps annex3 alias; maps dropped iwxxm_us to ICAO default', () => {
    expect(coerceIwxxmProfile('annex3')).toBe('annex3');
    expect(coerceIwxxmProfile('iwxxm_us')).toBe('ICAO_2025');
    expect(coerceIwxxmProfile('ANNEX3')).toBe('annex3');
    expect(coerceIwxxmProfile('IWXXM-US')).toBe('ICAO_2025');
  });

  it('defaults unknown profile strings to ICAO_2025', () => {
    expect(coerceIwxxmProfile('not-a-profile')).toBe('ICAO_2025');
    expect(coerceIwxxmProfile('')).toBe('ICAO_2025');
    expect(coerceIwxxmProfile(null)).toBe('ICAO_2025');
  });

  it('hydrates annex3 to ICAO; dropped nationals fall back to ICAO', () => {
    expect(hydrateSemanticProfile('annex3')).toBe('ICAO_2025');
    expect(hydrateSemanticProfile('iwxxm_us')).toBe('ICAO_2025');
    expect(hydrateSemanticProfile('ca_eccc')).toBe('ICAO_2025');
    expect(hydrateSemanticProfile(undefined)).toBe('ICAO_2025');
  });

  it('wires semantic_profile values for FormData', () => {
    expect(wireSemanticProfile('ICAO_2025')).toBe('ICAO_2025');
    expect(wireSemanticProfile('CA_ECCC')).toBe('ICAO_2025');
    expect(wireSemanticProfile('annex3')).toBe('annex3');
    expect(wireSemanticProfile(undefined)).toBe('ICAO_2025');
  });

  it('still detects CA_ECCC strings for leftover pin/metadata paths', () => {
    expect(isCaEcccProfile('CA_ECCC')).toBe(true);
    expect(isCaEcccProfile('ca_eccc')).toBe(true);
    expect(isCaEcccProfile('ICAO_2025')).toBe(false);
  });
});

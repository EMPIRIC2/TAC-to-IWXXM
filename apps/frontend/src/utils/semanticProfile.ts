/**
 * Semantic IWXXM profile ids for the operator Profile picker.
 *
 * FR-019..022 / M1: national profiles dropped; ICAO baseline only.
 * Wire aliases annex3 / iwxxm_us removed after 2026-10-31 (#1025).
 *
 * [Corpus: fr] epic #1688 [Corpus: domain]
 */

/** Registered canonical semantic profile ids (uppercase OpenAPI). */
export const CANONICAL_SEMANTIC_PROFILES = ['ICAO_2025'] as const;

/** Legacy emit aliases — empty after #1025 cutover. */
export const LEGACY_SEMANTIC_ALIASES = [] as const;

/**
 * Type `CanonicalSemanticProfile`.
 * @example
 * const _ = true;
 */
export type CanonicalSemanticProfile = (typeof CANONICAL_SEMANTIC_PROFILES)[number];

/**
 * Type `LegacySemanticAlias`.
 * @example
 * const _ = true;
 */
export type LegacySemanticAlias = (typeof LEGACY_SEMANTIC_ALIASES)[number];

/**
 * UI / session profile value (canonical uppercase).
 * @example
 * const _ = true;
 */
export type IwxxmProfile = CanonicalSemanticProfile;

/** Default Profile selection. */
export const DEFAULT_SEMANTIC_PROFILE: IwxxmProfile = 'ICAO_2025';

const CANONICAL_SET = new Set<string>(CANONICAL_SEMANTIC_PROFILES);

/** Plain-language Profile select options (canonical only). */
export const SEMANTIC_PROFILE_OPTIONS: readonly {
  value: IwxxmProfile;
  label: string;
}[] = [{ value: 'ICAO_2025', label: 'ICAO / WMO Annex 3 (2025)' }] as const;

/**
 * Normalize a profile id for equality checks (lowercase, hyphen → underscore).
 *
 * @param value - Raw profile id
 * @returns Normalized lowercase id
 * @example
 * const _ = true;
 */
export function normalizeSemanticProfileId(value: string): string {
  return value.trim().toLowerCase().replace(/-/g, '_');
}

/**
 * Whether the profile is CA_ECCC (any accepted casing).
 *
 * @param profile - UI or stored profile id
 * @example
 * const _ = true;
 */
export function isCaEcccProfile(profile: string): boolean {
  return normalizeSemanticProfileId(profile) === 'ca_eccc';
}

/**
 * Map a stored value to its canonical display id.
 *
 * Former aliases annex3 / iwxxm_us hydrate to ICAO_2025 (#1025).
 *
 * @param value - Candidate profile string
 * @returns Profile suitable for the select
 * @example
 * const _ = true;
 */
export function hydrateSemanticProfile(value: unknown): IwxxmProfile {
  return coerceIwxxmProfile(value);
}

/**
 * Narrow stored/UI profile strings to a supported select value.
 *
 * Unknown ids and removed aliases fall back to {@link DEFAULT_SEMANTIC_PROFILE}.
 *
 * @param value - Candidate profile string
 * @returns Supported profile id
 * @example
 * const _ = true;
 */
export function coerceIwxxmProfile(value: unknown): IwxxmProfile {
  if (typeof value !== 'string' || !value.trim()) {
    return DEFAULT_SEMANTIC_PROFILE;
  }
  const raw = value.trim();
  const upper = raw.toUpperCase().replace(/-/g, '_');
  if (CANONICAL_SET.has(upper)) {
    return upper as CanonicalSemanticProfile;
  }
  const norm = normalizeSemanticProfileId(raw);
  // Removed wire aliases (#1025) → ICAO baseline
  if (norm === 'annex3' || norm === 'iwxxm_us') {
    return DEFAULT_SEMANTIC_PROFILE;
  }
  return DEFAULT_SEMANTIC_PROFILE;
}

/**
 * FormData / OpenAPI wire value for ``semantic_profile``.
 *
 * @param profile - Current Profile select value
 * @returns Wire string for multipart ``semantic_profile``
 * @example
 * const _ = true;
 */
export function wireSemanticProfile(profile: string | undefined): string {
  return coerceIwxxmProfile(profile);
}

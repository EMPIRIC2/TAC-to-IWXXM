/**
 * Semantic IWXXM profile ids for the operator Profile picker (EV-093 / #1024).
 *
 * Canonical wire values are uppercase OpenAPI ids. Legacy aliases `annex3` /
 * `iwxxm_us` remain selectable through the #1025 deprecation window so alias
 * metrics still fire when chosen. Separate from exchange profiles (ADR-036).
 *
 * [Corpus: product §F35] [Corpus: product §F36] [Corpus: adr/ADR-036] [Corpus: api]
 */

/** Registered canonical semantic profile ids (uppercase OpenAPI). */
export const CANONICAL_SEMANTIC_PROFILES = [
  'ICAO_2025',
  'US_FAA_NWS',
  'CA_ECCC',
  'AU_BOM',
  'NZ_CAA_MET',
  'UK_METOFFICE',
  'BR_DECEA',
  'KR_KMA',
  'JP_JMA',
  'IN_IMD',
  'HK_HKO',
] as const;

/** Legacy emit aliases kept as distinct select values through #1025. */
export const LEGACY_SEMANTIC_ALIASES = ['annex3', 'iwxxm_us'] as const;

export type CanonicalSemanticProfile = (typeof CANONICAL_SEMANTIC_PROFILES)[number];

export type LegacySemanticAlias = (typeof LEGACY_SEMANTIC_ALIASES)[number];

/** UI / session profile value (canonical uppercase or legacy alias). */
export type IwxxmProfile = CanonicalSemanticProfile | LegacySemanticAlias;

/** Default Profile selection (canonical alias of former annex3 default). */
export const DEFAULT_SEMANTIC_PROFILE: IwxxmProfile = 'ICAO_2025';

const ALIAS_TO_CANONICAL: Record<LegacySemanticAlias, CanonicalSemanticProfile> = {
  annex3: 'ICAO_2025',
  iwxxm_us: 'US_FAA_NWS',
};

const CANONICAL_SET = new Set<string>(CANONICAL_SEMANTIC_PROFILES);
const ALIAS_SET = new Set<string>(LEGACY_SEMANTIC_ALIASES);

/** Plain-language Profile select options (canonicals first, then legacy aliases). */
export const SEMANTIC_PROFILE_OPTIONS: readonly {
  value: IwxxmProfile;
  label: string;
}[] = [
  { value: 'ICAO_2025', label: 'ICAO / WMO Annex 3 (2025)' },
  { value: 'US_FAA_NWS', label: 'United States (FAA/NWS)' },
  { value: 'CA_ECCC', label: 'Canada (ECCC)' },
  { value: 'AU_BOM', label: 'Australia (BoM)' },
  { value: 'NZ_CAA_MET', label: 'New Zealand (CAA MET)' },
  { value: 'UK_METOFFICE', label: 'United Kingdom (Met Office)' },
  { value: 'BR_DECEA', label: 'Brazil (DECEA)' },
  { value: 'KR_KMA', label: 'Republic of Korea (KMA)' },
  { value: 'JP_JMA', label: 'Japan (JMA)' },
  { value: 'IN_IMD', label: 'India (IMD)' },
  { value: 'HK_HKO', label: 'Hong Kong (HKO)' },
  { value: 'annex3', label: 'Annex 3 (legacy alias)' },
  { value: 'iwxxm_us', label: 'IWXXM-US (legacy alias)' },
] as const;

/**
 * Normalize a profile id for equality checks (lowercase, hyphen → underscore).
 *
 * @param value - Raw profile id
 * @returns Normalized lowercase id
 */
export function normalizeSemanticProfileId(value: string): string {
  return value.trim().toLowerCase().replace(/-/g, '_');
}

/**
 * Whether the profile is CA_ECCC (any accepted casing).
 *
 * @param profile - UI or stored profile id
 */
export function isCaEcccProfile(profile: string): boolean {
  return normalizeSemanticProfileId(profile) === 'ca_eccc';
}

/**
 * Map a stored alias to its canonical display id; leave other known ids as-is.
 *
 * Used when hydrating prefs / work sessions (FR-04).
 *
 * @param value - Candidate profile string
 * @returns Profile suitable for the select (canonical preferred over alias)
 */
export function hydrateSemanticProfile(value: unknown): IwxxmProfile {
  const coerced = coerceIwxxmProfile(value);
  if (ALIAS_SET.has(coerced)) {
    return ALIAS_TO_CANONICAL[coerced as LegacySemanticAlias];
  }
  return coerced;
}

/**
 * Narrow stored/UI profile strings to a supported select value.
 *
 * Keeps legacy aliases as distinct values so alias convert metrics still fire.
 * Lowercase canonicals (e.g. ``ca_eccc``) become uppercase OpenAPI ids.
 *
 * @param value - Candidate profile string
 * @returns Supported profile id (default {@link DEFAULT_SEMANTIC_PROFILE})
 */
export function coerceIwxxmProfile(value: unknown): IwxxmProfile {
  if (typeof value !== 'string' || !value.trim()) {
    return DEFAULT_SEMANTIC_PROFILE;
  }
  const raw = value.trim();
  if (ALIAS_SET.has(raw)) {
    return raw as LegacySemanticAlias;
  }
  const upper = raw.toUpperCase().replace(/-/g, '_');
  if (CANONICAL_SET.has(upper)) {
    return upper as CanonicalSemanticProfile;
  }
  const norm = normalizeSemanticProfileId(raw);
  if (norm === 'annex3') {
    return 'annex3';
  }
  if (norm === 'iwxxm_us') {
    return 'iwxxm_us';
  }
  return DEFAULT_SEMANTIC_PROFILE;
}

/**
 * FormData / OpenAPI wire value for ``semantic_profile``.
 *
 * Canonical options stay uppercase; legacy aliases stay lowercase emit keys.
 *
 * @param profile - Current Profile select value
 * @returns Wire string for multipart ``semantic_profile``
 */
export function wireSemanticProfile(profile: string | undefined): string {
  const coerced = coerceIwxxmProfile(profile);
  return coerced;
}

/**
 * Exchange packaging profile ids (ADR-036 / F35–F36).
 *
 * Separate from semantic {@link IwxxmProfile} — do not coerce GLOBAL_AFS into annex3.
 *
 * [Corpus: product §F36] [Corpus: adr/ADR-036] [Corpus: api]
 */

export type ExchangeProfileId =
  | 'GLOBAL_AFS'
  | 'APAC_ROBEX'
  | 'EUR_RODEX'
  | 'AFI'
  | 'CAR_SAM';

export const DEFAULT_EXCHANGE_PROFILE: ExchangeProfileId = 'GLOBAL_AFS';

export const EXCHANGE_PROFILE_OPTIONS: readonly {
  value: ExchangeProfileId;
  label: string;
}[] = [
  { value: 'GLOBAL_AFS', label: 'Global AFS (default)' },
  { value: 'APAC_ROBEX', label: 'APAC ROBEX' },
  { value: 'EUR_RODEX', label: 'EUR RODEX' },
  { value: 'AFI', label: 'AFI' },
  { value: 'CAR_SAM', label: 'CAR/SAM' },
] as const;

const KNOWN = new Set<string>(EXCHANGE_PROFILE_OPTIONS.map((o) => o.value));

/**
 * Coerce an unknown value to a known exchange profile wire id.
 *
 * @param value - Raw select / session / preference value
 * @returns Canonical wire id (defaults to GLOBAL_AFS)
 */
export function coerceExchangeProfile(value: unknown): ExchangeProfileId {
  if (typeof value === 'string' && KNOWN.has(value)) {
    return value as ExchangeProfileId;
  }
  return DEFAULT_EXCHANGE_PROFILE;
}

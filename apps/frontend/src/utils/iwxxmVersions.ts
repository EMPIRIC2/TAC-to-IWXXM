/**
 * IWXXM supported versions from Python SoT export (#851 / D-S046-sot).
 *
 * Regenerate: `make export-iwxxm-versions`
 * Artifact: `apps/frontend/src/generated/iwxxm_versions.json`
 */

import iwxxmVersionsJson from '@/generated/iwxxm_versions.json';

export type IwxxmVersionRole = 'latest' | 'previous';

export interface IwxxmVersionEntry {
  id: string;
  role: IwxxmVersionRole;
}

export interface IwxxmVersionsSoT {
  default: string;
  versions: IwxxmVersionEntry[];
}

/** Committed SoT payload (roles drive Latest / Previous labels). */
export const IWXXM_VERSIONS_SOT = iwxxmVersionsJson as IwxxmVersionsSoT;

/** Version ids as a union-friendly string list (runtime). */
export const IWXXM_VERSION_IDS = IWXXM_VERSIONS_SOT.versions.map((v) => v.id);

export type IwxxmVersionId = (typeof IWXXM_VERSION_IDS)[number];

/** Default IWXXM line (matches Python ``DEFAULT_VERSION``). */
export const DEFAULT_IWXXM_VERSION = IWXXM_VERSIONS_SOT.default as IwxxmVersionId;

/** MSC operational IWXXM line for CA_ECCC (EV-064). */
export const CA_ECCC_IWXXM_VERSION = '3.0.0' as const;

/**
 * Human label for a role — UJ-050 / #854.
 *
 * @param role - ``latest`` or ``previous`` from SoT
 * @returns Display role word
 */
export function roleLabel(role: IwxxmVersionRole): string {
  return role === 'latest' ? 'Latest' : 'Previous';
}

/**
 * Option label ``{id} ({Latest|Previous})``.
 *
 * @param entry - SoT version row
 * @returns Select option text
 */
export function versionOptionLabel(entry: IwxxmVersionEntry): string {
  return `${entry.id} (${roleLabel(entry.role)})`;
}

/** Ordered select options from SoT. */
export const IWXXM_VERSION_OPTIONS = IWXXM_VERSIONS_SOT.versions.map((entry) => ({
  value: entry.id as IwxxmVersionId,
  label: versionOptionLabel(entry),
  role: entry.role,
}));

/**
 * Narrow unknown prefs / form values to a supported SoT id.
 *
 * @param value - Candidate version string
 * @returns Supported id or SoT default
 */
export function coerceIwxxmVersion(value: unknown): IwxxmVersionId {
  if (typeof value === 'string' && IWXXM_VERSION_IDS.includes(value)) {
    return value as IwxxmVersionId;
  }
  return DEFAULT_IWXXM_VERSION;
}

/**
 * IWXXM version select options for the active semantic profile.
 *
 * @param profile - UI profile emit key
 * @returns Version options (CA_ECCC pins 3.0.0 only)
 */
export function iwxxmVersionOptionsForProfile(profile: string) {
  if (profile === 'ca_eccc') {
    return [
      {
        value: CA_ECCC_IWXXM_VERSION,
        label: '3.0.0 (CA MSC operational)',
        role: 'latest' as IwxxmVersionRole,
      },
    ];
  }
  return IWXXM_VERSION_OPTIONS;
}

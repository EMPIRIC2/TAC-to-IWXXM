/**
 * Semantic profile wire helpers (EV-073 M2 / #1042; EV-093 uppercase ids).
 *
 * Maps UI profile selection to API extension tokens and exchange packaging flags.
 */

import { isCaEcccProfile, type IwxxmProfile } from '@/utils/semanticProfile';

/** National extension token for full Canadian XSD validation stack. */
export const CA_ECCC_NATIONAL_EXTENSION = 'IWXXM_CA';

/** Products supported under CA_ECCC in the operator workbench. */
export const CA_ECCC_SUPPORTED_PRODUCTS = ['METAR', 'SPECI', 'TAF', 'AIRMET'] as const;

/**
 * National extension tokens to send for the active profile.
 *
 * @param profile - UI semantic profile id
 */
export function nationalExtensionsForProfile(profile: IwxxmProfile | string): string[] {
  return isCaEcccProfile(profile) ? [CA_ECCC_NATIONAL_EXTENSION] : [];
}

/**
 * Whether convert should request MSC COLLECT exchange output wrapping.
 *
 * @param profile - UI semantic profile id
 */
export function exchangeOutputForProfile(profile: IwxxmProfile | string): boolean {
  return isCaEcccProfile(profile);
}

/**
 * Operator-visible national extension label (no internal planning ids).
 */
export const CA_ECCC_EXTENSION_LABEL = 'Canadian national IWXXM extensions';

/**
 * Confirm + reset library ids when the Convert national line / semantic profile changes (#1251 T3.1).
 */

import { libraryIdsForNationalLine } from './libraryIds';
import {
  coerceIwxxmProfile,
  type IwxxmProfile,
  wireSemanticProfile,
} from './semanticProfile';
import { CONVERT_PROFILE_LIBRARY_RESET_CONFIRM } from './conversionProfilesCopy';

/**
 * Type for the library id fields stored on Convert params.
 * @example
 * const _ = true;
 */
export type ConvertLibraryIdFields = {
  conversionLibraryId: string;
  tacValidationLibraryId: string;
  iwxxmValidationLibraryId: string;
  disseminationLibraryId: string;
  decodingLibraryId: string;
};

/**
 * Whether changing to ``nextNationalLine`` is a different semantic profile wire id.
 *
 * @param previousProfile - Current Convert profile
 * @param nextNationalLine - National line from a LIB.* conversion selection
 * @example
 * const _ = true;
 */
export function isSemanticProfileLineChange(
  previousProfile: string,
  nextNationalLine: string,
): boolean {
  return coerceIwxxmProfile(previousProfile) !== coerceIwxxmProfile(nextNationalLine);
}

/**
 * Ask the operator to confirm resetting all library selects to a national line.
 *
 * @param nextNationalLine - Target national line (e.g. US_FAA_NWS)
 * @param confirmFn - Injectable confirm (defaults to ``window.confirm``)
 * @returns Whether the operator confirmed
 * @example
 * const _ = true;
 */
export function confirmLibraryResetForProfile(
  nextNationalLine: string,
  confirmFn: (message: string) => boolean = (message) => window.confirm(message),
): boolean {
  const line = coerceIwxxmProfile(nextNationalLine);
  return confirmFn(CONVERT_PROFILE_LIBRARY_RESET_CONFIRM(line));
}

const SESSION_LIBRARY_KEYS = [
  ['conversionLibraryId', 'conversion_library_id'],
  ['tacValidationLibraryId', 'tac_validation_library_id'],
  ['iwxxmValidationLibraryId', 'iwxxm_validation_library_id'],
  ['disseminationLibraryId', 'dissemination_library_id'],
  ['decodingLibraryId', 'decoding_library_id'],
] as const;

/**
 * Read persisted Convert library ids from a work-session params blob.
 *
 * @param params - ``conversion_params`` (camelCase or snake_case)
 * @returns Present library id fields only
 * @example
 * const _ = true;
 */
export function libraryIdsFromSessionParams(
  params: Record<string, unknown>,
): Partial<ConvertLibraryIdFields> {
  const out: Partial<ConvertLibraryIdFields> = {};
  for (const [camel, snake] of SESSION_LIBRARY_KEYS) {
    const raw = params[camel] ?? params[snake];
    if (typeof raw === 'string' && raw.trim()) {
      out[camel] = raw.trim();
    }
  }
  return out;
}

/**
 * Build Convert library id fields for a national line after a confirmed profile change.
 *
 * @param nextNationalLine - Target national line
 * @returns Library ids + coerced profile
 * @example
 * const _ = true;
 */
export function libraryResetForProfile(nextNationalLine: string): {
  profile: IwxxmProfile;
  libraryIds: ConvertLibraryIdFields;
} {
  const profile = coerceIwxxmProfile(nextNationalLine);
  return {
    profile,
    libraryIds: libraryIdsForNationalLine(wireSemanticProfile(profile)),
  };
}

/** National lines that have a matching built-in four-library set. */
export const COUNTRY_PRESET_LINES = ['ICAO_2025', 'US_FAA_NWS', 'CA_ECCC'] as const;

/**
 * National line when TAC validation, conversion, decoding, and IWXXM validation match one preset.
 *
 * Dissemination is ignored. A mixed set returns an empty string.
 *
 * @param ids - Current Convert library ids
 * @returns Matching preset line, or ``''`` when the four libraries do not match
 * @example
 * const _ = true;
 */
export function countryPresetLineForLibraries(
  ids: Pick<
    ConvertLibraryIdFields,
    | 'conversionLibraryId'
    | 'tacValidationLibraryId'
    | 'iwxxmValidationLibraryId'
    | 'decodingLibraryId'
  >,
): (typeof COUNTRY_PRESET_LINES)[number] | '' {
  for (const line of COUNTRY_PRESET_LINES) {
    const expected = libraryIdsForNationalLine(line);
    if (
      ids.conversionLibraryId === expected.conversionLibraryId &&
      ids.tacValidationLibraryId === expected.tacValidationLibraryId &&
      ids.iwxxmValidationLibraryId === expected.iwxxmValidationLibraryId &&
      ids.decodingLibraryId === expected.decodingLibraryId
    ) {
      return line;
    }
  }
  return '';
}

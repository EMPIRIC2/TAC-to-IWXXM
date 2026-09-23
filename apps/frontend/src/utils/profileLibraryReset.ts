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

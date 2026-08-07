/**
 * Operator dissemination / DB destination UI (F16–F19 drawer + Convert&Send +
 * Upload to Database / DatabaseUploadDialog).
 *
 * EV-042 / #897: temporarily hidden (11-verify-impl: include Upload to Database).
 * Restore via #898 by flipping ``destinationsEnabled`` to ``true`` (or delete this gate).
 * Backend ``/api/v1/dissemination/*`` remains for harness/tests.
 *
 * Mutable config supports Vitest coverage of Convert&Send / upload dialog while the
 * operator default stays off.
 *
 * [Corpus: product §F16–F19] [Corpus: journeys UJ-053]
 */

export const operatorDisseminationUiConfig = {
  /** When false, Convert&Send + Disseminate + Upload to Database are hidden. */
  destinationsEnabled: false,
};

export function isOperatorDisseminationDestinationsEnabled(): boolean {
  return operatorDisseminationUiConfig.destinationsEnabled;
}

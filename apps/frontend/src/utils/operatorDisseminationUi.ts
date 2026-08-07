/**
 * Operator dissemination destination UI (F16–F19 drawer + Convert&Send).
 *
 * EV-042 / #897: temporarily hidden. Restore via #898 by flipping
 * ``destinationsEnabled`` to ``true`` (or delete this gate).
 * Backend ``/api/v1/dissemination/*`` remains for harness/tests.
 *
 * Mutable config supports Vitest coverage of Convert&Send while the operator
 * default stays off.
 *
 * [Corpus: product §F16–F19] [Corpus: journeys UJ-053]
 */

export const operatorDisseminationUiConfig = {
  /** When false, Convert&Send + DisseminationDrawer entry are hidden. */
  destinationsEnabled: false,
};

export function isOperatorDisseminationDestinationsEnabled(): boolean {
  return operatorDisseminationUiConfig.destinationsEnabled;
}

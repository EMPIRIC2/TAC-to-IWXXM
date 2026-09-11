/**
 * Operator dissemination / DB destination UI (F16–F19 drawer + Convert&Send).
 *
 * EV-091 / #898: destinations restored (Convert&Send, Disseminate).
 * EV-beta-ux-export-auth: Upload to Database toolbar control removed.
 * Mutable config supports Vitest isolation (set ``destinationsEnabled`` false to assert
 * the EV-042 hide gate still works).
 *
 * Backend ``/api/v1/dissemination/*`` remains for harness/tests.
 *
 * [Corpus: product §F16–F19] [Corpus: journeys UJ-027–030]
 */

export const operatorDisseminationUiConfig = {
  /** When false, Convert&Send + Disseminate are hidden. */
  destinationsEnabled: true,
};

/**
 * Whether operator Convert&Send / Disseminate are shown.
 *
 * @returns true when destinations UI is enabled (default after EV-091)
 */
export function isOperatorDisseminationDestinationsEnabled(): boolean {
  return operatorDisseminationUiConfig.destinationsEnabled;
}

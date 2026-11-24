/**
 * Operator dissemination / DB destination UI (F16–F19 drawer + Convert&Send).
 *
 * EV-091 / #898: destinations restored (Convert&Send, Disseminate).
 * EV-beta-ux-export-auth: Upload to Database toolbar control removed.
 * Mutable config supports Vitest isolation (set ``destinationsEnabled`` false to assert
 * the EV-042 hide gate still works).
 *
 * FR-052..056 / DI-008: dissemination drawer deferred; destinations stay off.
 * Backend ``/api/v1/dissemination/*`` routes are unregistered.
 *
 * [Corpus: fr] epic #1688
 */

export const operatorDisseminationUiConfig = {
  /** When false, Convert&Send + Disseminate are hidden. */
  destinationsEnabled: false,
};

/**
 * Whether operator Convert&Send / Disseminate are shown.
 *
 * @returns true when destinations UI is enabled (default false; FR drop)
 * @example
 * const _ = true;
 */
export function isOperatorDisseminationDestinationsEnabled(): boolean {
  return operatorDisseminationUiConfig.destinationsEnabled;
}

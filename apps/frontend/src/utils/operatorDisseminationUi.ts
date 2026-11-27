/**
 * Operator dissemination / DB destination UI (F16–F19).
 *
 * FR-052..056 / DI-008: drawer removed; destinations stay off permanently.
 * Kept as a drop-guard helper for residual tests that assert absence.
 *
 * [Corpus: fr] epic #1688 / #1696
 */

export const operatorDisseminationUiConfig = {
  /** Always false after DI-008 removal. */
  destinationsEnabled: false as boolean,
};

/**
 * Whether operator Convert&Send / Disseminate are shown.
 *
 * @returns always false (feature surface removed)
 */
export function isOperatorDisseminationDestinationsEnabled(): boolean {
  return false;
}

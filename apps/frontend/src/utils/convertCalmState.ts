/**
 * Calmer Convert phase helpers (EV-calmer-convert-tutorial-caribbean / UJ-088).
 *
 * [Corpus: product §F7] [Corpus: tests §TC-UX-CALM]
 */

export type CalmConvertPhase = 'empty' | 'editing' | 'postSuccess';

export type CalmPrimaryKind = 'convert' | 'download';

export interface CalmConvertInputs {
  /** True when TAC/manual input or pending files are present. */
  hasInput: boolean;
  /** True when at least one converted result is in the queue. */
  hasConverted: boolean;
  /** True when the newest result is publishable / downloadable as valid IWXXM. */
  latestReadyToDownload?: boolean;
}

export interface CalmConvertUi {
  phase: CalmConvertPhase;
  primaryKind: CalmPrimaryKind;
  showEmptyHero: boolean;
  showValidityStrip: boolean;
  hideAdvancedSetup: boolean;
}

/**
 * Derive calm Convert chrome phase from workbench state.
 *
 * @param input - Input / convert / readiness flags
 * @returns Phase and CTA choreography for Calmer Convert
 */
export function deriveCalmConvertUi(input: CalmConvertInputs): CalmConvertUi {
  const { hasInput, hasConverted, latestReadyToDownload = hasConverted } = input;
  if (!hasInput && !hasConverted) {
    return {
      phase: 'empty',
      primaryKind: 'convert',
      showEmptyHero: true,
      showValidityStrip: false,
      hideAdvancedSetup: true,
    };
  }
  if (hasConverted && latestReadyToDownload) {
    return {
      phase: 'postSuccess',
      primaryKind: 'download',
      showEmptyHero: false,
      showValidityStrip: true,
      hideAdvancedSetup: false,
    };
  }
  return {
    phase: 'editing',
    primaryKind: 'convert',
    showEmptyHero: false,
    showValidityStrip: false,
    hideAdvancedSetup: false,
  };
}

/** Primary button label for Convert modes (not IWXXM validate-only). */
export const CALM_CONVERT_PRIMARY_LABEL = 'Convert & validate';

/** Primary button label after successful convert. */
export const CALM_DOWNLOAD_PRIMARY_LABEL = 'Download IWXXM';

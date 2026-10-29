/**
 * Calmer Convert phase helpers (EV-calmer-convert-tutorial-caribbean / UJ-088).
 *
 * [Corpus: product §F7] [Corpus: tests §TC-UX-CALM]
 */

/**
 * Convert workbench phase for calm chrome.
 * @example
 * const _ = true;
 */
export type CalmConvertPhase = 'empty' | 'editing' | 'postSuccess';

/**
 * Which primary CTA the strip should emphasize.
 * @example
 * const _ = true;
 */
export type CalmPrimaryKind = 'convert' | 'download';

/**
 * Inputs that drive calm Convert chrome.
 * @example
 * const _ = true;
 */
export interface CalmConvertInputs {
  /** True when TAC/manual input or pending files are present. */
  hasInput: boolean;
  /** True when at least one converted result is in the queue. */
  hasConverted: boolean;
  /** True when the newest result is publishable / downloadable as valid IWXXM. */
  latestReadyToDownload?: boolean;
}

/**
 * Derived calm Convert UI flags.
 * @example
 * const _ = true;
 */
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
 * @example
 * const _ = true;
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
      // Validity notes live in the results Console tab (UJ-089).
      showValidityStrip: false,
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
export const CALM_CONVERT_PRIMARY_LABEL = 'Convert';

/** Primary button label after successful convert (latest single result). */
export const CALM_DOWNLOAD_PRIMARY_LABEL = 'Download latest';
/** Fallback when the active profile id is not in the semantic options list. */
export const CALM_PROFILE_LABEL_FALLBACK = 'International (ICAO)';

/**
 * Resolve a human profile label for the empty-hero footer.
 *
 * @param profileId - Active semantic profile id
 * @param options - Profile option rows with value/label
 * @returns Display label
 * @example
 * const _ = true;
 */
export function resolveCalmProfileLabel(
  profileId: string,
  options: readonly { value: string; label: string }[],
): string {
  return (
    options.find((option) => option.value === profileId)?.label ??
    CALM_PROFILE_LABEL_FALLBACK
  );
}

/**
 * Build empty-hero example chips from a product→example lookup.
 *
 * @param chips - Label + product pairs to offer
 * @param lookup - Returns the first example id for a product, or undefined
 * @returns Chips with concrete example ids
 * @example
 * const _ = true;
 */
export function buildCalmExampleChips(
  chips: readonly { label: string; product: string }[],
  lookup: (product: string) => { id: string } | undefined,
): { id: string; label: string }[] {
  const out: { id: string; label: string }[] = [];
  for (const chip of chips) {
    const example = lookup(chip.product);
    if (example) {
      out.push({ id: example.id, label: chip.label });
    }
  }
  return out;
}

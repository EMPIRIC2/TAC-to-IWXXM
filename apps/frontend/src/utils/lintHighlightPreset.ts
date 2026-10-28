/**
 * Lint span highlight color presets (UJ-089 / TC-UX-DECLUTTER-008).
 *
 * [Corpus: product §F7]
 */

/**
 * Supported lint highlight presets.
 * @example
 * const _ = true;
 */
export type LintHighlightPreset = 'default' | 'colorblind';

export const LINT_HIGHLIGHT_PRESET_STORAGE_KEY = 'tac-to-iwxxm.lint-highlight.preset';

/**
 * CSS custom properties for CodeMirror issue marks.
 * @example
 * const _ = true;
 */
export type LintHighlightTokens = {
  issueBg: string;
  issueBorder: string;
  infoBg: string;
  infoBorder: string;
  selectedBg: string;
  selectedBorder: string;
};

const PRESETS: Record<LintHighlightPreset, LintHighlightTokens> = {
  default: {
    issueBg: 'rgba(251, 191, 36, 0.45)',
    issueBorder: '#f59e0b',
    infoBg: 'rgba(249, 115, 22, 0.35)',
    infoBorder: '#ea580c',
    selectedBg: 'rgba(234, 179, 8, 0.5)',
    selectedBorder: '#ca8a04',
  },
  colorblind: {
    issueBg: 'rgba(217, 119, 6, 0.45)',
    issueBorder: '#b45309',
    infoBg: 'rgba(124, 58, 237, 0.35)',
    infoBorder: '#6d28d9',
    selectedBg: 'rgba(5, 150, 105, 0.45)',
    selectedBorder: '#047857',
  },
};

/**
 * Resolve tokens for a preset id.
 *
 * @param preset - Preset id
 * @returns Theme tokens
 * @example
 * const _ = true;
 */
export function lintHighlightTokens(preset: LintHighlightPreset): LintHighlightTokens {
  return PRESETS[preset];
}

/**
 * Whether a browser `window` is available (SSR-safe).
 *
 * @param g - Global-like object to inspect
 * @returns True when `window` is defined
 * @example
 * const _ = true;
 */
export function isBrowserEnv(
  g: { window?: unknown } = globalThis as { window?: unknown },
): boolean {
  return typeof g.window !== 'undefined';
}

/**
 * Read a stored preset from localStorage.
 *
 * @param browser - Override browser detection (tests)
 * @returns Preset id
 * @example
 * const _ = true;
 */
export function readLintHighlightPreset(
  browser: boolean = isBrowserEnv(),
): LintHighlightPreset {
  if (!browser) {
    return 'default';
  }
  try {
    const raw = window.localStorage.getItem(LINT_HIGHLIGHT_PRESET_STORAGE_KEY);
    if (raw === 'colorblind' || raw === 'default') {
      return raw;
    }
  } catch {
    /* ignore */
  }
  return 'default';
}

/**
 * Persist a lint highlight preset.
 *
 * @param preset - Preset to store
 * @param browser - Override browser detection (tests)
 * @example
 * const _ = true;
 */
export function writeLintHighlightPreset(
  preset: LintHighlightPreset,
  browser: boolean = isBrowserEnv(),
): void {
  if (!browser) {
    return;
  }
  try {
    window.localStorage.setItem(LINT_HIGHLIGHT_PRESET_STORAGE_KEY, preset);
  } catch {
    /* ignore */
  }
}

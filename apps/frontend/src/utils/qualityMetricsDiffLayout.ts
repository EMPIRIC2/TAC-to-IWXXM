/**
 * Quality metrics XML diff layout preference (F7.q / EV-058 / #983).
 *
 * Persist Inline (unified) vs Side-by-side in localStorage; derive side-by-side
 * rows from {@link unifiedLineDiff} without a new npm diff package.
 */

import type { UnifiedDiffLine } from './unifiedLineDiff';

/** localStorage key for diff layout preference (`D-S068-01-ac=2b`). */
export const QUALITY_METRICS_DIFF_LAYOUT_STORAGE_KEY =
  'tac-to-iwxxm.quality-metrics.diff-layout';

/** Diff layout modes on `/quality/:stem`. */
export type QualityMetricsDiffLayout = 'unified' | 'side-by-side';

/** One aligned row for side-by-side rendering. */
export type SideBySideDiffRow = {
  /** Left (official) line text, or null when only converted added a line. */
  left: string | null;
  /** Right (converted) line text, or null when only official removed a line. */
  right: string | null;
  /** Left gutter highlight. */
  leftOp: 'equal' | 'remove' | 'empty';
  /** Right gutter highlight. */
  rightOp: 'equal' | 'add' | 'empty';
};

/**
 * Parse a stored layout value; unknown values fall back to unified.
 *
 * @param raw - Raw localStorage string
 * @returns Valid layout mode
 */
export function parseDiffLayout(
  raw: string | null | undefined,
): QualityMetricsDiffLayout {
  return raw === 'side-by-side' ? 'side-by-side' : 'unified';
}

/**
 * Read preferred layout from localStorage (SSR-safe).
 *
 * @returns Stored preference or unified default
 */
export function readDiffLayoutPreference(): QualityMetricsDiffLayout {
  if (typeof window === 'undefined' || !window.localStorage) {
    return 'unified';
  }
  try {
    return parseDiffLayout(
      window.localStorage.getItem(QUALITY_METRICS_DIFF_LAYOUT_STORAGE_KEY),
    );
  } catch {
    return 'unified';
  }
}

/**
 * Persist layout preference to localStorage (best-effort).
 *
 * @param layout - Selected layout
 */
export function writeDiffLayoutPreference(layout: QualityMetricsDiffLayout): void {
  if (typeof window === 'undefined' || !window.localStorage) {
    return;
  }
  try {
    window.localStorage.setItem(QUALITY_METRICS_DIFF_LAYOUT_STORAGE_KEY, layout);
  } catch {
    // Quota / private mode — preference is session-only.
  }
}

/**
 * Build side-by-side rows from a unified line diff (same LCS source as inline).
 *
 * @param lines - Output of {@link unifiedLineDiff}
 * @returns Aligned left/right rows
 */
export function sideBySideFromUnified(lines: UnifiedDiffLine[]): SideBySideDiffRow[] {
  const rows: SideBySideDiffRow[] = [];
  let i = 0;
  while (i < lines.length) {
    const line = lines[i]!;
    if (line.op === 'equal') {
      rows.push({
        left: line.text,
        right: line.text,
        leftOp: 'equal',
        rightOp: 'equal',
      });
      i += 1;
      continue;
    }
    // Pair consecutive remove+add as a changed line when both present.
    if (line.op === 'remove') {
      const next = lines[i + 1];
      if (next?.op === 'add') {
        rows.push({
          left: line.text,
          right: next.text,
          leftOp: 'remove',
          rightOp: 'add',
        });
        i += 2;
        continue;
      }
      rows.push({
        left: line.text,
        right: null,
        leftOp: 'remove',
        rightOp: 'empty',
      });
      i += 1;
      continue;
    }
    // add without preceding remove
    rows.push({
      left: null,
      right: line.text,
      leftOp: 'empty',
      rightOp: 'add',
    });
    i += 1;
  }
  return rows;
}

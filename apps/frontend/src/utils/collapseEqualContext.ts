/**
 * GitHub-style equal-context collapse for unified line diffs (F7.q / EV-056).
 *
 * Keeps `context` equal lines around each change hunk; collapses longer equal runs.
 */

import type { UnifiedDiffLine } from './unifiedLineDiff';

/** Default equal lines kept around each change hunk (`D-S066-context-n=1`). */
export const DEFAULT_DIFF_CONTEXT = 3;

export type CollapsedDiffSegment =
  | {
      /** Visible contiguous lines (mix of equal/add/remove within a hunk window). */
      type: 'lines';
      /** Inclusive start index into the original unified diff. */
      startIndex: number;
      /** Lines to render. */
      lines: UnifiedDiffLine[];
    }
  | {
      /** Collapsed run of equal lines. */
      type: 'collapse';
      /** Inclusive start index into the original unified diff. */
      startIndex: number;
      /** Hidden equal lines (expand restores these). */
      lines: UnifiedDiffLine[];
    };

export type CollapseEqualContextOptions = {
  /** Equal lines retained on each side of a change (default {@link DEFAULT_DIFF_CONTEXT}). */
  context?: number;
};

/**
 * Mark which unified-diff indices stay visible given context around changes.
 *
 * @param lines - Unified diff lines
 * @param context - Equal lines kept around each non-equal line
 * @returns Boolean mask aligned with `lines`
 */
export function visibleEqualContextMask(
  lines: UnifiedDiffLine[],
  context: number = DEFAULT_DIFF_CONTEXT,
): boolean[] {
  const n = lines.length;
  const visible = Array.from({ length: n }, () => false);
  const ctx = Math.max(0, context);

  for (let i = 0; i < n; i += 1) {
    if (lines[i]?.op !== 'equal') {
      const from = Math.max(0, i - ctx);
      const to = Math.min(n - 1, i + ctx);
      for (let j = from; j <= to; j += 1) {
        visible[j] = true;
      }
    }
  }

  // All-equal (or empty) diffs: show everything — caller usually short-circuits empty.
  if (!visible.some(Boolean) && n > 0) {
    return Array.from({ length: n }, () => true);
  }

  return visible;
}

/**
 * Collapse long equal runs outside change hunks into expand-able segments.
 *
 * @param lines - Output of {@link unifiedLineDiff}
 * @param options.context - Equal lines kept around each change (default 3)
 * @returns Segments for rendering (lines vs collapse placeholders)
 */
export function collapseEqualContext(
  lines: UnifiedDiffLine[],
  options: CollapseEqualContextOptions = {},
): CollapsedDiffSegment[] {
  const context = options.context ?? DEFAULT_DIFF_CONTEXT;
  if (lines.length === 0) {
    return [];
  }

  const visible = visibleEqualContextMask(lines, context);
  const segments: CollapsedDiffSegment[] = [];
  let i = 0;

  while (i < lines.length) {
    if (visible[i]) {
      const startIndex = i;
      const chunk: UnifiedDiffLine[] = [];
      while (i < lines.length && visible[i]) {
        chunk.push(lines[i]!);
        i += 1;
      }
      segments.push({ type: 'lines', startIndex, lines: chunk });
      continue;
    }

    const startIndex = i;
    const hidden: UnifiedDiffLine[] = [];
    while (i < lines.length && !visible[i]) {
      hidden.push(lines[i]!);
      i += 1;
    }
    segments.push({ type: 'collapse', startIndex, lines: hidden });
  }

  return segments;
}

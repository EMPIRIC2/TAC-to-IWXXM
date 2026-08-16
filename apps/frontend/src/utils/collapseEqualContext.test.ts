/**
 * Unit tests for GitHub-style equal-context collapse (TC-EV056-003).
 */

import { describe, expect, it } from 'vitest';
import {
  collapseEqualContext,
  DEFAULT_DIFF_CONTEXT,
  visibleEqualContextMask,
} from './collapseEqualContext';
import { unifiedLineDiff, type UnifiedDiffLine } from './unifiedLineDiff';

function equals(n: number): UnifiedDiffLine[] {
  return Array.from({ length: n }, (_, i) => ({
    op: 'equal' as const,
    text: `eq${i}`,
    leftLine: i + 1,
    rightLine: i + 1,
  }));
}

describe('collapseEqualContext', () => {
  it('defaults context to 3', () => {
    expect(DEFAULT_DIFF_CONTEXT).toBe(3);
  });

  it('returns no segments for an empty diff and uses default options', () => {
    expect(collapseEqualContext([])).toEqual([]);
    const segments = collapseEqualContext(equals(2));
    expect(segments).toHaveLength(1);
    expect(segments[0]?.type).toBe('lines');
  });

  it('treats a negative context as zero', () => {
    const lines: UnifiedDiffLine[] = [
      { op: 'equal', text: 'a', leftLine: 1, rightLine: 1 },
      { op: 'add', text: 'b', leftLine: null, rightLine: 2 },
      { op: 'equal', text: 'c', leftLine: 2, rightLine: 3 },
    ];
    const mask = visibleEqualContextMask(lines, -1);
    expect(mask).toEqual([false, true, false]);
  });

  it('shows all lines when there are no changes', () => {
    const lines = equals(10);
    const segments = collapseEqualContext(lines, { context: 3 });
    expect(segments).toHaveLength(1);
    expect(segments[0]?.type).toBe('lines');
    if (segments[0]?.type === 'lines') {
      expect(segments[0].lines).toHaveLength(10);
    }
  });

  it('collapses equal runs far from a change with context=3', () => {
    const left = Array.from({ length: 20 }, (_, i) => `L${i}`).join('\n');
    const rightLines = Array.from({ length: 20 }, (_, i) => `L${i}`);
    rightLines[10] = 'CHANGED';
    const right = rightLines.join('\n');
    const lines = unifiedLineDiff(left, right);
    const segments = collapseEqualContext(lines, { context: 3 });

    const collapsed = segments.filter((s) => s.type === 'collapse');
    expect(collapsed.length).toBeGreaterThan(0);
    const hiddenCount = collapsed.reduce((n, s) => n + s.lines.length, 0);
    expect(hiddenCount).toBeGreaterThan(0);

    const visibleLines = segments
      .filter((s) => s.type === 'lines')
      .flatMap((s) => (s.type === 'lines' ? s.lines : []));
    expect(visibleLines.some((l) => l.op !== 'equal')).toBe(true);
    // Context window around change: roughly 3 before + change(s) + 3 after
    expect(visibleLines.length).toBeLessThan(lines.length);
  });

  it('visibleEqualContextMask marks neighbors of removes/adds', () => {
    const lines: UnifiedDiffLine[] = [
      ...equals(5),
      { op: 'remove', text: 'old', leftLine: 6, rightLine: null },
      { op: 'add', text: 'new', leftLine: null, rightLine: 6 },
      ...equals(5).map((l, i) => ({
        ...l,
        text: `after${i}`,
        leftLine: 7 + i,
        rightLine: 7 + i,
      })),
    ];
    const mask = visibleEqualContextMask(lines, 2);
    const visibleIdx = mask.map((v, i) => (v ? i : -1)).filter((i) => i >= 0);
    expect(visibleIdx[0]).toBe(3); // 5-2
    expect(visibleIdx.at(-1)).toBe(8); // change at 5-6 + 2
  });
});

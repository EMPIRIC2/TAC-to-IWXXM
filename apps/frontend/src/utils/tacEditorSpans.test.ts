/**
 * T4.2 — Span normalize / decoration helpers for live workbench (UJ-017).
 */

import { describe, expect, it } from 'vitest';
import { buildSpanDecorations, normalizeTacSpans } from './tacEditorSpans';

describe('normalizeTacSpans', () => {
  it('clamps to document length and drops empty ranges', () => {
    const out = normalizeTacSpans(
      [
        { start: -2, end: 4, message: 'a' },
        { start: 10, end: 10, message: 'empty' },
        { start: 8, end: 100, message: 'clamp' },
      ],
      12,
    );
    expect(out).toEqual([
      { start: 0, end: 4, message: 'a' },
      { start: 8, end: 12, message: 'clamp' },
    ]);
  });

  it('sorts by start then end', () => {
    const out = normalizeTacSpans(
      [
        { start: 5, end: 8 },
        { start: 1, end: 3 },
        { start: 1, end: 2 },
      ],
      20,
    );
    expect(out.map((s) => [s.start, s.end])).toEqual([
      [1, 2],
      [1, 3],
      [5, 8],
    ]);
  });
});

describe('buildSpanDecorations', () => {
  it('creates a decoration set sized to the span count', () => {
    const set = buildSpanDecorations([
      { start: 0, end: 5, message: 'x' },
      { start: 6, end: 9, message: 'y' },
    ]);
    expect(set.size).toBe(2);
  });
});

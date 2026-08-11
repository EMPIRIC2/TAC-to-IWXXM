/**
 * BUG-2026-08-11 — Quality metrics display XML must be multi-line for human diffs.
 *
 * Compact C14N alone yields one mega-line; operators need pretty-printed peers.
 */

import { describe, it, expect } from 'vitest';
import { qualityMetricsDisplayXml } from './qualityMetricsDisplayXml';
import { splitLines, unifiedLineDiff } from './unifiedLineDiff';

const NESTED = '<root xmlns="urn:x"><a><b>1</b></a><c>2</c></root>';
const NESTED_DIFF = '<root xmlns="urn:x"><a><b>9</b></a><c>2</c></root>';

describe('qualityMetricsDisplayXml (BUG-2026-08-11)', () => {
  it('pretty-prints nested C14N so display is multi-line', () => {
    const display = qualityMetricsDisplayXml(NESTED);
    const lines = splitLines(display);
    expect(lines.length).toBeGreaterThan(3);
    expect(Math.max(...lines.map((line) => line.length))).toBeLessThan(120);
  });

  it('feeds multi-line peers into unifiedLineDiff (not one mega-line)', () => {
    const left = qualityMetricsDisplayXml(NESTED);
    const right = qualityMetricsDisplayXml(NESTED_DIFF);
    const diff = unifiedLineDiff(left, right);
    expect(diff.length).toBeGreaterThan(2);
    expect(Math.max(...diff.map((line) => line.text.length))).toBeLessThan(120);
    expect(
      diff.some((line) => line.op === 'remove' && line.text.includes('<b>1</b>')),
    ).toBe(true);
    expect(
      diff.some((line) => line.op === 'add' && line.text.includes('<b>9</b>')),
    ).toBe(true);
  });
});

/**
 * Unit tests for client-side unified line diff (TC-EV054-003 helper).
 */

import { describe, expect, it } from 'vitest';
import { isUnifiedDiffEmpty, splitLines, unifiedLineDiff } from './unifiedLineDiff';

describe('unifiedLineDiff', () => {
  it('returns empty for two empty strings', () => {
    expect(unifiedLineDiff('', '')).toEqual([]);
    expect(isUnifiedDiffEmpty([])).toBe(true);
  });

  it('marks equal lines when texts match', () => {
    const lines = unifiedLineDiff('a\nb\n', 'a\nb\n');
    expect(lines.every((l) => l.op === 'equal')).toBe(true);
    expect(isUnifiedDiffEmpty(lines)).toBe(true);
  });

  it('emits remove/add for unequal XML snippets', () => {
    const left = '<root>\n  <a/>\n</root>';
    const right = '<root>\n  <b/>\n</root>';
    const lines = unifiedLineDiff(left, right);
    expect(lines.some((l) => l.op === 'remove' && l.text.includes('<a/>'))).toBe(true);
    expect(lines.some((l) => l.op === 'add' && l.text.includes('<b/>'))).toBe(true);
    expect(isUnifiedDiffEmpty(lines)).toBe(false);
  });

  it('emits trailing removes when left is longer', () => {
    const lines = unifiedLineDiff('a\nb\nc', 'a');
    expect(lines.filter((l) => l.op === 'remove').map((l) => l.text)).toEqual([
      'b',
      'c',
    ]);
  });

  it('emits trailing adds when right is longer', () => {
    const lines = unifiedLineDiff('a', 'a\nb\nc');
    expect(lines.filter((l) => l.op === 'add').map((l) => l.text)).toEqual(['b', 'c']);
  });

  it('splitLines returns an empty array for empty input', () => {
    expect(splitLines('')).toEqual([]);
  });

  it('splitLines normalizes CRLF', () => {
    expect(splitLines('a\r\nb\r\n')).toEqual(['a', 'b', '']);
  });

  it('splitLines normalizes bare CR', () => {
    expect(splitLines('a\rb')).toEqual(['a', 'b']);
  });

  it('prefers remove when LCS backtrack favors dropping left line', () => {
    const lines = unifiedLineDiff('x\ny', 'x');
    expect(lines.some((l) => l.op === 'remove' && l.text === 'y')).toBe(true);
  });

  it('prefers add when LCS backtrack favors inserting right line', () => {
    const lines = unifiedLineDiff('x', 'x\nz');
    expect(lines.some((l) => l.op === 'add' && l.text === 'z')).toBe(true);
  });

  it('handles interleaved edits in the middle of equal runs', () => {
    const left = 'keep\nold\nkeep';
    const right = 'keep\nnew\nkeep';
    const lines = unifiedLineDiff(left, right);
    expect(lines.filter((l) => l.op === 'equal').map((l) => l.text)).toEqual([
      'keep',
      'keep',
    ]);
    expect(lines.some((l) => l.op === 'remove' && l.text === 'old')).toBe(true);
    expect(lines.some((l) => l.op === 'add' && l.text === 'new')).toBe(true);
  });
});

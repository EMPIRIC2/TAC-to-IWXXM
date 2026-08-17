/**
 * Unit tests for Quality metrics diff layout helpers (TC-EV058).
 */

import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { unifiedLineDiff } from './unifiedLineDiff';
import {
  QUALITY_METRICS_DIFF_LAYOUT_STORAGE_KEY,
  parseDiffLayout,
  readDiffLayoutPreference,
  sideBySideFromUnified,
  writeDiffLayoutPreference,
} from './qualityMetricsDiffLayout';

describe('qualityMetricsDiffLayout (TC-EV058)', () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  afterEach(() => {
    window.localStorage.clear();
  });

  it('parseDiffLayout defaults unknown to unified', () => {
    expect(parseDiffLayout(null)).toBe('unified');
    expect(parseDiffLayout('')).toBe('unified');
    expect(parseDiffLayout('side-by-side')).toBe('side-by-side');
    expect(parseDiffLayout('inline')).toBe('unified');
  });

  it('persists preference in localStorage', () => {
    expect(readDiffLayoutPreference()).toBe('unified');
    writeDiffLayoutPreference('side-by-side');
    expect(window.localStorage.getItem(QUALITY_METRICS_DIFF_LAYOUT_STORAGE_KEY)).toBe(
      'side-by-side',
    );
    expect(readDiffLayoutPreference()).toBe('side-by-side');
    writeDiffLayoutPreference('unified');
    expect(readDiffLayoutPreference()).toBe('unified');
  });

  it('sideBySideFromUnified pairs remove+add and keeps equals', () => {
    const lines = unifiedLineDiff('a\nb\nc', 'a\nx\nc');
    const rows = sideBySideFromUnified(lines);
    expect(rows).toEqual([
      { left: 'a', right: 'a', leftOp: 'equal', rightOp: 'equal' },
      { left: 'b', right: 'x', leftOp: 'remove', rightOp: 'add' },
      { left: 'c', right: 'c', leftOp: 'equal', rightOp: 'equal' },
    ]);
  });

  it('sideBySideFromUnified handles unpaired add/remove', () => {
    const onlyRemove = sideBySideFromUnified(unifiedLineDiff('a\nb', 'a'));
    expect(onlyRemove.some((r) => r.leftOp === 'remove' && r.right === null)).toBe(
      true,
    );
    const onlyAdd = sideBySideFromUnified(unifiedLineDiff('a', 'a\nb'));
    expect(onlyAdd.some((r) => r.rightOp === 'add' && r.left === null)).toBe(true);
  });
});

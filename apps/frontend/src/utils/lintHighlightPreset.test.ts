/**
 * Lint highlight presets (TC-UX-DECLUTTER-008).
 *
 * [Corpus: tests §TC-UX-DECLUTTER]
 */

import { describe, expect, it } from 'vitest';

import {
  lintHighlightTokens,
  readLintHighlightPreset,
  writeLintHighlightPreset,
} from './lintHighlightPreset';

describe('lintHighlightPreset', () => {
  it('TC-UX-DECLUTTER-008: default and colorblind tokens differ', () => {
    const def = lintHighlightTokens('default');
    const cb = lintHighlightTokens('colorblind');
    expect(def.infoBorder).not.toBe(cb.infoBorder);
    expect(def.infoBorder.toLowerCase()).not.toContain('0284c7');
  });

  it('round-trips localStorage preset', () => {
    writeLintHighlightPreset('colorblind');
    expect(readLintHighlightPreset()).toBe('colorblind');
    writeLintHighlightPreset('default');
    expect(readLintHighlightPreset()).toBe('default');
  });
});

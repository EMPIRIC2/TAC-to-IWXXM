/**
 * Lint highlight presets (TC-UX-DECLUTTER-008).
 *
 * [Corpus: tests §TC-UX-DECLUTTER]
 */

import { describe, expect, it, vi } from 'vitest';

import {
  isBrowserEnv,
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

  it('falls back to default on invalid or throwing storage', () => {
    window.localStorage.setItem('tac-to-iwxxm.lint-highlight.preset', 'nope');
    expect(readLintHighlightPreset()).toBe('default');
    const getItem = vi.spyOn(Storage.prototype, 'getItem').mockImplementation(() => {
      throw new Error('blocked');
    });
    expect(readLintHighlightPreset()).toBe('default');
    getItem.mockRestore();
    const setItem = vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => {
      throw new Error('blocked');
    });
    expect(() => writeLintHighlightPreset('colorblind')).not.toThrow();
    setItem.mockRestore();
  });

  it('isBrowserEnv distinguishes SSR from browser globals', () => {
    expect(isBrowserEnv({})).toBe(false);
    expect(isBrowserEnv({ window: {} })).toBe(true);
  });

  it('SSR overrides skip localStorage', () => {
    expect(readLintHighlightPreset(false)).toBe('default');
    expect(() => writeLintHighlightPreset('default', false)).not.toThrow();
  });
});

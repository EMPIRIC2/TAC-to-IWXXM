/**
 * TC-UX-DECLUTTER helpers for Convert results drawer.
 *
 * [Corpus: tests §TC-UX-DECLUTTER]
 */

import { describe, expect, it } from 'vitest';

import {
  CONVERT_RESULTS_TABS,
  defaultTabAfterConvert,
  shouldAutoOpenResultsDrawer,
} from './convertResultsDrawer';

describe('convertResultsDrawer', () => {
  it('TC-UX-DECLUTTER-002: exposes five ordered tabs', () => {
    expect(CONVERT_RESULTS_TABS.map((t) => t.id)).toEqual([
      'iwxxm',
      'console',
      'decoder',
      'map',
      'downloads',
    ]);
  });

  it('TC-UX-DECLUTTER-003: auto-opens on IWXXM after first convert', () => {
    expect(defaultTabAfterConvert()).toBe('iwxxm');
    expect(shouldAutoOpenResultsDrawer(true, true)).toBe(true);
    expect(shouldAutoOpenResultsDrawer(true, false)).toBe(false);
    expect(shouldAutoOpenResultsDrawer(false, true)).toBe(false);
  });
});

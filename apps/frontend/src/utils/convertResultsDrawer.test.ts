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
  it('TC-UX-DECLUTTER-002: exposes four ordered tabs without Map', () => {
    expect(CONVERT_RESULTS_TABS.map((t) => t.id)).toEqual([
      'iwxxm',
      'console',
      'decoder',
      'downloads',
    ]);
    expect(CONVERT_RESULTS_TABS.map((t) => t.id)).not.toContain('map');
    expect(CONVERT_RESULTS_TABS.every((t) => t.label !== 'Map')).toBe(true);
  });

  it('TC-UX-DECLUTTER-003: auto-opens on IWXXM after first convert', () => {
    expect(defaultTabAfterConvert()).toBe('iwxxm');
    expect(shouldAutoOpenResultsDrawer(true, true)).toBe(true);
    expect(shouldAutoOpenResultsDrawer(true, false)).toBe(false);
    expect(shouldAutoOpenResultsDrawer(false, true)).toBe(false);
  });
});

/**
 * Unit tests for Quality metrics operator copy helpers.
 */

import { describe, expect, it } from 'vitest';
import {
  formatMatchStatusLabel,
  QUALITY_METRICS_DEFERRED_LABEL,
} from './qualityMetricsCopy';

describe('formatMatchStatusLabel', () => {
  it('maps known API statuses to plain language', () => {
    expect(formatMatchStatusLabel('equal')).toBe('Matches official');
    expect(formatMatchStatusLabel('unequal')).toBe('Differs from official');
    expect(formatMatchStatusLabel('deferred')).toBe(QUALITY_METRICS_DEFERRED_LABEL);
  });

  it('passes through unknown statuses unchanged', () => {
    expect(formatMatchStatusLabel('unknown-status')).toBe('unknown-status');
  });
});

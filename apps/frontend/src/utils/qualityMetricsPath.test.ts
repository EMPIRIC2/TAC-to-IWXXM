/**
 * Unit tests for Quality metrics path helpers (TC-EV056-001).
 */

import { describe, expect, it } from 'vitest';
import {
  parseQualityMetricsPath,
  QUALITY_METRICS_LIST_PATH,
  qualityMetricsDetailPath,
} from './qualityMetricsPath';

describe('qualityMetricsPath', () => {
  it('builds and parses a detail stem path', () => {
    const path = qualityMetricsDetailPath('metar-A3-1');
    expect(path).toBe('/quality/metar-A3-1');
    expect(parseQualityMetricsPath(path)).toEqual({
      kind: 'detail',
      stem: 'metar-A3-1',
    });
  });

  it('parses list path with optional trailing slash', () => {
    expect(parseQualityMetricsPath(QUALITY_METRICS_LIST_PATH)).toEqual({
      kind: 'list',
    });
    expect(parseQualityMetricsPath('/quality/')).toEqual({ kind: 'list' });
  });

  it('returns null for unrelated paths', () => {
    expect(parseQualityMetricsPath('/')).toBeNull();
    expect(parseQualityMetricsPath('/convert')).toBeNull();
  });

  it('encodes special characters in stems', () => {
    const path = qualityMetricsDetailPath('sigmet/foo');
    // Slash in stem is encoded so path stays single segment.
    expect(path).toBe('/quality/sigmet%2Ffoo');
    expect(parseQualityMetricsPath(path)).toEqual({
      kind: 'detail',
      stem: 'sigmet/foo',
    });
  });
});

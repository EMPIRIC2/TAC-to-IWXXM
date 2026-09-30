/**
 * Unit tests for Quality metrics operator copy helpers.
 */

import { describe, expect, it } from 'vitest';
import {
  formatMatchStatusLabel,
  isOperatorValidateNoise,
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

describe('isOperatorValidateNoise', () => {
  it('hides XPath engine errors and schema-import warnings', () => {
    expect(
      isOperatorValidateNoise({
        code: 'SCHEMATRON_XPATH_UNSUPPORTED',
        message: 'skip',
      }),
    ).toBe(true);
    expect(
      isOperatorValidateNoise({ code: ' SCHEMA_IMPORT_WARNING ', message: 'import' }),
    ).toBe(true);
    expect(isOperatorValidateNoise({ code: 'OTHER', message: 'XPath error: id' })).toBe(
      true,
    );
  });

  it('keeps product validation findings', () => {
    expect(
      isOperatorValidateNoise({ code: 'SCHEMA', message: 'element missing' }),
    ).toBe(false);
    expect(isOperatorValidateNoise({ code: 1, message: 2 })).toBe(false);
  });
});

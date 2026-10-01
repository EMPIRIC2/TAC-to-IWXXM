import { describe, expect, it } from 'vitest';
import { ruleExamplePair, ruleExamplePairFrom } from './ruleCatalogExamples';

describe('ruleCatalogExamples', () => {
  it('returns packaged reports and treats a missing or blank side as unavailable', () => {
    const both = ruleExamplePair('MISSING_CCCC');
    expect(both.pass).toContain('KJFK');
    expect(both.fail).not.toContain('KJFK');

    const failOnly = ruleExamplePair('MISSING_DTG');
    expect(failOnly.pass).toBeNull();
    expect(failOnly.fail).toContain('VA ADVISORY');

    expect(ruleExamplePair('NOT_A_RULE')).toEqual({ pass: null, fail: null });
    expect(
      ruleExamplePairFrom('BLANK', {
        BLANK: { pass: '   ', fail: '' },
      }),
    ).toEqual({ pass: null, fail: null });
    expect(ruleExamplePairFrom('ABSENT', {})).toEqual({ pass: null, fail: null });
  });
});

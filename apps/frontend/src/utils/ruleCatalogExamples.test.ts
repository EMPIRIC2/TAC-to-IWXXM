import { describe, expect, it } from 'vitest';
import {
  isInfoCatalogLevel,
  plainInfoExample,
  ruleExamplePair,
  ruleExamplePairFrom,
} from './ruleCatalogExamples';

describe('ruleCatalogExamples', () => {
  it('returns packaged reports and treats a missing or blank side as unavailable', () => {
    const both = ruleExamplePair('MISSING_CCCC');
    expect(both.pass).toContain('KJFK');
    expect(both.fail).not.toContain('KJFK');

    const advisory = ruleExamplePair('MISSING_DTG');
    expect(advisory.pass).toContain('VA ADVISORY');
    expect(advisory.pass).toMatch(/^DTG:/m);
    expect(advisory.fail).toContain('VA ADVISORY');
    expect(advisory.fail).not.toMatch(/^DTG:/m);

    expect(ruleExamplePair('NOT_A_RULE')).toEqual({ pass: null, fail: null });
    expect(
      ruleExamplePairFrom('BLANK', {
        BLANK: { pass: '   ', fail: '' },
      }),
    ).toEqual({ pass: null, fail: null });
    expect(ruleExamplePairFrom('ABSENT', {})).toEqual({ pass: null, fail: null });
  });

  it('shows info samples without a pass or fail label and keeps a lone report', () => {
    expect(isInfoCatalogLevel('info')).toBe(true);
    expect(isInfoCatalogLevel(' INFO ')).toBe(true);
    expect(isInfoCatalogLevel('warning')).toBe(false);
    expect(isInfoCatalogLevel('error')).toBe(false);
    expect(isInfoCatalogLevel('warn')).toBe(false);
    expect(isInfoCatalogLevel('')).toBe(false);
    expect(isInfoCatalogLevel(null)).toBe(false);
    expect(isInfoCatalogLevel(undefined)).toBe(false);

    expect(plainInfoExample({ pass: 'TAF OK=', fail: 'TAF BAD=' })).toBe('TAF OK=');
    expect(plainInfoExample({ pass: null, fail: 'TAF BAD=' })).toBe('TAF BAD=');
    expect(plainInfoExample({ pass: 'TAF OK=', fail: null })).toBe('TAF OK=');
    expect(plainInfoExample({ pass: null, fail: null })).toBeNull();
  });
});

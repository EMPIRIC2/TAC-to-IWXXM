/**
 * optionalFormField unit tests.
 */

import { describe, expect, it } from 'vitest';

import { optionalFormField } from './optionalFormField';

describe('optionalFormField', () => {
  it('returns trimmed non-empty values', () => {
    expect(optionalFormField('  LIB.X  ')).toBe('LIB.X');
  });

  it('returns undefined for blank or missing values', () => {
    expect(optionalFormField('')).toBeUndefined();
    expect(optionalFormField('   ')).toBeUndefined();
    expect(optionalFormField(undefined)).toBeUndefined();
  });
});

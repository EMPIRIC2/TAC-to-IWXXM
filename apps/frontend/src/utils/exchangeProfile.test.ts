/**
 * Unit tests for exchange profile coerce helpers (EV-090 / #1024).
 */
import { describe, expect, it } from 'vitest';
import {
  coerceExchangeProfile,
  DEFAULT_EXCHANGE_PROFILE,
  EXCHANGE_PROFILE_OPTIONS,
} from './exchangeProfile';

describe('coerceExchangeProfile', () => {
  it('accepts registered wire ids', () => {
    for (const opt of EXCHANGE_PROFILE_OPTIONS) {
      expect(coerceExchangeProfile(opt.value)).toBe(opt.value);
    }
  });

  it('defaults unknown values to GLOBAL_AFS', () => {
    expect(coerceExchangeProfile('NOPE')).toBe(DEFAULT_EXCHANGE_PROFILE);
    expect(coerceExchangeProfile(null)).toBe('GLOBAL_AFS');
    expect(coerceExchangeProfile('annex3')).toBe('GLOBAL_AFS');
  });
});

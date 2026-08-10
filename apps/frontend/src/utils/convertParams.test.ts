/**
 * Unit tests for convert parameter mapping (ADR-023 / ADR-024).
 */
import { describe, expect, it } from 'vitest';
import {
  consoleLevelPasses,
  issueLevelPasses,
  issueSeverityRank,
  mapOnErrorToStopOnError,
  mapStrictToValidation,
} from './convertParams';

describe('convertParams', () => {
  it('maps strict validation to comprehensive validate_output on hard convert', () => {
    expect(mapStrictToValidation(true, false)).toEqual({
      validateOutput: true,
      validationLevel: 'comprehensive',
    });
    expect(mapStrictToValidation(false, false)).toEqual({
      validateOutput: false,
      validationLevel: 'basic',
    });
  });

  it('disables post-convert validation during soft-preview', () => {
    expect(mapStrictToValidation(true, true)).toEqual({
      validateOutput: false,
      validationLevel: 'basic',
    });
  });

  it('maps onError fail to stop_on_error', () => {
    expect(mapOnErrorToStopOnError('fail')).toBe(true);
    expect(mapOnErrorToStopOnError('skip')).toBe(false);
    expect(mapOnErrorToStopOnError('warn')).toBe(false);
  });

  it('filters console lines by operator log level', () => {
    expect(consoleLevelPasses('info', 'DEBUG')).toBe(true);
    expect(consoleLevelPasses('info', 'WARNING')).toBe(false);
    expect(consoleLevelPasses('warn', 'WARNING')).toBe(true);
    expect(consoleLevelPasses('error', 'ERROR')).toBe(true);
    expect(consoleLevelPasses('warn', 'CRITICAL')).toBe(false);
  });

  it('filters conversion/validation issue severities by log level', () => {
    expect(issueLevelPasses('info', 'INFO')).toBe(true);
    expect(issueLevelPasses('warning', 'ERROR')).toBe(false);
    expect(issueLevelPasses('error', 'WARNING')).toBe(true);
  });

  it('ranks debug, information aliases, and unknown issue severity', () => {
    expect(issueSeverityRank('debug')).toBe(0);
    expect(issueSeverityRank('information')).toBe(1);
    expect(issueSeverityRank('unexpected')).toBe(3);
    expect(issueSeverityRank(undefined)).toBe(3);
  });
});

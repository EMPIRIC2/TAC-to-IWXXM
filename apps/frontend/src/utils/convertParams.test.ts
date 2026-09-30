/**
 * Unit tests for convert parameter mapping (ADR-023 / ADR-024).
 */
import { describe, expect, it } from 'vitest';
import {
  convertFieldsFromParamsBar,
  optionalTrim,
  consoleLevelPasses,
  isValidBulletinId,
  isValidIssuingCenter,
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

  it('accepts empty or TTAAii Bulletin ID and 4-letter issuing center', () => {
    expect(isValidBulletinId('')).toBe(true);
    expect(isValidBulletinId('saaa00')).toBe(true);
    expect(isValidBulletinId('SAAA0X')).toBe(false);
    expect(isValidIssuingCenter('')).toBe(true);
    expect(isValidIssuingCenter('kwbc')).toBe(true);
    expect(isValidIssuingCenter('KW1C')).toBe(false);
  });

  it('maps the params bar onto convert fields and omits blank identifiers', () => {
    const bar = {
      bulletinId: '  SAAA00 ',
      issuingCenter: '',
      reportVariant: ' SPECI ',
      profile: 'icao',
      exchangeProfile: 'default',
      presetId: '',
      conversionLibraryId: ' LIB.CONVERSION.ICAO_2025 ',
      tacValidationLibraryId: '',
      iwxxmValidationLibraryId: '',
      disseminationLibraryId: '',
      decodingLibraryId: '',
      iwxxmVersion: '2025-2',
      strictValidation: true,
      includeNilReasons: true,
      onError: 'fail' as const,
      logLevel: 'WARNING' as const,
    };
    expect(
      convertFieldsFromParamsBar(bar, {
        softPreview: false,
        propagateResidualsToRemarks: true,
      }),
    ).toMatchObject({
      bulletinId: 'SAAA00',
      issuingCenter: undefined,
      reportVariant: 'SPECI',
      conversionLibraryId: 'LIB.CONVERSION.ICAO_2025',
      presetId: undefined,
      validateOutput: true,
      validationLevel: 'comprehensive',
      stopOnError: true,
      includeNilReasons: true,
      logLevel: 'WARNING',
      preview: false,
      propagateResidualsToRemarks: true,
    });
    expect(
      convertFieldsFromParamsBar(bar, {
        softPreview: true,
        propagateResidualsToRemarks: false,
      }).validateOutput,
    ).toBe(false);
    expect(optionalTrim(undefined)).toBeUndefined();
    expect(optionalTrim('   ')).toBeUndefined();
  });
});

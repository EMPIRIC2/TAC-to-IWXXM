/**
 * TC-EVPYL-REGEX / CROSS — client YAML + regex diagnostics.
 */

import { describe, expect, it } from 'vitest';

import {
  diagnoseJsRegex,
  diagnosticsFromYaml,
  isLibrarySelectableOnConvert,
  yamlLooksInvalid,
} from './libraryYamlDiagnostics';

describe('libraryYamlDiagnostics', () => {
  it('TC-EVPYL-REGEX-001 compiles named captures', () => {
    const diag = diagnoseJsRegex('(?P<wind>\\d{5})KT', '18004KT');
    expect(diag.severity).toBe('ok');
    expect(diag.captures[0]?.name).toBe('wind');
    expect(diag.sampleMatched).toBe(true);
  });

  it('TC-EVPYL-REGEX-002 fails when the pattern does not compile', () => {
    const diag = diagnoseJsRegex('(unclosed');
    expect(diag.severity).toBe('fail');
    expect(diag.message.toLowerCase()).toContain('compile');
  });

  it('TC-EVPYL-REGEX-003 fails when the sample has no match', () => {
    const diag = diagnoseJsRegex('^TAF ', 'METAR KJFK');
    expect(diag.severity).toBe('fail');
    expect(diag.sampleMatched).toBe(false);
  });

  it('warns on nested quantifiers', () => {
    expect(diagnoseJsRegex('(a+)+b').severity).toBe('warn');
  });

  it('TC-EVPYL-CROSS-001 treats invalid YAML as locked', () => {
    expect(yamlLooksInvalid('')).toBe(true);
    expect(yamlLooksInvalid('kind: conversion\nname: "unclosed')).toBe(true);
    expect(yamlLooksInvalid('name: only')).toBe(true);
    expect(yamlLooksInvalid('kind: conversion\nname: Wind')).toBe(false);
  });

  it('extracts quoted patterns from YAML', () => {
    const yaml = `kind: tac_validation
name: Wind
rules:
  - pattern: "(?P<wind>\\d{5})KT"
`;
    const diags = diagnosticsFromYaml(yaml, '18004KT');
    expect(diags[0]?.severity).toBe('ok');
    expect(diagnosticsFromYaml('kind: nope')).toEqual([]);
  });

  it('TC-EVPYL-ACTIVATE Convert selectability', () => {
    expect(
      isLibrarySelectableOnConvert({ access: 'first_party', status: 'draft' }),
    ).toBe(true);
    expect(isLibrarySelectableOnConvert({ access: 'custom', status: 'draft' })).toBe(
      false,
    );
    expect(
      isLibrarySelectableOnConvert({ access: 'custom', status: 'activated' }),
    ).toBe(true);
  });
});

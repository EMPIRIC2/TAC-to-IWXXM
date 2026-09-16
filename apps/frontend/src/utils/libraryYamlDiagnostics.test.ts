/**
 * TC-EVPYL-REGEX / CROSS — client YAML + regex diagnostics.
 */

import { afterEach, describe, expect, it, vi } from 'vitest';

import {
  diagnoseJsRegex,
  diagnosticsFromYaml,
  isLibrarySelectableOnConvert,
  yamlLooksInvalid,
} from './libraryYamlDiagnostics';

describe('libraryYamlDiagnostics', () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

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

  it('uses non-Error compile fallback message', () => {
    const OriginalRegExp = globalThis.RegExp;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (globalThis as any).RegExp = function failingRegExp() {
      throw 'boom' as never;
    };
    try {
      const diag = diagnoseJsRegex('abc');
      expect(diag.severity).toBe('fail');
      expect(diag.message).toBe('Does not compile: Does not compile');
    } finally {
      globalThis.RegExp = OriginalRegExp;
    }
  });

  it('falls back when named-group capture text is missing', () => {
    vi.spyOn(String.prototype, 'matchAll').mockImplementation(function* (this: string) {
      const match = ['(?<wind>', undefined] as unknown as RegExpExecArray;
      match.index = 0;
      match.input = this;
      yield match;
    } as unknown as (regexp: RegExp) => RegExpStringIterator<RegExpExecArray>);
    const diag = diagnoseJsRegex('(?P<wind>\\d{5})KT');
    expect(diag.severity).toBe('ok');
    expect(diag.captures[0]?.name).toBe('group1');
  });

  it('TC-EVPYL-REGEX-003 fails when the sample has no match', () => {
    const diag = diagnoseJsRegex('^TAF ', 'METAR KJFK');
    expect(diag.severity).toBe('fail');
    expect(diag.sampleMatched).toBe(false);
  });

  it('warns on nested quantifiers', () => {
    expect(diagnoseJsRegex('(a+)+b').severity).toBe('warn');
  });

  it('warns when only unnamed captures are present', () => {
    expect(diagnoseJsRegex('(abc)').severity).toBe('warn');
  });

  it('TC-EVPYL-CROSS-001 treats invalid YAML as locked', () => {
    expect(yamlLooksInvalid('')).toBe(true);
    expect(yamlLooksInvalid('kind: conversion\nname: "unclosed')).toBe(true);
    expect(yamlLooksInvalid('name: only')).toBe(true);
    expect(yamlLooksInvalid('kind: conversion\nname: Wind')).toBe(false);
  });

  it('extracts quoted patterns from YAML including empty patterns', () => {
    const yaml = `kind: tac_validation
name: Wind
rules:
  - pattern: "(?P<wind>\\d{5})KT"
  - pattern: ""
`;
    const diags = diagnosticsFromYaml(yaml, '18004KT');
    expect(diags[0]?.severity).toBe('ok');
    expect(diags.some((d) => d.pattern === '')).toBe(true);
    expect(diagnosticsFromYaml('kind: nope')).toEqual([]);
    expect(diagnosticsFromYaml('kind: conversion\nname: Wind')).toEqual([]);
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

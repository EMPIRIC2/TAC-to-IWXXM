import { describe, it, expect } from 'vitest';
import { prettyPrintXml } from './prettyXml';

describe('prettyPrintXml', () => {
  it('indents nested elements', () => {
    const out = prettyPrintXml('<a><b/></a>');
    expect(out).toContain('<a>');
    expect(out).toContain('\n');
    expect(out).toMatch(/ {2}<b\/>/);
  });

  it('returns non-XML unchanged', () => {
    expect(prettyPrintXml('not xml')).toBe('not xml');
  });
});

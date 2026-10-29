/**
 * Source attribution segment splitting for Issue details.
 */
import { describe, expect, it } from 'vitest';
import { splitSourceSegments } from './issueDetailSource';

describe('splitSourceSegments', () => {
  it('keeps plain text without a URL as one text segment', () => {
    expect(splitSourceSegments('WMO code list')).toEqual([
      { kind: 'text', text: 'WMO code list' },
    ]);
  });

  it('returns a single empty text segment for an empty string', () => {
    expect(splitSourceSegments('')).toEqual([{ kind: 'text', text: '' }]);
  });

  it('splits a label and URL, leaving the label as plain text', () => {
    const url = 'https://www.icao.int/doc.pdf';
    expect(splitSourceSegments(`icao-eur-doc-014 - ${url}`)).toEqual([
      { kind: 'text', text: 'icao-eur-doc-014 - ' },
      { kind: 'url', href: url },
    ]);
  });

  it('accepts http as well as https', () => {
    expect(splitSourceSegments('see http://example.com/a')).toEqual([
      { kind: 'text', text: 'see ' },
      { kind: 'url', href: 'http://example.com/a' },
    ]);
    // Kill https?-only and character-class mutants: scheme + path stay linked.
    const httpOnly = splitSourceSegments('http://x.example/path?q=1');
    expect(httpOnly).toEqual([{ kind: 'url', href: 'http://x.example/path?q=1' }]);
    expect(httpOnly[0]).toMatchObject({ kind: 'url' });
  });

  it('does not treat whitespace inside a would-be URL as part of the href', () => {
    expect(splitSourceSegments('go https://ex.example/a b')).toEqual([
      { kind: 'text', text: 'go ' },
      { kind: 'url', href: 'https://ex.example/a' },
      { kind: 'text', text: ' b' },
    ]);
  });

  it('peels a trailing closing paren from parenthetical URLs', () => {
    expect(splitSourceSegments('wmo (https://example.com)')).toEqual([
      { kind: 'text', text: 'wmo (' },
      { kind: 'url', href: 'https://example.com' },
      { kind: 'text', text: ')' },
    ]);
  });

  it('peels trailing comma, period, semicolon, and colon', () => {
    // URL regex consumes trailing punct; peelUrl splits it into its own text segment.
    expect(splitSourceSegments('a https://ex.com/x, b')).toEqual([
      { kind: 'text', text: 'a ' },
      { kind: 'url', href: 'https://ex.com/x' },
      { kind: 'text', text: ',' },
      { kind: 'text', text: ' b' },
    ]);
    expect(splitSourceSegments('end https://ex.com.')).toEqual([
      { kind: 'text', text: 'end ' },
      { kind: 'url', href: 'https://ex.com' },
      { kind: 'text', text: '.' },
    ]);
    expect(splitSourceSegments('x https://ex.com; y')).toEqual([
      { kind: 'text', text: 'x ' },
      { kind: 'url', href: 'https://ex.com' },
      { kind: 'text', text: ';' },
      { kind: 'text', text: ' y' },
    ]);
    expect(splitSourceSegments('x https://ex.com: y')).toEqual([
      { kind: 'text', text: 'x ' },
      { kind: 'url', href: 'https://ex.com' },
      { kind: 'text', text: ':' },
      { kind: 'text', text: ' y' },
    ]);
  });

  it('peels only trailing punctuation on the URL match, not mid-string dots', () => {
    // Kill `$` removal and `+`→single mutants: ".." at end peels as a unit;
    // a path segment with an internal dot stays inside the href.
    expect(splitSourceSegments('see https://ex.example/a.b..')).toEqual([
      { kind: 'text', text: 'see ' },
      { kind: 'url', href: 'https://ex.example/a.b' },
      { kind: 'text', text: '..' },
    ]);
    const negated = splitSourceSegments('pad https://ex.example/ok)');
    expect(negated).toEqual([
      { kind: 'text', text: 'pad ' },
      { kind: 'url', href: 'https://ex.example/ok' },
      { kind: 'text', text: ')' },
    ]);
  });

  it('splits multiple URLs and keeps interstitial text', () => {
    expect(
      splitSourceSegments('A https://a.example/1 and https://b.example/2 end'),
    ).toEqual([
      { kind: 'text', text: 'A ' },
      { kind: 'url', href: 'https://a.example/1' },
      { kind: 'text', text: ' and ' },
      { kind: 'url', href: 'https://b.example/2' },
      { kind: 'text', text: ' end' },
    ]);
  });

  it('treats a URL-only string as a single url segment', () => {
    expect(splitSourceSegments('https://only.example/path')).toEqual([
      { kind: 'url', href: 'https://only.example/path' },
    ]);
  });

  it('leaves scheme-only and host-without-scheme as plain text', () => {
    expect(splitSourceSegments('go https:// next')).toEqual([
      { kind: 'text', text: 'go https:// next' },
    ]);
    expect(splitSourceSegments('see example.com/a')).toEqual([
      { kind: 'text', text: 'see example.com/a' },
    ]);
  });

  it('peels multiple trailing punctuation marks in one peel', () => {
    expect(splitSourceSegments('see https://ex.com/x).')).toEqual([
      { kind: 'text', text: 'see ' },
      { kind: 'url', href: 'https://ex.com/x' },
      { kind: 'text', text: ').' },
    ]);
  });
});

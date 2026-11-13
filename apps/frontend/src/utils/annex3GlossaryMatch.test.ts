import { describe, expect, it } from 'vitest';
import {
  isLimitedMeaningHoverExcluded,
  segmentGlossaryText,
} from './annex3GlossaryMatch';

describe('annex3GlossaryMatch', () => {
  it('matches longest phrase before shorter tokens (TC-F38-003)', () => {
    const segments = segmentGlossaryText(
      'Prevailing visibility and runway visual range at the aerodrome',
    );
    const terms = segments
      .filter((s) => s.kind === 'term')
      .map((s) => (s.kind === 'term' ? s.entry.id : ''));
    expect(terms).toContain('prevailing-visibility');
    expect(terms).toContain('rvr');
    expect(terms).toContain('aerodrome');
  });

  it('is case-insensitive and keeps surrounding text', () => {
    const segments = segmentGlossaryText('Check SIGMET then done.');
    expect(segments[0]).toEqual({ kind: 'text', value: 'Check ' });
    expect(segments[1]).toMatchObject({
      kind: 'term',
      value: 'SIGMET',
      entry: expect.objectContaining({ id: 'sigmet' }),
    });
    expect(segments[2]).toEqual({ kind: 'text', value: ' then done.' });
  });

  it('does not match limited-meaning verbs for hover (TC-F38-006)', () => {
    expect(isLimitedMeaningHoverExcluded('provide')).toBe(true);
    expect(isLimitedMeaningHoverExcluded('issue')).toBe(true);
    expect(isLimitedMeaningHoverExcluded('supply')).toBe(true);
    const segments = segmentGlossaryText('Please provide and issue or supply data');
    expect(segments.every((s) => s.kind === 'text')).toBe(true);
  });

  it('does not match mid-token substrings', () => {
    const segments = segmentGlossaryText('unSIGmeta and foreshadow');
    expect(segments.every((s) => s.kind === 'text')).toBe(true);
  });

  it('matches aliases such as RVR (TC-F38-003)', () => {
    const segments = segmentGlossaryText('Reported RVR is low');
    const term = segments.find((s) => s.kind === 'term');
    expect(term).toMatchObject({
      kind: 'term',
      value: 'RVR',
      entry: expect.objectContaining({ id: 'rvr' }),
    });
  });

  it('returns empty segments for empty input (data validation)', () => {
    expect(segmentGlossaryText('')).toEqual([]);
  });

  it('returns plain text when catalog override is empty (service validation)', () => {
    expect(segmentGlossaryText('SIGMET ahead', [])).toEqual([
      { kind: 'text', value: 'SIGMET ahead' },
    ]);
  });
});

describe('segmentGlossaryText trailing coverage', () => {
  it('keeps trailing text after a match', () => {
    const segments = segmentGlossaryText('SIGMET then more words');
    expect(segments.at(-1)).toEqual({ kind: 'text', value: ' then more words' });
  });

  it('returns a single text segment when catalog override is empty', () => {
    expect(segmentGlossaryText('SIGMET', [])).toEqual([
      { kind: 'text', value: 'SIGMET' },
    ]);
  });
});

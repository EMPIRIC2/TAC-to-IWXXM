/**
 * STE hygiene — match behavior stays stable when paraphrase copy changes.
 *
 * Coordinates with mid-flight glossary language edits: assert ids/aliases only.
 */

import { describe, expect, it } from 'vitest';
import { ANNEX3_GLOSSARY_ENTRIES } from '@/data/annex3Glossary';
import { segmentGlossaryText } from './annex3GlossaryMatch';

describe('glossary STE match hygiene (F38)', () => {
  it('still matches each seeded term string regardless of blurb wording', () => {
    for (const entry of ANNEX3_GLOSSARY_ENTRIES) {
      const segments = segmentGlossaryText(`See ${entry.term} here`);
      const hit = segments.find((s) => s.kind === 'term');
      expect(hit).toMatchObject({
        kind: 'term',
        entry: expect.objectContaining({ id: entry.id }),
      });
    }
  });

  it('still matches each alias when present', () => {
    for (const entry of ANNEX3_GLOSSARY_ENTRIES) {
      for (const alias of entry.aliases ?? []) {
        const segments = segmentGlossaryText(`Token ${alias} end`);
        const hit = segments.find((s) => s.kind === 'term');
        expect(hit).toMatchObject({
          kind: 'term',
          entry: expect.objectContaining({ id: entry.id }),
        });
      }
    }
  });
});

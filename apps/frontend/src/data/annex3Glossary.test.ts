import { describe, expect, it } from 'vitest';
import {
  ANNEX3_GLOSSARY_ENTRIES,
  ANNEX3_LIMITED_MEANING_NOTES,
  getAnnex3GlossaryEntry,
} from './annex3Glossary';

describe('annex3Glossary seed (TC-F38-008)', () => {
  it('keeps a small paraphrase seed with citation on every entry', () => {
    expect(ANNEX3_GLOSSARY_ENTRIES.length).toBeGreaterThan(5);
    expect(ANNEX3_GLOSSARY_ENTRIES.length).toBeLessThanOrEqual(20);
    for (const entry of ANNEX3_GLOSSARY_ENTRIES) {
      expect(entry.citation).toBe('ICAO Annex 3 (2025), Chapter 1');
      expect(entry.shortBlurb.length).toBeGreaterThan(20);
      expect(entry.pageBody.length).toBeGreaterThan(20);
      // Guard against dumping a full chapter heading into fixtures.
      expect(entry.pageBody).not.toMatch(/1\.1\s+Definitions/i);
    }
  });

  it('keeps limited-meaning notes separate from hover catalog', () => {
    expect(ANNEX3_LIMITED_MEANING_NOTES.map((n) => n.id)).toEqual([
      'provide',
      'issue',
      'supply',
    ]);
    expect(getAnnex3GlossaryEntry('provide')).toBeUndefined();
  });

  it('lookup fails closed for unknown ids (TC-F38-008)', () => {
    expect(getAnnex3GlossaryEntry('not-a-real-term')).toBeUndefined();
    expect(getAnnex3GlossaryEntry('')).toBeUndefined();
  });

  it('keeps unique ids and required seed fields (data validation)', () => {
    const ids = ANNEX3_GLOSSARY_ENTRIES.map((e) => e.id);
    expect(new Set(ids).size).toBe(ids.length);
    for (const entry of ANNEX3_GLOSSARY_ENTRIES) {
      expect(entry.id).toMatch(/^[a-z0-9-]+$/);
      expect(entry.term.trim().length).toBeGreaterThan(0);
      expect(entry.shortBlurb).not.toMatch(/Chapter 1\.\s*Definitions/i);
    }
  });
});

import { describe, expect, it } from 'vitest';
import {
  ANNEX3_GLOSSARY_ENTRIES,
  ANNEX3_LIMITED_MEANING_NOTES,
  getAnnex3GlossaryEntry,
} from './annex3Glossary';

const OLD_MWO_PHRASE = 'meteorological watch office';

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

  it('uses short watch-office role wording in operator-facing copy', () => {
    const mwo = getAnnex3GlossaryEntry('mwo');
    expect(mwo?.term).toBe('Watch office');
    expect(mwo?.aliases).toContain('MWO');
    expect(mwo?.shortBlurb.toLowerCase()).not.toContain(OLD_MWO_PHRASE);
    expect(mwo?.pageBody.toLowerCase()).not.toContain(OLD_MWO_PHRASE);
    const sigmet = getAnnex3GlossaryEntry('sigmet');
    expect(sigmet?.shortBlurb.toLowerCase()).toContain('watch office');
    expect(sigmet?.shortBlurb.toLowerCase()).not.toContain(OLD_MWO_PHRASE);
    expect(sigmet?.pageBody.toLowerCase()).not.toContain(OLD_MWO_PHRASE);
  });
});

describe('annex3Glossary watch-office label matrix', () => {
  it('S / V+: mwo lookup returns locked short term and alias for official long form', () => {
    const mwo = getAnnex3GlossaryEntry('mwo');
    expect(mwo).toBeDefined();
    expect(mwo?.term).toBe('Watch office');
    expect(mwo?.aliases).toEqual(
      expect.arrayContaining(['MWO', 'Meteorological watch office']),
    );
    expect(mwo?.shortBlurb.toLowerCase()).toContain('sigmet');
    expect(mwo?.pageBody.toLowerCase()).toContain('watch office');
  });

  it('S: SIGMET and AIRMET blurbs stay free of the long MWO phrase', () => {
    for (const id of ['sigmet', 'airmet', 'mwo'] as const) {
      const entry = getAnnex3GlossaryEntry(id);
      expect(entry).toBeDefined();
      expect(entry?.shortBlurb.toLowerCase()).not.toContain(OLD_MWO_PHRASE);
      expect(entry?.pageBody.toLowerCase()).not.toContain(OLD_MWO_PHRASE);
    }
  });

  it('F / read fault: unknown and blank ids return undefined', () => {
    expect(getAnnex3GlossaryEntry('mwo-office')).toBeUndefined();
    expect(getAnnex3GlossaryEntry('watch-office')).toBeUndefined();
    expect(getAnnex3GlossaryEntry('MWO')).toBeUndefined();
  });

  it('V+: catalog accepts Meteorological watch office only as an alias, not as term', () => {
    const mwo = getAnnex3GlossaryEntry('mwo');
    expect(mwo?.term.toLowerCase()).not.toBe(OLD_MWO_PHRASE);
    expect(mwo?.aliases?.map((a) => a.toLowerCase())).toContain(OLD_MWO_PHRASE);
  });

  it('V-: every seed entry rejects the long MWO phrase in operator-facing blurbs', () => {
    for (const entry of ANNEX3_GLOSSARY_ENTRIES) {
      expect(entry.shortBlurb.toLowerCase()).not.toContain(OLD_MWO_PHRASE);
      expect(entry.pageBody.toLowerCase()).not.toContain(OLD_MWO_PHRASE);
      expect(entry.term.toLowerCase()).not.toBe(OLD_MWO_PHRASE);
    }
  });

  it('M N/A: seed is immutable lookup data (re-read equals first read)', () => {
    const first = getAnnex3GlossaryEntry('mwo');
    const second = getAnnex3GlossaryEntry('mwo');
    expect(second).toBe(first);
    expect(second?.term).toBe('Watch office');
  });
});

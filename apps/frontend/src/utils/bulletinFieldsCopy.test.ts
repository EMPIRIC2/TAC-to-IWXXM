/**
 * Bulletin field copy exists and stays free of planning vocabulary.
 */

import { describe, expect, it } from 'vitest';

import {
  BULLETIN_ID_FIELD_ERROR,
  ISSUING_CENTER_FIELD_ERROR,
} from './bulletinFieldsCopy';
import { findInternalDocRefs, scrubInternalDocRefs } from './internalDocRefGuard';

const CATALOG = {
  ISSUING_CENTER_FIELD_ERROR,
  BULLETIN_ID_FIELD_ERROR,
} as const;

describe('bulletinFieldsCopy', () => {
  it('exports non-empty operator strings', () => {
    expect(ISSUING_CENTER_FIELD_ERROR).toMatch(/issuing center/i);
    expect(ISSUING_CENTER_FIELD_ERROR).toMatch(/4-letter ICAO/i);
    expect(BULLETIN_ID_FIELD_ERROR).toMatch(/bulletin id/i);
    expect(BULLETIN_ID_FIELD_ERROR).toMatch(/4 letters/i);
  });

  it('passes the internal doc-ref guard (success)', () => {
    for (const [id, text] of Object.entries(CATALOG)) {
      expect(findInternalDocRefs(text), id).toEqual([]);
    }
  });

  it('detects and scrubs injected planning tokens (failure + scrub)', () => {
    const poisoned = `${BULLETIN_ID_FIELD_ERROR} [Corpus: product] ADR-022 docs/sessions/x TC-F7-002 EV-048`;
    const hits = findInternalDocRefs(poisoned);
    const names = new Set(hits.map((h) => h.name));
    expect(names.has('Corpus')).toBe(true);
    expect(names.has('ADR')).toBe(true);
    expect(names.has('docs/sessions')).toBe(true);
    expect(names.has('TC')).toBe(true);
    expect(names.has('EV')).toBe(true);

    const scrubbed = scrubInternalDocRefs(poisoned);
    expect(findInternalDocRefs(scrubbed)).toEqual([]);
    expect(scrubbed).toContain('Bulletin ID');
    expect(scrubbed).not.toMatch(/Corpus:|ADR-|docs\/sessions|TC-|EV-/);
  });
});

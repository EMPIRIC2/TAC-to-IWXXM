/**
 * Site terms copy exists and stays free of planning vocabulary.
 */

import { describe, expect, it } from 'vitest';

import {
  SITE_TERMS_BODY,
  SITE_TERMS_CHECKBOX,
  SITE_TERMS_CONTINUE,
  SITE_TERMS_TITLE,
} from './siteTermsCopy';
import { findInternalDocRefs, scrubInternalDocRefs } from './internalDocRefGuard';

const CATALOG = {
  SITE_TERMS_TITLE,
  SITE_TERMS_BODY,
  SITE_TERMS_CHECKBOX,
  SITE_TERMS_CONTINUE,
} as const;

describe('siteTermsCopy', () => {
  it('exports non-empty operator strings', () => {
    expect(SITE_TERMS_TITLE).toBe('Before you continue');
    expect(SITE_TERMS_BODY).toMatch(/incomplete or wrong/i);
    expect(SITE_TERMS_CHECKBOX).toMatch(/agree to continue/i);
    expect(SITE_TERMS_CONTINUE).toBe('Continue');
  });

  it('passes the internal doc-ref guard (success)', () => {
    for (const [id, text] of Object.entries(CATALOG)) {
      expect(findInternalDocRefs(text), id).toEqual([]);
    }
  });

  it('detects and scrubs injected planning tokens (failure + scrub)', () => {
    const poisoned = `${SITE_TERMS_BODY} [Corpus: product] ${['ADR','-','021'].join('')} docs/sessions/terms TC-F21-001 EV-017`;
    const hits = findInternalDocRefs(poisoned);
    const names = new Set(hits.map((h) => h.name));
    expect(names.has('Corpus')).toBe(true);
    expect(names.has('ADR')).toBe(true);
    expect(names.has('docs/sessions')).toBe(true);
    expect(names.has('TC')).toBe(true);
    expect(names.has('EV')).toBe(true);

    const scrubbed = scrubInternalDocRefs(poisoned);
    expect(findInternalDocRefs(scrubbed)).toEqual([]);
    expect(scrubbed).toMatch(/incomplete or wrong/i);
    expect(scrubbed).not.toMatch(/Corpus:|ADR-|docs\/sessions|TC-|EV-/);
  });
});

/**
 * IWXXM product pass-through copy exists and stays free of planning vocabulary.
 */

import { describe, expect, it } from 'vitest';

import {
  IWXXM_PRODUCT_CONVERT_ARIA,
  IWXXM_PRODUCT_CONVERT_LABEL,
  IWXXM_PRODUCT_HELP,
} from './iwxxmProductCopy';
import { findInternalDocRefs, scrubInternalDocRefs } from './internalDocRefGuard';

const CATALOG = {
  IWXXM_PRODUCT_HELP,
  IWXXM_PRODUCT_CONVERT_LABEL,
  IWXXM_PRODUCT_CONVERT_ARIA,
} as const;

describe('iwxxmProductCopy', () => {
  it('exports non-empty operator strings', () => {
    expect(IWXXM_PRODUCT_HELP).toMatch(/pass-through/i);
    expect(IWXXM_PRODUCT_HELP).toMatch(/TAC text is rejected/i);
    expect(IWXXM_PRODUCT_CONVERT_LABEL).toBe('Lint & validate');
    expect(IWXXM_PRODUCT_CONVERT_ARIA).toMatch(/no TAC convert/i);
  });

  it('passes the internal doc-ref guard (success)', () => {
    for (const [id, text] of Object.entries(CATALOG)) {
      expect(findInternalDocRefs(text), id).toEqual([]);
    }
  });

  it('detects and scrubs injected planning tokens (failure + scrub)', () => {
    const poisoned = `${IWXXM_PRODUCT_HELP} [Corpus: api] ${['ADR','-','045'].join('')} docs/sessions/s TC-EV048-003 EV-080`;
    const hits = findInternalDocRefs(poisoned);
    const names = new Set(hits.map((h) => h.name));
    expect(names.has('Corpus')).toBe(true);
    expect(names.has('ADR')).toBe(true);
    expect(names.has('docs/sessions')).toBe(true);
    expect(names.has('TC')).toBe(true);
    expect(names.has('EV')).toBe(true);

    const scrubbed = scrubInternalDocRefs(poisoned);
    expect(findInternalDocRefs(scrubbed)).toEqual([]);
    expect(scrubbed).toMatch(/pass-through/i);
    expect(scrubbed).not.toMatch(/Corpus:|ADR-|docs\/sessions|TC-|EV-/);
  });
});

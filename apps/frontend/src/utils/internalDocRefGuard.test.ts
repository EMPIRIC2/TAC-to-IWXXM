/**
 * TC-EV048-003/005 — FE operator string catalogs free of internal planning vocabulary.
 *
 * [Corpus: tests] [Corpus: product §F7]
 */

import { describe, expect, it } from 'vitest';

import { findInternalDocRefs, INTERNAL_DOC_REF_ALLOWLIST } from './internalDocRefGuard';
import { collectOperatorVisibleCopy } from './operatorVisibleCopy';

describe('TC-EV048 internal doc ref guard (FE)', () => {
  it('TC-EV048-005: detects synthetic planning cites', () => {
    const poisoned =
      'Soft-preview (ADR-022); see #702 and TC-F7-002 / E11-31 / EV-040 / S011 / F31 [Corpus: product]';
    const hits = findInternalDocRefs(poisoned);
    const names = new Set(hits.map((h) => h.name));
    expect(names.has('ADR')).toBe(true);
    expect(names.has('#NNN')).toBe(true);
    expect(names.has('TC')).toBe(true);
    expect(names.has('E##')).toBe(true);
    expect(names.has('EV')).toBe(true);
    expect(names.has('S0')).toBe(true);
    expect(names.has('Corpus')).toBe(true);
    expect(names.has('Fn')).toBe(true);
  });

  it('TC-EV048-005: clean operator copy passes', () => {
    expect(
      findInternalDocRefs(
        'Soft-preview: best-effort IWXXM with failure spans on partial convert.',
      ),
    ).toEqual([]);
  });

  it('does not report an explicitly documented allowlisted token', () => {
    INTERNAL_DOC_REF_ALLOWLIST.add('ADR-022');
    try {
      expect(findInternalDocRefs('ADR-022')).toEqual([]);
    } finally {
      INTERNAL_DOC_REF_ALLOWLIST.delete('ADR-022');
    }
  });

  it('TC-EV048-003: operator-visible catalogs pass guard', () => {
    const leaks: string[] = [];
    for (const { id, text } of collectOperatorVisibleCopy()) {
      const hits = findInternalDocRefs(text);
      if (hits.length > 0) {
        leaks.push(`${id}: ${hits.map((h) => `${h.name}=${h.token}`).join(', ')}`);
      }
    }
    expect(leaks, leaks.join('\n')).toEqual([]);
  });
});

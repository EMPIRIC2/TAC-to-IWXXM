/**
 * Conversion profile editor copy exists and stays free of planning vocabulary.
 */

import { describe, expect, it } from 'vitest';

import * as conversionProfilesCopy from './conversionProfilesCopy';
import { findInternalDocRefs, scrubInternalDocRefs } from './internalDocRefGuard';

function collectStringEntries(
  mod: Record<string, unknown>,
): Array<{ id: string; text: string }> {
  const out: Array<{ id: string; text: string }> = [];
  for (const [id, value] of Object.entries(mod)) {
    if (typeof value === 'string') {
      out.push({ id, text: value });
    }
  }
  return out;
}

describe('conversionProfilesCopy', () => {
  const strings = collectStringEntries(
    conversionProfilesCopy as Record<string, unknown>,
  );

  it('exports a non-empty string catalog and confirm helper', () => {
    expect(strings.length).toBeGreaterThan(50);
    expect(conversionProfilesCopy.PROFILES_EDITOR_TITLE).toBe('Conversion profiles');
    expect(conversionProfilesCopy.PROFILES_EDITOR_SUBTITLE.length).toBeGreaterThan(20);
    const confirm =
      conversionProfilesCopy.CONVERT_PROFILE_LIBRARY_RESET_CONFIRM('CA_ECCC');
    expect(confirm).toMatch(/Change profile to CA_ECCC/);
    expect(confirm).toMatch(/reset Decoding/i);
  });

  it('passes the internal doc-ref guard for every string export (success)', () => {
    const leaks: string[] = [];
    for (const { id, text } of strings) {
      const hits = findInternalDocRefs(text);
      if (hits.length > 0) {
        leaks.push(`${id}: ${hits.map((h) => `${h.name}=${h.token}`).join(', ')}`);
      }
    }
    expect(leaks, leaks.join('\n')).toEqual([]);
  });

  it('confirm helper output also passes the guard (success)', () => {
    const text = conversionProfilesCopy.CONVERT_PROFILE_LIBRARY_RESET_CONFIRM('ICAO');
    expect(findInternalDocRefs(text)).toEqual([]);
  });

  it('detects and scrubs injected planning tokens (failure + scrub)', () => {
    const base = conversionProfilesCopy.PROFILES_EDITOR_SUBTITLE;
    const poisoned = `${base} [Corpus: product] ADR-933 docs/sessions/profiles TC-F7-w EV-933`;
    const hits = findInternalDocRefs(poisoned);
    const names = new Set(hits.map((h) => h.name));
    expect(names.has('Corpus')).toBe(true);
    expect(names.has('ADR')).toBe(true);
    expect(names.has('docs/sessions')).toBe(true);
    expect(names.has('TC')).toBe(true);
    expect(names.has('EV')).toBe(true);

    const scrubbed = scrubInternalDocRefs(poisoned);
    expect(findInternalDocRefs(scrubbed)).toEqual([]);
    expect(scrubbed).toMatch(/Inspect deployed profiles/i);
    expect(scrubbed).not.toMatch(/Corpus:|ADR-|docs\/sessions|TC-|EV-/);
  });
});

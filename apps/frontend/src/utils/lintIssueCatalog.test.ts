/**
 * T5.3 / TC-F15-004 — catalog tooltip resolver (E11-29 / E11-31).
 * T5.1 / E15-14 — TAF tag filter + list-copy helpers (red until T5.2 exports).
 */

import { describe, expect, it } from 'vitest';
import { indexCatalogByCode, resolveLintIssueTooltip } from './lintIssueCatalog';
import * as lintIssueCatalog from './lintIssueCatalog';
import type { LintIssueCatalogEntry } from './api';

/** T5.2 will export these; cast keeps tsc green while Vitest stays red. */
const filterCatalogByTag = (
  lintIssueCatalog as unknown as {
    filterCatalogByTag: (
      entries: LintIssueCatalogEntry[],
      tag: string,
    ) => LintIssueCatalogEntry[];
  }
).filterCatalogByTag;

const formatCatalogEntryCopy = (
  lintIssueCatalog as unknown as {
    formatCatalogEntryCopy: (entry: LintIssueCatalogEntry) => string;
  }
).formatCatalogEntryCopy;

const SAMPLE: LintIssueCatalogEntry[] = [
  {
    code: 'MISSING_TERMINATOR',
    severity: 'info',
    message_template: "Reports in bulletins end with '=' — add it before publishing",
    product: null,
    tags: ['terminator', 'metar', 'speci'],
  },
  {
    code: 'INVALID_WEATHER',
    severity: 'error',
    message_template: '{product} invalid present weather token {token!r}',
    product: null,
    tags: ['weather', 'metar', 'speci', 'r3'],
  },
];

const TAF_SAMPLE: LintIssueCatalogEntry[] = [
  {
    code: 'FM_PRESENT',
    severity: 'info',
    message_template: '{product} FM change group present',
    product: 'taf',
    tags: ['change', 'taf', 't2', 'fm'],
  },
  {
    code: 'CAVOK_PRESENT',
    severity: 'info',
    message_template: '{product} CAVOK present',
    product: null,
    tags: ['cavok', 'metar', 'speci', 'taf'],
  },
  {
    code: 'MISSING_TERMINATOR',
    severity: 'info',
    message_template: "Reports end with '='",
    product: null,
    tags: ['terminator', 'metar', 'speci'],
  },
];

describe('lintIssueCatalog tooltip resolver (T5.3)', () => {
  it('indexes entries by code', () => {
    const byCode = indexCatalogByCode(SAMPLE);
    expect(byCode.size).toBe(2);
    expect(byCode.get('MISSING_TERMINATOR')?.severity).toBe('info');
  });

  it('resolves severity + message_template for a known code', () => {
    const byCode = indexCatalogByCode(SAMPLE);
    const tip = resolveLintIssueTooltip(byCode, 'MISSING_TERMINATOR');
    expect(tip).toContain('info:');
    expect(tip).toContain("end with '='");
  });

  it('falls back when code is missing from catalog', () => {
    const byCode = indexCatalogByCode(SAMPLE);
    expect(resolveLintIssueTooltip(byCode, 'NOT_A_REAL_CODE')).toBe(
      'NOT_A_REAL_CODE (not in loaded catalog)',
    );
  });
});

describe('lintIssueCatalog TAF tag helpers (T5.1 / E15-14)', () => {
  it('filterCatalogByTag keeps rows that include the tag (case-insensitive)', () => {
    const filtered = filterCatalogByTag(TAF_SAMPLE, 'taf');
    expect(filtered.map((e: LintIssueCatalogEntry) => e.code)).toEqual([
      'FM_PRESENT',
      'CAVOK_PRESENT',
    ]);
  });

  it('filterCatalogByTag with empty/whitespace tag returns all rows', () => {
    expect(filterCatalogByTag(TAF_SAMPLE, '')).toHaveLength(3);
    expect(filterCatalogByTag(TAF_SAMPLE, '   ')).toHaveLength(3);
  });

  it('formatCatalogEntryCopy includes severity, tags, and product when set', () => {
    const withProduct = formatCatalogEntryCopy(TAF_SAMPLE[0]);
    expect(withProduct).toContain('FM_PRESENT');
    expect(withProduct).toContain('info');
    expect(withProduct).toMatch(/tags:\s*change,\s*taf/i);
    expect(withProduct).toMatch(/product:\s*taf/i);

    const shared = formatCatalogEntryCopy(TAF_SAMPLE[1]);
    expect(shared).toContain('CAVOK_PRESENT');
    expect(shared).toMatch(/tags:.*taf/i);
    expect(shared).not.toMatch(/product:/i);
  });
});

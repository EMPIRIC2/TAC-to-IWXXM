/**
 * Fuller issue descriptions for lint and validation rows (F7 / F10 / F15).
 */
import { describe, expect, it } from 'vitest';
import type { LintIssueCatalogEntry } from '@/utils/api';
import { findInternalDocRefs } from '@/utils/internalDocRefGuard';
import { ISSUE_DETAIL_EMPTY } from '@/utils/issueDetailCopy';
import {
  buildIssueDetail,
  catalogCodeInMessage,
  issueDetailFromConsoleLine,
  issueDetailFromUnknown,
} from '@/utils/issueDetail';

const ENTRY: LintIssueCatalogEntry = {
  code: 'MISSING_TERMINATOR',
  severity: 'info',
  message_template: "Reports in bulletins end with '='",
  product: 'METAR',
  tags: ['terminator', ' '],
  source_attribution: 'WMO code list',
};

describe('buildIssueDetail', () => {
  it('fills rule, source, product, and tags from the catalog', () => {
    const detail = buildIssueDetail({
      code: 'MISSING_TERMINATOR',
      severity: 'warning',
      message: 'Add the end marker',
      hint: 'End the report with =',
      location: 'line 1',
      start: 4,
      end: 8,
      catalog: ENTRY,
    });
    expect(detail.rule).toBe("Reports in bulletins end with '='");
    expect(detail.source).toBe('WMO code list');
    expect(detail.product).toBe('METAR');
    expect(detail.tags).toBe('terminator');
    expect(detail.location).toBe('line 1');
    expect(detail.hint).toBe('End the report with =');
  });

  it('hides a rule that repeats the message and uses a character span', () => {
    const detail = buildIssueDetail({
      message: "Reports in bulletins end with '='",
      start: 0,
      end: 2,
      catalog: {
        ...ENTRY,
        source_attribution: '  ',
        source_id: 'wmo',
        source_url: 'https://example.com',
      },
    });
    expect(detail.rule).toBe(ISSUE_DETAIL_EMPTY);
    expect(detail.code).toBe('MISSING_TERMINATOR');
    expect(detail.severity).toBe('info');
    expect(detail.source).toBe('wmo (https://example.com)');
    expect(detail.location).toBe('Characters 0–2');
  });

  it('uses a source id without a url and an em dash for a blank row', () => {
    const withId = buildIssueDetail({
      catalog: {
        ...ENTRY,
        source_attribution: null,
        source_id: 'annex-3',
        source_url: null,
      },
    });
    expect(withId.source).toBe('annex-3');
    const empty = buildIssueDetail({
      catalog: {
        ...ENTRY,
        source_attribution: null,
        source_id: null,
        product: null,
        tags: [],
      },
    });
    expect(empty.source).toBe(ISSUE_DETAIL_EMPTY);
    expect(empty.message).toBe(ISSUE_DETAIL_EMPTY);
    expect(empty.product).toBe(ISSUE_DETAIL_EMPTY);
    expect(empty.tags).toBe(ISSUE_DETAIL_EMPTY);
    expect(buildIssueDetail({ start: 1 }).location).toBe(ISSUE_DETAIL_EMPTY);
  });

  it('scrubs EV / ticket / TC-EV planning tokens from message and tags', () => {
    const detail = buildIssueDetail({
      code: 'MISSING_TC_IDENTITY',
      severity: 'error',
      message: 'TC SIGMET missing cyclone identity (TC … PSN) - #829 / TC-EV030-004',
      catalog: {
        code: 'MISSING_TC_IDENTITY',
        severity: 'error',
        message_template:
          'TC SIGMET missing cyclone identity (TC … PSN). Error: correct the TAC.',
        product: 'sigmet',
        tags: ['tc', 'cyclone', 'sigmet', 'ev030'],
        source_attribution: 'EUR Doc 014 public',
      },
    });
    expect(detail.code).toBe('MISSING_TC_IDENTITY');
    expect(detail.message).toBe('TC SIGMET missing cyclone identity (TC … PSN)');
    expect(detail.tags).toBe('tc, cyclone, sigmet');
    expect(findInternalDocRefs(detail.message)).toEqual([]);
    expect(findInternalDocRefs(detail.tags)).toEqual([]);
    expect(detail.tags.toLowerCase()).not.toContain('ev030');
  });

  it('scrubs F26 theme crumbs and feature/theme tags from VAA issue detail', () => {
    const detail = buildIssueDetail({
      code: 'VAA_FCST_NO_VA_EXP',
      severity: 'info',
      message:
        'VAA forecast NO VA EXP - status NO_VOLCANIC_ASH_EXPECTED (F26 theme V1)',
      catalog: {
        code: 'VAA_FCST_NO_VA_EXP',
        severity: 'info',
        message_template:
          'VAA forecast NO VA EXP - status NO_VOLCANIC_ASH_EXPECTED (F26 theme V1)',
        product: 'vaa',
        tags: ['forecast', 'no_va_exp', 'vaa', 'v1', 'f26'],
        source_attribution: 'icao-annex-3',
      },
    });
    expect(detail.message).toBe(
      'VAA forecast NO VA EXP - status NO_VOLCANIC_ASH_EXPECTED',
    );
    expect(detail.tags).toBe('forecast, no_va_exp, vaa');
    expect(detail.message).not.toMatch(/F26|theme V1/i);
    expect(detail.tags.toLowerCase()).not.toMatch(/\bf26\b|\bv1\b/);
  });
});

describe('catalogCodeInMessage', () => {
  const catalog = new Map([['MISSING_TERMINATOR', ENTRY]]);

  it('returns the first loaded code', () => {
    expect(catalogCodeInMessage('no codes', catalog)).toBeUndefined();
    expect(catalogCodeInMessage('[UNKNOWN] then [MISSING_TERMINATOR]', catalog)).toBe(
      'MISSING_TERMINATOR',
    );
    expect(catalogCodeInMessage('[MISSING_TERMINATOR]', undefined)).toBeUndefined();
    expect(catalogCodeInMessage('[MISSING_TERMINATOR]', new Map())).toBeUndefined();
  });
});

describe('issueDetailFromConsoleLine', () => {
  it('attaches the catalog row for a known code', () => {
    const detail = issueDetailFromConsoleLine(
      { level: 'warn', message: 'Fix [MISSING_TERMINATOR]' },
      new Map([['MISSING_TERMINATOR', ENTRY]]),
    );
    expect(detail.code).toBe('MISSING_TERMINATOR');
    expect(detail.severity).toBe('warn');
    expect(detail.rule).toContain('=');
  });

  it('keeps the line when no catalog code is present', () => {
    const detail = issueDetailFromConsoleLine({ level: 'error', message: 'plain' });
    expect(detail.code).toBe(ISSUE_DETAIL_EMPTY);
    expect(detail.message).toBe('plain');
  });
});

describe('issueDetailFromUnknown', () => {
  it('reads strings, empty values, and diagnostic fields', () => {
    expect(issueDetailFromUnknown('bare').message).toBe('bare');
    expect(issueDetailFromUnknown(null).message).toBe('Issue');
    expect(issueDetailFromUnknown(3).message).toBe('3');
    const detail = issueDetailFromUnknown(
      {
        code: 'XSD',
        detail: 'schema boom',
        remediation: 'Fix the element',
        location: '  ',
        start: 2,
        end: 6,
        severity: 'error',
        hint: '   ',
      },
      new Map([['OTHER', ENTRY]]),
    );
    expect(detail.message).toBe('schema boom');
    expect(detail.hint).toBe('Fix the element');
    expect(detail.location).toBe('Characters 2–6');
    expect(detail.code).toBe('XSD');
  });

  it('uses the catalog when the code is loaded and JSON when the row has neither', () => {
    const loaded = issueDetailFromUnknown(
      { code: 'MISSING_TERMINATOR', message: 'short' },
      new Map([['MISSING_TERMINATOR', ENTRY]]),
    );
    expect(loaded.source).toBe('WMO code list');
    const coded = issueDetailFromUnknown({ code: 'ONLY', start: '1', end: Number.NaN });
    expect(coded.message).toBe(ISSUE_DETAIL_EMPTY);
    expect(coded.location).toBe(ISSUE_DETAIL_EMPTY);
    expect(issueDetailFromUnknown({ other: true }).message).toContain('other');
    const circular: Record<string, unknown> = {};
    circular.self = circular;
    expect(issueDetailFromUnknown(circular).message).toBe('[object Object]');
  });
});

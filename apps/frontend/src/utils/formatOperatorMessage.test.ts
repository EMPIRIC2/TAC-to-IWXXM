/**
 * Operator message template formatting (no raw `{product}` braces).
 */
import { describe, expect, it } from 'vitest';
import {
  formatOperatorMessageTemplate,
  operatorProductLabel,
} from './formatOperatorMessage';
import { buildIssueDetail } from './issueDetail';
import { indexCatalogByCode, resolveLintIssueTooltip } from './lintIssueCatalog';
import type { LintIssueCatalogEntry } from './api';

describe('formatOperatorMessageTemplate', () => {
  it('substitutes product and hides braces (success)', () => {
    const text = formatOperatorMessageTemplate(
      'This {product} is an amendment (AMD). Conversion can continue.',
      { product: 'taf' },
    );
    expect(text).toBe('This TAF is an amendment (AMD). Conversion can continue.');
    expect(text).not.toContain('{');
  });

  it('falls back to report when product is missing (failure / fallback)', () => {
    const text = formatOperatorMessageTemplate(
      'This {product} includes CAVOK. Conversion can continue.',
    );
    expect(text).toBe('This report includes CAVOK. Conversion can continue.');
  });

  it('formats token!r without leaving braces (validation)', () => {
    const text = formatOperatorMessageTemplate(
      'Invalid token {token!r} on {product}.',
      { product: 'METAR', token: 'XX' },
    );
    expect(text).toBe('Invalid token "XX" on METAR.');
  });

  it('omits unknown placeholders instead of showing braces (failure)', () => {
    const text = formatOperatorMessageTemplate('Keep {product} drop {nope}.', {
      product: 'TAF',
    });
    expect(text).toBe('Keep TAF drop .');
    expect(text).not.toContain('{');
  });
});

describe('operatorProductLabel', () => {
  it('uppercases known products and defaults blank to report', () => {
    expect(operatorProductLabel('taf')).toBe('TAF');
    expect(operatorProductLabel('')).toBe('report');
    expect(operatorProductLabel(null)).toBe('report');
  });
});

describe('catalog and issue detail join path', () => {
  const amd: LintIssueCatalogEntry = {
    code: 'AMD_PRESENT',
    severity: 'info',
    message_template: 'This {product} is an amendment (AMD). Conversion can continue.',
    product: 'taf',
    tags: ['modifier', 'taf'],
  };

  it('tooltip substitutes product from catalog (mutation / read)', () => {
    const tip = resolveLintIssueTooltip(indexCatalogByCode([amd]), 'AMD_PRESENT');
    expect(tip).toContain('This TAF is an amendment (AMD)');
    expect(tip).not.toContain('{product}');
  });

  it('issue detail rule field substitutes product (success)', () => {
    const detail = buildIssueDetail({
      code: 'AMD_PRESENT',
      severity: 'info',
      message: 'This TAF is an amendment (AMD). Conversion can continue.',
      catalog: amd,
    });
    // Rule hides when identical to message after format.
    expect(detail.message).toContain('TAF');
    expect(detail.message).not.toContain('{product}');
  });

  it('unknown catalog code stays safe (failure)', () => {
    expect(resolveLintIssueTooltip(indexCatalogByCode([amd]), 'NOPE')).toBe(
      'NOPE (not in loaded catalog)',
    );
  });

  it('create + validation pass: index then resolve new catalog row', () => {
    const created: LintIssueCatalogEntry = {
      ...amd,
      code: 'COR_PRESENT',
      message_template:
        'This {product} is a correction (COR). Conversion can continue.',
    };
    const tip = resolveLintIssueTooltip(
      indexCatalogByCode([amd, created]),
      'COR_PRESENT',
    );
    expect(tip).toContain('This TAF is a correction (COR)');
    expect(tip).not.toContain('{');
  });

  it('update + validation pass: replacing template updates tooltip text', () => {
    const updated: LintIssueCatalogEntry = {
      ...amd,
      message_template: 'Updated AMD wording for {product}.',
    };
    const tip = resolveLintIssueTooltip(indexCatalogByCode([updated]), 'AMD_PRESENT');
    expect(tip).toContain('Updated AMD wording for TAF.');
    expect(tip).not.toContain('{product}');
  });

  it('delete + allowed: removing a catalog row yields not-found fault', () => {
    const tip = resolveLintIssueTooltip(indexCatalogByCode([]), 'AMD_PRESENT');
    expect(tip).toBe('AMD_PRESENT (not in loaded catalog)');
  });
});

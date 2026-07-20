/**
 * T5.3 / TC-F15-004 — catalog tooltip resolver (E11-29 / E11-31).
 */

import { describe, expect, it } from 'vitest';
import { indexCatalogByCode, resolveLintIssueTooltip } from './lintIssueCatalog';
import type { LintIssueCatalogEntry } from './api';

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

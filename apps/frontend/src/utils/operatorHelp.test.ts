/**
 * TC-EV047-011 — Help URLs for operator one-pager / handbook.
 */

import { describe, expect, it } from 'vitest';

import { OPERATOR_HANDBOOK_URL, OPERATOR_ONE_PAGER_URL } from './operatorHelp';

describe('operatorHelp (EV-047 / UJ-054)', () => {
  it('points Help at the operator one-pager on the public docs path', () => {
    expect(OPERATOR_ONE_PAGER_URL).toContain('docs/guides/operator-one-pager.md');
    expect(OPERATOR_ONE_PAGER_URL).toMatch(/^https:\/\//);
  });

  it('exposes the handbook URL for deeper reading', () => {
    expect(OPERATOR_HANDBOOK_URL).toContain('docs/guides/operator-handbook.md');
  });
});

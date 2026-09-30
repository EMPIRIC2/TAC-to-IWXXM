/**
 * TC-EV1313-001 — Console lint code deep-links into Rule catalogs focus.
 */

import { beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { WorkbenchConsole } from '../app/components/WorkbenchConsole';
import { LintValidationCatalogPage } from '../app/components/LintValidationCatalogPage';
import type { LintIssueCatalogEntry } from '@/utils/api';

const fetchLintIssueCatalog = vi.hoisted(() => vi.fn());
const fetchRuleCatalog = vi.hoisted(() => vi.fn());

vi.mock('@/utils/api', () => ({
  fetchLintIssueCatalog: (...args: unknown[]) => fetchLintIssueCatalog(...args),
  fetchRuleCatalog: (...args: unknown[]) => fetchRuleCatalog(...args),
}));

const ENTRY: LintIssueCatalogEntry = {
  code: 'MISSING_TERMINATOR',
  severity: 'info',
  message_template: "Reports in bulletins end with '='",
  product: null,
  tags: ['terminator'],
  family: 'lint',
  issue_type: 'structure',
  source_access: 'public',
  source_url: 'https://example.com/term',
  status: 'verified',
  semantic_profiles: [],
  exchange_profiles: [],
};

describe('TC-EV1313-001 console → catalog deep link', () => {
  beforeEach(() => {
    fetchLintIssueCatalog.mockReset();
    fetchRuleCatalog.mockReset();
    fetchLintIssueCatalog.mockResolvedValue({ issues: [ENTRY] });
    fetchRuleCatalog.mockResolvedValue({ family: 'conversion', items: [] });
  });

  it('invokes onOpenCatalogCode when a bracketed lint code is activated', async () => {
    const user = userEvent.setup();
    const onOpenCatalogCode = vi.fn();
    const byCode = new Map([['MISSING_TERMINATOR', ENTRY]]);
    render(
      <WorkbenchConsole
        defaultOpen
        lines={[
          {
            at: Date.now(),
            level: 'warn',
            source: 'lint',
            message: 'Fix [MISSING_TERMINATOR] before publish',
          },
        ]}
        catalogByCode={byCode}
        onOpenCatalogCode={onOpenCatalogCode}
      />,
    );
    const token = await screen.findByTestId('lint-code-tooltip-MISSING_TERMINATOR');
    expect(token).toHaveAttribute(
      'aria-label',
      'Open MISSING_TERMINATOR in rule catalogs',
    );
    await user.click(token);
    expect(onOpenCatalogCode).toHaveBeenCalledWith('MISSING_TERMINATOR');
  });

  it('focuses and highlights the matching catalog row', async () => {
    const onFocusHandled = vi.fn();
    const scrollIntoView = vi.fn();
    HTMLElement.prototype.scrollIntoView = scrollIntoView;

    render(
      <LintValidationCatalogPage
        focusCode="MISSING_TERMINATOR"
        initialFamily="lint"
        onFocusHandled={onFocusHandled}
      />,
    );
    const row = await screen.findByTestId(
      'lint-validation-catalog-entry-MISSING_TERMINATOR',
    );
    expect(scrollIntoView).toHaveBeenCalled();
    expect(row.className).toMatch(/ring-sky/);
    expect(onFocusHandled).toHaveBeenCalled();
  });
});

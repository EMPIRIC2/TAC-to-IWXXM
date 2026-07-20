/**
 * T5.4 / TC-F15-004 — console code tooltips from catalog (E11-29).
 */

import { describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { WorkbenchConsole } from './WorkbenchConsole';
import type { LintIssueCatalogEntry } from '@/utils/api';

vi.mock('/utils/convertParams', () => ({
  consoleLevelPasses: () => true,
}));

const ENTRY: LintIssueCatalogEntry = {
  code: 'MISSING_TERMINATOR',
  severity: 'info',
  message_template: "Reports in bulletins end with '='",
  product: null,
  tags: ['terminator'],
};

describe('WorkbenchConsole catalog tooltips (T5.4)', () => {
  it('renders dotted underline tooltip span for [CODE] tokens', async () => {
    const user = userEvent.setup();
    const byCode = new Map([['MISSING_TERMINATOR', ENTRY]]);
    render(
      <WorkbenchConsole
        defaultOpen
        lines={[
          {
            level: 'warn',
            source: 'lint-tac',
            message: '1 issue(s): [MISSING_TERMINATOR] add terminator',
            at: 1,
          },
        ]}
        catalogByCode={byCode}
        catalogEntries={[ENTRY]}
      />,
    );
    const tip = screen.getByTestId('lint-code-tooltip-MISSING_TERMINATOR');
    expect(tip).toHaveAttribute('title', "info: Reports in bulletins end with '='");
    expect(screen.getByTestId('lint-issue-catalog-panel')).toBeInTheDocument();
    await user.click(screen.getByTestId('lint-issue-catalog-toggle'));
    expect(screen.getByTestId('lint-issue-catalog-list')).toHaveTextContent(
      'MISSING_TERMINATOR',
    );
  });
});

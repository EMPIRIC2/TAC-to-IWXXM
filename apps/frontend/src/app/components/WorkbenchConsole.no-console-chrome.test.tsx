/**
 * UX-2026-10-31-drop-console-chrome — the operator log surface renders inline
 * without a collapsible "Console" shell/heading. Log lines are visible by
 * default; the Lint issue catalog and Clear log remain usable.
 */

import { describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { WorkbenchConsole } from './WorkbenchConsole';
import type { LintIssueCatalogEntry } from '@/utils/api';

const CATALOG: LintIssueCatalogEntry[] = [
  {
    code: 'US_TAF_BECMG_FORBIDDEN',
    severity: 'error',
    message_template: 'TAF BECMG is forbidden',
    tags: ['taf'],
  } as unknown as LintIssueCatalogEntry,
];

describe('WorkbenchConsole drops the Console chrome (UX-2026-10-31)', () => {
  it('shows no Console heading or collapse toggle', () => {
    render(
      <WorkbenchConsole
        lines={[{ level: 'warn', source: 'lint-tac', message: '1 issue(s)', at: 1 }]}
      />,
    );
    expect(screen.queryByTestId('workbench-console-toggle')).toBeNull();
    expect(screen.queryByText(/^Console$/)).toBeNull();
    expect(screen.getByTestId('workbench-console')).not.toHaveTextContent(
      /\bConsole\b/,
    );
  });

  it('renders log lines inline by default (no toggle needed)', () => {
    render(
      <WorkbenchConsole
        lines={[{ level: 'warn', source: 'lint-tac', message: '1 issue(s)', at: 1 }]}
      />,
    );
    const lines = screen.getByTestId('workbench-console-lines');
    expect(lines).toHaveTextContent(/lint-tac/);
    expect(lines).toHaveTextContent(/1 issue/);
  });

  it('keeps the Lint issue catalog usable', () => {
    render(<WorkbenchConsole lines={[]} catalogEntries={CATALOG} />);
    expect(screen.getByTestId('lint-issue-catalog-toggle')).toHaveTextContent(
      /lint issue catalog/i,
    );
  });

  it('keeps a Clear log control without a Console label', async () => {
    const user = userEvent.setup();
    const onClear = vi.fn();
    render(<WorkbenchConsole lines={[]} onClear={onClear} />);
    const clear = screen.getByTestId('workbench-console-clear');
    expect(clear).toHaveTextContent(/clear log/i);
    await user.click(clear);
    expect(onClear).toHaveBeenCalled();
  });
});

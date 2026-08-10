/**
 * T4.3 — Pull-up workbench console (UJ-017 / TC-F7-004).
 */

import { describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { WorkbenchConsole } from './WorkbenchConsole';

describe('WorkbenchConsole', () => {
  it('shows line count and expands structured messages', async () => {
    const user = userEvent.setup();
    render(
      <WorkbenchConsole
        lines={[
          {
            level: 'warn',
            source: 'lint-tac',
            message: '1 issue(s)',
            at: 1,
          },
        ]}
      />,
    );
    expect(screen.getByTestId('workbench-console')).toHaveTextContent(/1/);
    expect(screen.queryByTestId('workbench-console-lines')).toBeNull();
    await user.click(screen.getByTestId('workbench-console-toggle'));
    expect(screen.getByTestId('workbench-console-lines')).toHaveTextContent(/lint-tac/);
    expect(screen.getByTestId('workbench-console-lines')).toHaveTextContent(/1 issue/);
  });

  it('filters lines below the operator log level', async () => {
    render(
      <WorkbenchConsole
        defaultOpen
        minLogLevel="WARNING"
        lines={[
          { level: 'info', source: 'lint', message: 'ok', at: 1 },
          { level: 'warn', source: 'lint', message: 'watch', at: 2 },
          { level: 'error', source: 'lint', message: 'bad', at: 3 },
        ]}
      />,
    );
    expect(screen.getByTestId('workbench-console')).toHaveTextContent(/2\/3/);
    expect(screen.getByTestId('workbench-console-lines')).toHaveTextContent(/watch/);
    expect(screen.getByTestId('workbench-console-lines')).toHaveTextContent(/bad/);
    expect(screen.getByTestId('workbench-console-lines')).not.toHaveTextContent(
      /\[lint\] ok/,
    );
  });

  it('clear does not crash when onClear provided', async () => {
    const user = userEvent.setup();
    const onClear = vi.fn();
    render(<WorkbenchConsole lines={[]} onClear={onClear} defaultOpen />);
    await user.click(screen.getByTestId('workbench-console-clear'));
    expect(screen.getByTestId('workbench-console-clear')).toHaveTextContent(
      /clear log/i,
    );
    expect(onClear).toHaveBeenCalled();
  });

  it('shows the log-level empty message when lines exist but are filtered out', () => {
    render(
      <WorkbenchConsole
        defaultOpen
        minLogLevel="ERROR"
        lines={[{ level: 'info', source: 'lint', message: 'hidden', at: 1 }]}
      />,
    );

    expect(screen.getByTestId('workbench-console-lines')).toHaveTextContent(
      /no messages at error or above/i,
    );
  });

  it('shows the empty console message when there are no lines', () => {
    render(<WorkbenchConsole defaultOpen lines={[]} />);
    expect(screen.getByTestId('workbench-console-lines')).toHaveTextContent(
      /no messages yet/i,
    );
  });
});

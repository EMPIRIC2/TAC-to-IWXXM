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

  it('clear does not crash when onClear provided', async () => {
    const user = userEvent.setup();
    const onClear = vi.fn();
    render(<WorkbenchConsole lines={[]} onClear={onClear} defaultOpen />);
    await user.click(screen.getByTestId('workbench-console-clear'));
    expect(onClear).toHaveBeenCalled();
  });
});

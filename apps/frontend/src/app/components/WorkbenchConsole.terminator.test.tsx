/**
 * T3.5 / TC-F10-002 §3 — info-level console + Add `=` quick fix (S013 / EV-009).
 */

import { describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { WorkbenchConsole } from './WorkbenchConsole';

describe('WorkbenchConsole terminator quick fix (F10)', () => {
  it('renders info-level lines with distinct styling (not warn/error)', () => {
    render(
      <WorkbenchConsole
        defaultOpen
        lines={[
          {
            level: 'info',
            source: 'lint-tac',
            message: "Reports in bulletins end with '=' — add it before publishing",
            at: 1,
            action: { id: 'add_terminator', label: 'Add `=`' },
          },
        ]}
      />,
    );
    const line = screen
      .getByTestId('workbench-console-lines')
      .querySelector('[data-level="info"]');
    expect(line).toBeTruthy();
    expect(line?.className).toMatch(/sky|cyan|blue|info/i);
    expect(line?.className).not.toMatch(/rose|amber/);
  });

  it('invokes onLineAction when Add `=` is clicked', async () => {
    const user = userEvent.setup();
    const onLineAction = vi.fn();
    render(
      <WorkbenchConsole
        defaultOpen
        onLineAction={onLineAction}
        lines={[
          {
            level: 'info',
            source: 'lint-tac',
            message: "Reports in bulletins end with '=' — add it before publishing",
            at: 1,
            action: { id: 'add_terminator', label: 'Add `=`' },
          },
        ]}
      />,
    );
    await user.click(screen.getByTestId('console-action-add_terminator'));
    expect(onLineAction).toHaveBeenCalledWith('add_terminator');
  });
});

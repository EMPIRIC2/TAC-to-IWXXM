/**
 * EV-053 branch fill — console styling/filter branches.
 */

import { describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { WorkbenchConsole } from './WorkbenchConsole';

vi.mock('/utils/convertParams', () => ({
  consoleLevelPasses: () => true,
}));

describe('WorkbenchConsole branch styling (EV-053)', () => {
  it('renders non-standard line levels with neutral styling', () => {
    render(
      <WorkbenchConsole
        defaultOpen
        lines={
          [
            {
              level: 'debug',
              source: 'assist',
              message: 'trace',
              at: 1,
            },
          ] as unknown as Parameters<typeof WorkbenchConsole>[0]['lines']
        }
      />,
    );

    const line = screen.getByTestId('workbench-console-lines').firstElementChild;
    expect(line).toHaveAttribute('data-level', 'debug');
    expect(line?.className).toMatch(/gray-800/);
  });
});

import { describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen } from '@testing-library/react';
import { TacLintJumps } from './TacLintJumps';
import type { JumpableLintIssue } from '/utils/lintIssueJump';

const issues: JumpableLintIssue[] = [
  { start: 0, end: 5, message: 'Wind group is incomplete', severity: 'error' },
  { start: 6, end: 8, message: 'Unknown group', severity: 'warning' },
];

describe('TacLintJumps', () => {
  it('renders nothing when there are no issues', () => {
    const { container } = render(
      <TacLintJumps issues={[]} activeIndex={null} onSelect={() => undefined} />,
    );
    expect(container).toBeEmptyDOMElement();
  });

  it('lists jumpable issues and skips empty slots', () => {
    const onSelect = vi.fn();
    const hole = [...issues];
    delete (hole as unknown[])[0];
    render(<TacLintJumps issues={hole} activeIndex={null} onSelect={onSelect} />);
    expect(
      screen.queryByRole('button', { name: 'Error: Wind group is incomplete' }),
    ).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Warning: Unknown group' }));
    expect(onSelect).toHaveBeenCalledWith(issues[1]);
  });

  it('selects an issue from the list', () => {
    const onSelect = vi.fn();
    render(<TacLintJumps issues={issues} activeIndex={0} onSelect={onSelect} />);
    expect(
      screen.getByRole('button', { name: 'Error: Wind group is incomplete' }),
    ).toHaveAttribute('aria-pressed', 'true');
    fireEvent.click(screen.getByRole('button', { name: 'Warning: Unknown group' }));
    expect(onSelect).toHaveBeenCalledWith(issues[1]);
    expect(
      screen.queryByRole('button', { name: 'Next TAC issue' }),
    ).not.toBeInTheDocument();
    expect(
      screen.queryByRole('button', { name: 'Previous TAC issue' }),
    ).not.toBeInTheDocument();
  });

  it('emphasizes error rows with destructive text, weight, and tint', () => {
    const withNote: JumpableLintIssue[] = [
      ...issues,
      { start: 9, end: 12, message: 'FIR airspace identity', severity: 'info' },
    ];
    render(
      <TacLintJumps issues={withNote} activeIndex={null} onSelect={() => undefined} />,
    );
    const errorBtn = screen.getByRole('button', {
      name: 'Error: Wind group is incomplete',
    });
    const warningBtn = screen.getByRole('button', {
      name: 'Warning: Unknown group',
    });
    const noteBtn = screen.getByRole('button', {
      name: 'Note: FIR airspace identity',
    });
    expect(errorBtn.className).toMatch(/text-destructive/);
    expect(errorBtn.className).toMatch(/font-semibold/);
    expect(errorBtn.className).toMatch(/bg-destructive\//);
    expect(warningBtn.className).not.toMatch(/text-destructive/);
    expect(warningBtn.className).not.toMatch(/bg-destructive\//);
    expect(noteBtn.className).not.toMatch(/text-destructive/);
    expect(noteBtn.className).not.toMatch(/bg-destructive\//);
    expect(errorBtn).toHaveTextContent('Error: Wind group is incomplete');
  });

  it('treats critical severity like error for destructive chrome', () => {
    render(
      <TacLintJumps
        issues={[
          { start: 0, end: 3, message: 'Schema hard fail', severity: 'critical' },
        ]}
        activeIndex={null}
        onSelect={() => undefined}
      />,
    );
    const btn = screen.getByRole('button', { name: /Schema hard fail/ });
    expect(btn.className).toMatch(/text-destructive/);
    expect(btn.className).toMatch(/bg-destructive\//);
  });

  it('scrubs planning ids from jump labels', () => {
    render(
      <TacLintJumps
        issues={[
          {
            start: 0,
            end: 3,
            message: 'Missing terminator - #829 / EV-030',
            severity: 'error',
          },
        ]}
        activeIndex={null}
        onSelect={() => undefined}
      />,
    );
    expect(
      screen.getByRole('button', { name: 'Error: Missing terminator' }),
    ).toBeInTheDocument();
  });
});

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
});

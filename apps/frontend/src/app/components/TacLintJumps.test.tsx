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

  it('steps and selects issues', () => {
    const onSelect = vi.fn();
    const hole = [...issues];
    delete (hole as unknown[])[0];
    const { rerender } = render(
      <TacLintJumps issues={hole} activeIndex={null} onSelect={onSelect} />,
    );
    fireEvent.click(screen.getByRole('button', { name: 'Next TAC issue' }));
    expect(onSelect).not.toHaveBeenCalled();

    rerender(<TacLintJumps issues={issues} activeIndex={null} onSelect={onSelect} />);
    fireEvent.click(screen.getByRole('button', { name: 'Next TAC issue' }));
    expect(onSelect).toHaveBeenCalledWith(issues[0]);
    fireEvent.click(screen.getByRole('button', { name: 'Previous TAC issue' }));
    expect(onSelect).toHaveBeenCalledWith(issues[1]);
    fireEvent.click(screen.getByRole('button', { name: 'Warning: Unknown group' }));
    expect(onSelect).toHaveBeenLastCalledWith(issues[1]);
  });
});

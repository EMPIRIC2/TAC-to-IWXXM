/**
 * Open and close the issue detail dialog.
 */
import { describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { IssueDetailDialog } from './IssueDetailDialog';
import { buildIssueDetail } from '@/utils/issueDetail';

const DETAIL = buildIssueDetail({
  code: 'XSD',
  severity: 'error',
  message: 'schema boom',
  hint: 'Check the element',
});

describe('IssueDetailDialog', () => {
  it('stays closed until a detail is provided', () => {
    const { rerender } = render(
      <IssueDetailDialog detail={null} onClose={() => undefined} />,
    );
    expect(screen.queryByTestId('issue-detail-dialog')).not.toBeInTheDocument();
    rerender(<IssueDetailDialog detail={DETAIL} onClose={() => undefined} />);
    expect(screen.getByRole('dialog')).toHaveTextContent('schema boom');
  });

  it('closes from the button, Escape, and the backdrop, and ignores other keys and inner clicks', async () => {
    const user = userEvent.setup();
    const onClose = vi.fn();
    render(<IssueDetailDialog detail={DETAIL} onClose={onClose} />);
    await user.keyboard('a');
    expect(onClose).not.toHaveBeenCalled();
    await user.click(screen.getByTestId('issue-detail-dialog'));
    expect(onClose).not.toHaveBeenCalled();
    await user.click(screen.getByTestId('issue-detail-close'));
    expect(onClose).toHaveBeenCalledTimes(1);
    await user.keyboard('{Escape}');
    expect(onClose).toHaveBeenCalledTimes(2);
    await user.click(screen.getByTestId('issue-detail-backdrop'));
    expect(onClose).toHaveBeenCalledTimes(3);
  });
});

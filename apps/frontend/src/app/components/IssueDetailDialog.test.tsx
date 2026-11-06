/**
 * Open and close the issue detail dialog.
 */
import { describe, expect, it, vi } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { IssueDetailDialog } from './IssueDetailDialog';
import { buildIssueDetail } from '@/utils/issueDetail';
import type { IssueDetailModel } from '@/utils/issueDetail';

const DETAIL = buildIssueDetail({
  code: 'XSD',
  severity: 'error',
  message: 'schema boom',
  hint: 'Check the element',
});

const LONG_SOURCE_URL =
  'https://www.icao.int/sites/default/files/EURNAT/Documents/ICAO%20EUR%20Doc%20014.pdf';

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

  it('wraps long Source text and linkifies the URL with a safe new-tab rel', () => {
    const withSource: IssueDetailModel = {
      ...DETAIL,
      source: `icao-eur-doc-014 - ${LONG_SOURCE_URL}`,
    };
    render(<IssueDetailDialog detail={withSource} onClose={() => undefined} />);
    const dialog = screen.getByTestId('issue-detail-dialog');
    expect(dialog.className).toMatch(/overflow-x-hidden/);
    const sourceValue = screen.getByTestId('issue-detail-source-value');
    expect(sourceValue.className).toMatch(/min-w-0/);
    expect(sourceValue.className).toMatch(/break-(?:words|all)/);
    expect(sourceValue).toHaveTextContent('icao-eur-doc-014');
    const link = within(sourceValue).getByRole('link', { name: LONG_SOURCE_URL });
    expect(link).toHaveAttribute('href', LONG_SOURCE_URL);
    expect(link).toHaveAttribute('target', '_blank');
    const rel = link.getAttribute('rel') ?? '';
    expect(rel.split(/\s+/)).toEqual(
      expect.arrayContaining(['noopener', 'noreferrer']),
    );
    expect(link).not.toHaveTextContent('icao-eur-doc-014');
  });
});

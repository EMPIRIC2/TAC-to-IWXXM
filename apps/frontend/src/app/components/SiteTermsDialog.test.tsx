/**
 * Terms dialog open and dismiss paths.
 * @example
 * const _ = true;
 */

import { describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { SiteTermsDialog } from './SiteTermsDialog';
import { dismissSiteTerms } from './dismissSiteTerms';

describe('SiteTermsDialog', () => {
  it('shows the quality terms and closes from the button', async () => {
    const user = userEvent.setup();
    const onClose = vi.fn();
    render(<SiteTermsDialog isOpen onClose={onClose} />);
    expect(screen.getByText(/results can be incomplete or wrong/i)).toBeInTheDocument();
    await user.click(screen.getByRole('button', { name: /close terms of service/i }));
    expect(onClose).toHaveBeenCalledOnce();
  });

  it('closes when the dialog itself is dismissed', async () => {
    const user = userEvent.setup();
    const onClose = vi.fn();
    render(<SiteTermsDialog isOpen onClose={onClose} />);
    await user.keyboard('{Escape}');
    expect(onClose).toHaveBeenCalled();
  });

  it('ignores an open notification and runs close only when dismissed', () => {
    const onClose = vi.fn();
    dismissSiteTerms(true, onClose);
    expect(onClose).not.toHaveBeenCalled();
    dismissSiteTerms(false, onClose);
    expect(onClose).toHaveBeenCalledOnce();
  });
});

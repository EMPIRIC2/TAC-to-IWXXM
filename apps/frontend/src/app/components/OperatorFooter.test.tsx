/**
 * Footer Feedback control opens the beta-feedback issue URL.
 * @example
 * const _ = true;
 */

import { describe, expect, it, vi, beforeEach } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { toast } from 'sonner';

import { OperatorFooter } from './OperatorFooter';
import {
  FEEDBACK_MESSAGE_REQUIRED,
  FEEDBACK_POPUP_BLOCKED,
} from '@/utils/betaFeedback';

vi.mock('sonner', () => ({
  toast: { error: vi.fn() },
}));

describe('OperatorFooter feedback', () => {
  beforeEach(() => {
    vi.mocked(toast.error).mockClear();
  });

  it('shows Feedback with a Beta badge and opens the beta-feedback URL', async () => {
    const user = userEvent.setup();
    const open = vi.spyOn(window, 'open').mockReturnValue({} as Window);
    render(<OperatorFooter onOpenPrivacy={vi.fn()} onOpenTerms={vi.fn()} />);

    const footer = screen.getByTestId('operator-footer');
    const control = within(footer).getByTestId('footer-feedback');
    expect(control).toHaveTextContent('Feedback');
    expect(within(footer).getByTestId('beta-badge')).toHaveTextContent('Beta');

    await user.click(control);
    const dialog = screen.getByTestId('feedback-dialog');
    expect(dialog).toBeInTheDocument();
    expect(within(dialog).getByTestId('beta-badge')).toHaveTextContent('Beta');

    await user.selectOptions(screen.getByLabelText('Category'), 'feature');
    await user.type(screen.getByLabelText('Message'), 'The map froze');
    await user.type(
      screen.getByLabelText('Email or contact (optional)'),
      'ada@example.com',
    );

    const submit = screen.getByTestId('feedback-submit');
    const href = submit.getAttribute('href') ?? '';
    const url = new URL(href);
    expect(url.origin + url.pathname).toBe(
      'https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/new',
    );
    expect(url.searchParams.get('labels')).toBe('beta-feedback');
    expect(
      href.startsWith('https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/new?'),
    ).toBe(true);
    const body = url.searchParams.get('body') ?? '';
    expect(body).toContain('Category: Feature');
    expect(body).toContain('The map froze');
    expect(body).toContain('Contact: ada@example.com');
    expect(body).toContain(`Page: ${window.location.href}`);
    expect(body).not.toMatch(/METAR|<\?xml/);

    await user.click(submit);
    expect(open).toHaveBeenCalledWith(href, '_blank', 'noopener,noreferrer');
    expect(toast.error).not.toHaveBeenCalled();
    expect(screen.queryByTestId('feedback-dialog')).not.toBeInTheDocument();
    open.mockRestore();
  });

  it('asks for a message and toasts when the browser blocks the tab', async () => {
    const user = userEvent.setup();
    const open = vi.spyOn(window, 'open').mockReturnValue(null);
    render(<OperatorFooter onOpenPrivacy={vi.fn()} onOpenTerms={vi.fn()} />);

    await user.click(screen.getByRole('button', { name: 'Open feedback' }));
    await user.click(screen.getByTestId('feedback-submit'));
    expect(open).not.toHaveBeenCalled();
    expect(screen.getByText(FEEDBACK_MESSAGE_REQUIRED)).toBeInTheDocument();

    await user.type(screen.getByLabelText('Message'), 'Need a clearer error');
    await user.clear(screen.getByLabelText('Page (optional)'));
    await user.click(screen.getByTestId('feedback-submit'));
    expect(open).toHaveBeenCalledOnce();
    const blockedUrl = new URL(String(open.mock.calls[0]?.[0]));
    const body = blockedUrl.searchParams.get('body') ?? '';
    expect(blockedUrl.searchParams.get('labels')).toBe('beta-feedback');
    expect(body).toContain('Category: Bug');
    expect(body).toContain('Need a clearer error');
    expect(body).not.toContain('Contact:');
    expect(body).not.toContain('Page:');
    expect(body).not.toMatch(/METAR|<\?xml/);
    expect(toast.error).toHaveBeenCalledWith(FEEDBACK_POPUP_BLOCKED);
    expect(screen.getByTestId('feedback-dialog')).toBeInTheDocument();
    open.mockRestore();
  });
});

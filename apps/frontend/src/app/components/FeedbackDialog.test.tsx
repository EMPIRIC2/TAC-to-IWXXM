/**
 * Feedback dialog — open, submit, cancel, and popup-blocked error.
 */

import { describe, expect, it, vi, beforeEach } from 'vitest';
import { fireEvent, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { toast } from 'sonner';

import { FeedbackDialog } from './FeedbackDialog';
import {
  FEEDBACK_DIALOG_INTRO,
  FEEDBACK_MESSAGE_REQUIRED,
  FEEDBACK_POPUP_BLOCKED,
  FEEDBACK_SUBMIT_LABEL,
} from '@/utils/betaFeedback';
import { findInternalDocRefs } from '@/utils/internalDocRefGuard';

vi.mock('sonner', () => ({
  toast: { error: vi.fn() },
}));

describe('FeedbackDialog', () => {
  beforeEach(() => {
    vi.mocked(toast.error).mockClear();
  });

  it('stays closed when isOpen is false', () => {
    render(<FeedbackDialog isOpen={false} onClose={vi.fn()} />);
    expect(screen.queryByTestId('feedback-dialog')).not.toBeInTheDocument();
  });

  it('opens with plain-language intro free of internal doc refs', () => {
    render(<FeedbackDialog isOpen onClose={vi.fn()} />);
    expect(screen.getByTestId('feedback-dialog')).toBeInTheDocument();
    expect(screen.getByText(FEEDBACK_DIALOG_INTRO)).toBeInTheDocument();
    expect(findInternalDocRefs(FEEDBACK_DIALOG_INTRO)).toEqual([]);
    expect(findInternalDocRefs(FEEDBACK_SUBMIT_LABEL)).toEqual([]);
  });

  it('blocks submit without a message (validation failure)', async () => {
    const user = userEvent.setup();
    const onClose = vi.fn();
    const open = vi.spyOn(window, 'open').mockReturnValue({} as Window);
    render(<FeedbackDialog isOpen onClose={onClose} />);

    await user.click(screen.getByTestId('feedback-submit'));
    expect(open).not.toHaveBeenCalled();
    expect(screen.getByText(FEEDBACK_MESSAGE_REQUIRED)).toBeInTheDocument();
    expect(onClose).not.toHaveBeenCalled();
    open.mockRestore();
  });

  it('submits successfully and closes (success)', async () => {
    const user = userEvent.setup();
    const onClose = vi.fn();
    const open = vi.spyOn(window, 'open').mockReturnValue({} as Window);
    render(<FeedbackDialog isOpen onClose={onClose} />);

    await user.type(screen.getByLabelText('Message'), 'Map froze on convert');
    await user.click(screen.getByTestId('feedback-submit'));

    expect(open).toHaveBeenCalledOnce();
    const href = String(open.mock.calls[0]?.[0]);
    const url = new URL(href);
    expect(url.searchParams.get('labels')).toBe('beta-feedback');
    expect(url.searchParams.get('body') ?? '').toContain('Map froze on convert');
    expect(toast.error).not.toHaveBeenCalled();
    expect(onClose).toHaveBeenCalledOnce();
    open.mockRestore();
  });

  it('toasts when the browser blocks the feedback tab (API/open error)', async () => {
    const user = userEvent.setup();
    const onClose = vi.fn();
    const open = vi.spyOn(window, 'open').mockReturnValue(null);
    render(<FeedbackDialog isOpen onClose={onClose} />);

    await user.type(screen.getByLabelText('Message'), 'Need a clearer error');
    await user.click(screen.getByTestId('feedback-submit'));

    expect(open).toHaveBeenCalledOnce();
    expect(toast.error).toHaveBeenCalledWith(FEEDBACK_POPUP_BLOCKED);
    expect(onClose).not.toHaveBeenCalled();
    expect(screen.getByTestId('feedback-dialog')).toBeInTheDocument();
    open.mockRestore();
  });

  it('cancels via Escape without submitting', async () => {
    const user = userEvent.setup();
    const onClose = vi.fn();
    render(<FeedbackDialog isOpen onClose={onClose} />);

    expect(screen.getByTestId('feedback-dialog')).toBeInTheDocument();
    await user.keyboard('{Escape}');
    expect(onClose).toHaveBeenCalled();
  });

  it('submits through the form element path', async () => {
    const user = userEvent.setup();
    const onClose = vi.fn();
    const open = vi.spyOn(window, 'open').mockReturnValue({} as Window);
    render(<FeedbackDialog isOpen onClose={onClose} />);

    await user.type(screen.getByLabelText('Message'), 'Form submit path');
    const form = screen.getByTestId('feedback-dialog').querySelector('form');
    expect(form).toBeInstanceOf(HTMLFormElement);
    fireEvent.submit(form as HTMLFormElement);

    expect(open).toHaveBeenCalled();
    expect(onClose).toHaveBeenCalledOnce();
    open.mockRestore();
  });
});

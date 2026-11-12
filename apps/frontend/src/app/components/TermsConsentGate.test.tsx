/**
 * Site terms gate — accept vs block until acknowledgement.
 */

import { describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import { TermsConsentGate } from './TermsConsentGate';
import {
  SITE_TERMS_BODY,
  SITE_TERMS_CHECKBOX,
  SITE_TERMS_CONTINUE,
  SITE_TERMS_TITLE,
} from '@/utils/siteTermsCopy';
import { findInternalDocRefs } from '@/utils/internalDocRefGuard';

describe('TermsConsentGate', () => {
  it('blocks continue until the checkbox is checked', async () => {
    const user = userEvent.setup();
    const onAcknowledge = vi.fn();
    render(<TermsConsentGate onAcknowledge={onAcknowledge} />);

    expect(screen.getByTestId('site-terms-gate')).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: SITE_TERMS_TITLE })).toBeInTheDocument();
    expect(screen.getByText(SITE_TERMS_BODY)).toBeInTheDocument();
    expect(screen.getByText(SITE_TERMS_CHECKBOX)).toBeInTheDocument();

    const continueBtn = screen.getByTestId('site-terms-continue');
    expect(continueBtn).toBeDisabled();
    expect(continueBtn).toHaveTextContent(SITE_TERMS_CONTINUE);

    await user.click(continueBtn);
    expect(onAcknowledge).not.toHaveBeenCalled();
  });

  it('acknowledges after the checkbox is checked', async () => {
    const user = userEvent.setup();
    const onAcknowledge = vi.fn();
    render(<TermsConsentGate onAcknowledge={onAcknowledge} />);

    await user.click(screen.getByTestId('site-terms-ack'));
    const continueBtn = screen.getByTestId('site-terms-continue');
    expect(continueBtn).toBeEnabled();

    await user.click(continueBtn);
    expect(onAcknowledge).toHaveBeenCalledOnce();
  });

  it('renders gate copy without internal doc refs', () => {
    render(<TermsConsentGate onAcknowledge={vi.fn()} />);
    for (const text of [
      SITE_TERMS_TITLE,
      SITE_TERMS_BODY,
      SITE_TERMS_CHECKBOX,
      SITE_TERMS_CONTINUE,
    ]) {
      expect(findInternalDocRefs(text)).toEqual([]);
    }
  });
});

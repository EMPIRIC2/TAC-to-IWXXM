/**
 * BetaBadge Vitest — EV-1150 / ADR-043.
 */

import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';

import { BetaBadge } from './BetaBadge';
import { BETA_FEEDBACK_ISSUES_URL } from '@/utils/betaFeedback';

describe('BetaBadge', () => {
  it('renders the Beta label', () => {
    render(<BetaBadge />);
    expect(screen.getByTestId('beta-badge')).toHaveTextContent('Beta');
  });

  it('links to the beta-feedback Issues URL when help is shown', () => {
    render(<BetaBadge showHelp />);
    const link = screen.getByTestId('beta-feedback-link');
    expect(link).toHaveAttribute('href', BETA_FEEDBACK_ISSUES_URL);
    expect(link).toHaveAttribute('target', '_blank');
    expect(link).toHaveAttribute('rel', expect.stringContaining('noopener'));
  });
});

/**
 * StatusBanner unit tests — tone / role / testid contract.
 */

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';

import { StatusBanner } from './StatusBanner';

describe('StatusBanner', () => {
  it('renders warning tone with status role and test id', () => {
    render(
      <StatusBanner tone="warning" data-testid="guest-loss-notice">
        Progress may be lost without signing in.
      </StatusBanner>,
    );
    const el = screen.getByTestId('guest-loss-notice');
    expect(el).toHaveAttribute('role', 'status');
    expect(el).toHaveTextContent(/progress may be lost/i);
    expect(el.className).toMatch(/amber/);
  });

  it('uses info tone for demo notices (distinct from warning amber)', () => {
    render(
      <StatusBanner tone="info" data-testid="demo-example-banner">
        Demo / non-operational example: METAR
      </StatusBanner>,
    );
    const el = screen.getByTestId('demo-example-banner');
    expect(el.className).toMatch(/sky/);
    expect(el.className).not.toMatch(/amber/);
  });

  it('renders optional action slot', () => {
    render(
      <StatusBanner
        tone="warning"
        data-testid="with-action"
        action={<button type="button">Sign in</button>}
      >
        Notice
      </StatusBanner>,
    );
    expect(screen.getByRole('button', { name: 'Sign in' })).toBeInTheDocument();
  });
});

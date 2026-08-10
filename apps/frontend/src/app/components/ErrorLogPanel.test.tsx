import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ErrorLogPanel } from './ErrorLogPanel';

describe('ErrorLogPanel', () => {
  it('renders nothing when log is empty', () => {
    const { container } = render(<ErrorLogPanel log={{ errors: [], issues: [] }} />);
    expect(container).toBeEmptyDOMElement();
  });

  it('shows errors and issues with collapse toggle', async () => {
    const user = userEvent.setup();
    render(
      <ErrorLogPanel
        log={{
          errors: ['Invalid METAR syntax'],
          issues: [
            {
              source: 'parser',
              message: 'Unexpected token',
              severity: 'warning',
              hint: 'Check TAC format',
              code: 'E001',
            },
          ],
        }}
      />,
    );

    expect(screen.getByLabelText(/conversion error log/i)).toBeInTheDocument();
    expect(screen.getByText('Invalid METAR syntax')).toBeInTheDocument();
    expect(screen.getByText(/Unexpected token/)).toBeInTheDocument();
    expect(screen.getByText(/Check TAC format/)).toBeInTheDocument();
    expect(screen.getByText(/Code: E001/)).toBeInTheDocument();

    await user.click(
      screen.getByRole('button', { name: /conversion \/ validation log/i }),
    );
    expect(screen.queryByText('Invalid METAR syntax')).not.toBeInTheDocument();
  });

  it('defaults missing issue severity to error', () => {
    render(
      <ErrorLogPanel
        log={{
          errors: [],
          issues: [
            {
              source: 'parser',
              message: 'Missing severity field',
            },
          ],
        }}
      />,
    );

    expect(
      screen.getByText(/\[error\] parser: Missing severity field/),
    ).toBeInTheDocument();
  });

  it('hides sub-critical issues when the operator log level is CRITICAL', () => {
    render(
      <ErrorLogPanel
        minLogLevel="CRITICAL"
        log={{
          errors: ['Fatal conversion error'],
          issues: [
            {
              source: 'parser',
              message: 'Minor warning',
              severity: 'warning',
            },
          ],
        }}
      />,
    );

    expect(screen.getByText(/Fatal conversion error/)).toBeInTheDocument();
    expect(screen.getByText(/1 · 1 hidden by log level/i)).toBeInTheDocument();
    expect(screen.queryByText(/Minor warning/)).not.toBeInTheDocument();
  });

  it('shows the log-level empty message when everything is filtered out', () => {
    render(
      <ErrorLogPanel
        minLogLevel="CRITICAL"
        log={{
          errors: [],
          issues: [
            {
              source: 'parser',
              message: 'Info only',
              severity: 'info',
            },
          ],
        }}
      />,
    );

    expect(screen.getByText(/0 · 1 hidden by log level/i)).toBeInTheDocument();
    expect(screen.getByText(/no messages at CRITICAL or above/i)).toBeInTheDocument();
  });
});

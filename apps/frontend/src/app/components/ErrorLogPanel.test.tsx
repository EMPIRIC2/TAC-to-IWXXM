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

    await user.click(screen.getByRole('button', { name: /conversion log/i }));
    expect(screen.queryByText('Invalid METAR syntax')).not.toBeInTheDocument();
  });
});

/**
 * Unit tests for PropagateResidualsControl (TC-EV981-003).
 */

import { describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {
  PROPAGATE_RESIDUALS_HELP,
  PROPAGATE_RESIDUALS_LABEL,
  PropagateResidualsControl,
} from './PropagateResidualsControl';

describe('PropagateResidualsControl', () => {
  it('renders plain-language label and help', () => {
    render(<PropagateResidualsControl checked={false} onChange={vi.fn()} />);
    expect(screen.getByTestId('propagate-residuals-toggle')).toBeInTheDocument();
    expect(screen.getByText(PROPAGATE_RESIDUALS_LABEL)).toBeInTheDocument();
    expect(screen.getByText(PROPAGATE_RESIDUALS_HELP)).toBeInTheDocument();
  });

  it('notifies onChange when toggled', async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(<PropagateResidualsControl checked={false} onChange={onChange} />);
    await user.click(screen.getByTestId('propagate-residuals-toggle'));
    expect(onChange).toHaveBeenCalledWith(true);
  });
});

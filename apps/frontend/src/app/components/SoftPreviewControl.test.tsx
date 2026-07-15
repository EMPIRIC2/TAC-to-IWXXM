/**
 * T3.3 — Soft-preview control contract for UJ-016 / #666 (wired in T3.4).
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { SoftPreviewControl } from './SoftPreviewControl';

describe('SoftPreviewControl', () => {
  it('exposes a preview checkbox distinct from hard convert', async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(<SoftPreviewControl checked={false} onChange={onChange} />);

    const toggle = screen.getByTestId('soft-preview-toggle');
    expect(toggle).toBeInTheDocument();
    expect(toggle).toHaveAttribute('type', 'checkbox');
    expect(screen.getByText(/soft-preview|preview/i)).toBeInTheDocument();

    await user.click(toggle);
    expect(onChange).toHaveBeenCalledWith(true);
  });

  it('reflects checked state', () => {
    render(<SoftPreviewControl checked={true} onChange={() => {}} />);
    expect(screen.getByTestId('soft-preview-toggle')).toBeChecked();
  });
});

/**
 * T4.3 — Live IWXXM toggle defaults off (UJ-017 / 04 Batch 1 A).
 */

import { describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { LiveIwxxmToggle } from './LiveIwxxmToggle';

describe('LiveIwxxmToggle', () => {
  it('renders unchecked by default when checked=false', () => {
    render(<LiveIwxxmToggle checked={false} onChange={() => undefined} />);
    expect(screen.getByTestId('live-iwxxm-toggle')).not.toBeChecked();
  });

  it('notifies on toggle', async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(<LiveIwxxmToggle checked={false} onChange={onChange} />);
    await user.click(screen.getByTestId('live-iwxxm-toggle'));
    expect(onChange).toHaveBeenCalledWith(true);
  });
});

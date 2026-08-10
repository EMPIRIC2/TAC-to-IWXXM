/**
 * GoldenExamplesSelect — soft-fail / file-queue absent (TC-F7-008 C5).
 */

import { describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import { GoldenExamplesSelect } from './GoldenExamplesSelect';

describe('GoldenExamplesSelect', () => {
  it('does not offer soft-fail or file-queue examples (C5)', async () => {
    const user = userEvent.setup();
    const onSelectExample = vi.fn();
    render(<GoldenExamplesSelect onSelectExample={onSelectExample} />);

    await user.click(screen.getByTestId('examples-select'));
    const options = await screen.findAllByRole('option');
    const labels = options.map((el) => el.textContent ?? '');
    expect(labels.some((label) => /soft.?fail|file.?queue/i.test(label))).toBe(false);
  });

  it('lists TC SIGMET A6-2-TC as WMO passer and loads on select (TC-EV032-003 / #835 / UJ-039)', async () => {
    const user = userEvent.setup();
    const onSelectExample = vi.fn();
    render(<GoldenExamplesSelect onSelectExample={onSelectExample} />);

    await user.click(screen.getByTestId('examples-select'));
    const option = await screen.findByRole('option', {
      name: /TC SIGMET WMO A6-2-TC.*WMO passer.*sigmet-A6-2-TC/i,
    });
    expect(option).toBeInTheDocument();
    await user.click(option);
    expect(onSelectExample).toHaveBeenCalledWith('sigmet_a6_2_tc');
  });

  it('disables the example picker without calling the selection callback', async () => {
    const user = userEvent.setup();
    const onSelectExample = vi.fn();
    render(<GoldenExamplesSelect disabled onSelectExample={onSelectExample} />);

    const trigger = screen.getByTestId('examples-select');
    expect(trigger).toBeDisabled();
    await user.click(trigger);
    expect(onSelectExample).not.toHaveBeenCalled();
  });
});

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
});

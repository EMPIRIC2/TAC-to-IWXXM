/**
 * Regression: operator label reads "Current Examples" and the selector is never
 * blank / missing its example options (HF-blank-main-current-examples).
 */

import { describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import { GoldenExamplesSelect } from './GoldenExamplesSelect';
import { EXAMPLES } from '@/fixtures/examples/examplesCatalog';

describe('GoldenExamplesSelect — Current Examples label', () => {
  it('labels the control "Current Examples"', () => {
    render(<GoldenExamplesSelect onSelectExample={vi.fn()} />);
    const label = screen.getByText('Current Examples');
    expect(label).toBeInTheDocument();
    expect(label).toHaveAttribute('for', 'examples-select');
  });

  it('no longer shows the bare "Examples" label', () => {
    render(<GoldenExamplesSelect onSelectExample={vi.fn()} />);
    // The accessible label text is exactly "Current Examples".
    expect(screen.queryByText(/^Examples$/)).not.toBeInTheDocument();
  });

  it('renders a usable trigger (non-blank) even with no applicable products', () => {
    render(
      <GoldenExamplesSelect
        onSelectExample={vi.fn()}
        semanticProfile="AU_BOM"
        applicableProducts={[]}
      />,
    );
    // Label + trigger always render so the examples area can never be blank.
    expect(screen.getByText('Current Examples')).toBeInTheDocument();
    const trigger = screen.getByTestId('examples-select');
    expect(trigger).toBeInTheDocument();
    expect(trigger).toHaveTextContent(/Load demo example/i);
  });

  it('keeps a non-empty set of loadable examples (missing-examples regression)', async () => {
    const user = userEvent.setup();
    render(<GoldenExamplesSelect onSelectExample={vi.fn()} />);

    await user.click(screen.getByTestId('examples-select'));
    const options = await screen.findAllByRole('option');
    expect(options.length).toBeGreaterThan(0);
    expect(options.length).toBe(EXAMPLES.length);
    expect(
      options.every((option) => (option.textContent ?? '').trim().length > 0),
    ).toBe(true);
  });

  it('keeps the label free of internal planning references', () => {
    render(<GoldenExamplesSelect onSelectExample={vi.fn()} />);
    expect(screen.getByText('Current Examples').textContent ?? '').not.toMatch(
      /\[Corpus|ADR-|EV-|TC-|#\d|S0\d/,
    );
  });
});

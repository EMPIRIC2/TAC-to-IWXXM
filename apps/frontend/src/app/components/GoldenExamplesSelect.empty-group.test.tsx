/**
 * Branch coverage for empty product groups and plain (non-WMO) labels.
 */
import { describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

vi.mock('@/fixtures/examples/examplesCatalog', () => ({
  EXAMPLE_PRODUCTS: ['METAR', 'SPECI'],
  EXAMPLES: [
    {
      id: 'plain_tac',
      label: 'Plain TAC demo',
      product: 'METAR',
      inputMode: 'tac',
      body: 'METAR KJFK 121251Z=',
      nonOperational: true,
      provenance: 'test',
    },
  ],
}));

import { GoldenExamplesSelect } from './GoldenExamplesSelect';

describe('GoldenExamplesSelect empty groups', () => {
  it('skips products with no TAC examples and labels plain demos without WMO copy', async () => {
    const user = userEvent.setup();
    const onSelectExample = vi.fn();
    render(<GoldenExamplesSelect onSelectExample={onSelectExample} />);

    await user.click(screen.getByTestId('examples-select'));
    const option = await screen.findByRole('option', { name: 'Plain TAC demo' });
    expect(option).toBeInTheDocument();
    expect(screen.queryByText('SPECI')).not.toBeInTheDocument();
    expect(screen.queryByText(/WMO passer/i)).not.toBeInTheDocument();
    await user.click(option);
    expect(onSelectExample).toHaveBeenCalledWith('plain_tac');
  });
});

/**
 * T2.6 — Decode panel Code | Explanation + residual display (UJ-015).
 */

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { DecodePanel } from './DecodePanel';

describe('DecodePanel', () => {
  it('is collapsible and shows Code | Explanation rows', async () => {
    const user = userEvent.setup();
    render(
      <DecodePanel
        product="METAR"
        segments={[
          {
            start: 0,
            end: 5,
            code: 'METAR',
            explanation: 'Report type',
          },
          {
            start: 6,
            end: 10,
            code: 'KJFK',
            explanation: 'ICAO station',
          },
        ]}
        residuals={[]}
      />,
    );

    expect(screen.queryByTestId('decode-segments')).not.toBeInTheDocument();
    await user.click(screen.getByRole('button', { name: /Decode/i }));
    expect(screen.getByText('Code')).toBeInTheDocument();
    expect(screen.getByText('Explanation')).toBeInTheDocument();
    expect(screen.getByText('METAR')).toBeInTheDocument();
    expect(screen.getByText('Report type')).toBeInTheDocument();
    expect(screen.getByText('KJFK')).toBeInTheDocument();
  });

  it('renders explicit residuals when undecoded spans exist', async () => {
    const user = userEvent.setup();
    render(
      <DecodePanel
        product="VAA"
        defaultOpen
        segments={[
          {
            start: 0,
            end: 2,
            code: 'VA',
            explanation: 'Volcanic ash advisory marker',
          },
        ]}
        residuals={[
          {
            start: 20,
            end: 40,
            text: 'KARYMSKY 1000-13',
          },
        ]}
      />,
    );

    expect(screen.getByTestId('decode-residuals')).toBeInTheDocument();
    expect(screen.getByText('KARYMSKY 1000-13')).toBeInTheDocument();
    await user.click(screen.getByRole('button', { name: /Decode/i }));
    expect(screen.queryByTestId('decode-residuals')).not.toBeInTheDocument();
  });
});

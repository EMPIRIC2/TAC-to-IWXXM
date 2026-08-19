/**
 * T2.6 — Decode panel Code | Explanation + residual display (UJ-015).
 */

import { describe, it, expect, vi } from 'vitest';
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

  // T3.1 / TC-F9-002 §4 — Plain language block (S013 / EV-009)
  it('renders Plain language block at the top when summary is provided', async () => {
    const user = userEvent.setup();
    const summary =
      'Report type (routine meteorological aerodrome report); station KJFK; from 180° at 4 kt.';
    render(
      <DecodePanel
        product="METAR"
        summary={summary}
        segments={[
          {
            start: 0,
            end: 5,
            code: 'METAR',
            explanation: 'Report type',
          },
        ]}
        residuals={[]}
      />,
    );

    await user.click(screen.getByRole('button', { name: /Decode/i }));
    const block = screen.getByTestId('decode-plain-language');
    expect(block).toBeInTheDocument();
    expect(block).toHaveTextContent(/Plain language/i);
    expect(block).toHaveTextContent(summary);
    // Block appears before the Code | Explanation header.
    const codeHeader = screen.getByText('Code');
    expect(
      block.compareDocumentPosition(codeHeader) & Node.DOCUMENT_POSITION_FOLLOWING,
    ).toBeTruthy();
  });

  it('updates Plain language text when summary prop changes', () => {
    const { rerender } = render(
      <DecodePanel
        product="METAR"
        defaultOpen
        summary="First summary about KJFK."
        segments={[]}
        residuals={[]}
      />,
    );
    expect(screen.getByTestId('decode-plain-language')).toHaveTextContent(
      'First summary about KJFK.',
    );
    rerender(
      <DecodePanel
        product="METAR"
        defaultOpen
        summary="Updated summary about KORD."
        segments={[]}
        residuals={[]}
      />,
    );
    expect(screen.getByTestId('decode-plain-language')).toHaveTextContent(
      'Updated summary about KORD.',
    );
  });

  it('shows AHL bulletin framing and per-report Code | Explanation rows (TC-EV061-1012-003)', () => {
    render(
      <DecodePanel
        product="METAR"
        defaultOpen
        summary="Bulletin SAUS31 KZNY 121200 (2 reports). Station KJFK. Station KLGA."
        segments={[
          {
            start: 0,
            end: 18,
            code: 'SAUS31 KZNY 121200',
            explanation:
              'WMO abbreviated heading — SAUS31 from KZNY at day-time 121200',
          },
          {
            start: 19,
            end: 24,
            code: 'METAR',
            explanation: 'Report type (routine meteorological aerodrome report)',
          },
          {
            start: 25,
            end: 29,
            code: 'KJFK',
            explanation: 'ICAO station location indicator (KJFK)',
          },
          {
            start: 71,
            end: 76,
            code: 'METAR',
            explanation: 'Report type (routine meteorological aerodrome report)',
          },
          {
            start: 77,
            end: 81,
            code: 'KLGA',
            explanation: 'ICAO station location indicator (KLGA)',
          },
        ]}
        residuals={[]}
      />,
    );
    expect(screen.getByTestId('decode-plain-language')).toHaveTextContent(
      /Bulletin SAUS31 KZNY 121200/,
    );
    expect(screen.getByTestId('decode-plain-language')).toHaveTextContent(/KJFK/);
    expect(screen.getByTestId('decode-plain-language')).toHaveTextContent(/KLGA/);
    expect(screen.getByText('SAUS31 KZNY 121200')).toBeInTheDocument();
    expect(screen.getByText(/abbreviated heading/i)).toBeInTheDocument();
    expect(screen.getByText('KJFK')).toBeInTheDocument();
    expect(screen.getByText('KLGA')).toBeInTheDocument();
  });

  it('hides Plain language block when summary is empty', () => {
    render(
      <DecodePanel
        product="METAR"
        defaultOpen
        summary=""
        segments={[]}
        residuals={[]}
      />,
    );
    expect(screen.queryByTestId('decode-plain-language')).not.toBeInTheDocument();
  });

  it('reports toggles and renders loading, errors, and an empty result independently', async () => {
    const user = userEvent.setup();
    const onOpenChange = vi.fn();
    const { rerender } = render(
      <DecodePanel
        segments={[]}
        residuals={[]}
        defaultOpen
        loading
        onOpenChange={onOpenChange}
      />,
    );

    expect(screen.getByRole('status')).toHaveTextContent('Decoding…');
    expect(screen.queryByText('No decode segments yet.')).not.toBeInTheDocument();
    await user.click(screen.getByRole('button', { name: 'Decode' }));
    expect(onOpenChange).toHaveBeenCalledWith(false);

    rerender(
      <DecodePanel
        segments={[]}
        residuals={[]}
        defaultOpen
        error="Decode service unavailable"
      />,
    );
    await user.click(screen.getByRole('button', { name: 'Decode' }));
    expect(screen.getByRole('alert')).toHaveTextContent('Decode service unavailable');

    rerender(<DecodePanel segments={[]} residuals={[]} defaultOpen />);
    expect(screen.getByText('No decode segments yet.')).toBeInTheDocument();
  });
});

/**
 * Live map mutation matrix: publish/clear station, layout span, assert no station finder.
 */
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { act, render, screen } from '@testing-library/react';
import { DecodeVisualsPage } from './DecodeVisualsPage';
import { publishDecodeVisuals } from '@/utils/decodeVisualsStore';

vi.mock('@/app/components/LiveWorldMap', () => ({
  LiveWorldMap: ({ focusStation }: { focusStation?: string }) => (
    <div data-testid="live-world-map" data-focus-station={focusStation ?? ''} />
  ),
}));

function expectNoStationFinder(): void {
  expect(screen.queryByTestId('decode-visuals-station')).not.toBeInTheDocument();
  expect(document.getElementById('decode-visuals-station-input')).toBeNull();
}

describe('map full page mutation matrix', () => {
  beforeEach(() => {
    publishDecodeVisuals({ station: '', segments: [] });
    window.localStorage.clear();
  });

  it('create+validation pass: publish complete station shows heading without finder', () => {
    render(<DecodeVisualsPage />);
    act(() => {
      publishDecodeVisuals({
        station: 'KJFK',
        segments: [{ code: '18010KT', explanation: 'wind' }],
      });
    });
    expectNoStationFinder();
    expect(screen.getByTestId('decode-visuals-heading')).toHaveTextContent('Kennedy');
    expect(screen.getByTestId('live-world-map')).toHaveAttribute(
      'data-focus-station',
      'KJFK',
    );
  });

  it('create+validation fail: incomplete station keeps empty state without finder', () => {
    render(<DecodeVisualsPage />);
    act(() => {
      publishDecodeVisuals({ station: 'KJ', segments: [] });
    });
    expectNoStationFinder();
    expect(screen.getByTestId('decode-visuals-empty')).toBeInTheDocument();
    expect(screen.queryByTestId('decode-visuals-heading')).not.toBeInTheDocument();
  });

  it('update+validation pass: replace station updates focus without finder', () => {
    publishDecodeVisuals({ station: 'KJFK', segments: [] });
    render(<DecodeVisualsPage />);
    act(() => {
      publishDecodeVisuals({
        station: 'EGLL',
        segments: [{ code: '27012KT', explanation: 'wind' }],
      });
    });
    expectNoStationFinder();
    expect(screen.getByTestId('decode-visuals-heading')).toHaveTextContent('Heathrow');
    expect(screen.getByTestId('live-world-map')).toHaveAttribute(
      'data-focus-station',
      'EGLL',
    );
  });

  it('update+validation fail: replace with incomplete station clears heading', () => {
    publishDecodeVisuals({ station: 'KJFK', segments: [] });
    render(<DecodeVisualsPage />);
    act(() => {
      publishDecodeVisuals({ station: 'AB', segments: [] });
    });
    expectNoStationFinder();
    expect(screen.getByTestId('decode-visuals-empty')).toBeInTheDocument();
    expect(screen.queryByTestId('decode-visuals-heading')).not.toBeInTheDocument();
  });

  it('delete+allowed: clear published station removes heading without finder', () => {
    publishDecodeVisuals({
      station: 'KJFK',
      segments: [{ code: '18010KT', explanation: 'wind' }],
    });
    render(<DecodeVisualsPage />);
    act(() => {
      publishDecodeVisuals({ station: '', segments: [] });
    });
    expectNoStationFinder();
    expect(screen.getByTestId('decode-visuals-empty')).toBeInTheDocument();
    expect(screen.queryByTestId('wind-cue')).not.toBeInTheDocument();
  });

  it('layout span mutation keeps station finder absent', () => {
    window.localStorage.setItem(
      'tac-to-iwxxm.live-convert.layout',
      JSON.stringify({
        density: 'detailed',
        wrapXml: true,
        paneWidths: [34, 27, 39],
        span: 'roomy',
      }),
    );
    const { unmount } = render(<DecodeVisualsPage />);
    expectNoStationFinder();
    expect(screen.getByTestId('decode-visuals-page')).toHaveClass('max-w-none');
    unmount();
    window.localStorage.setItem(
      'tac-to-iwxxm.live-convert.layout',
      JSON.stringify({
        density: 'detailed',
        wrapXml: true,
        paneWidths: [34, 27, 39],
        span: 'tight',
      }),
    );
    render(<DecodeVisualsPage />);
    expectNoStationFinder();
    expect(screen.getByTestId('decode-visuals-page')).toHaveClass('max-w-6xl');
  });
});

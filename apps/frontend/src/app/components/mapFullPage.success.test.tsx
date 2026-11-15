/**
 * Live map full-page success paths (map Send handoff + ambient station focus).
 */
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { DecodeVisualsPage } from './DecodeVisualsPage';
import { publishDecodeVisuals } from '@/utils/decodeVisualsStore';

vi.mock('@/app/components/LiveWorldMap', () => ({
  LiveWorldMap: ({
    focusStation,
    onOpenPlace,
  }: {
    focusStation?: string;
    onOpenPlace?: (place: {
      place_key: string;
      product: string;
      latitude: number;
      longitude: number;
      reports: { tac: string; observed_at: string | null }[];
    }) => void;
  }) => (
    <div data-testid="live-world-map" data-focus-station={focusStation ?? ''}>
      <button
        type="button"
        data-testid="mock-send-place"
        onClick={() =>
          onOpenPlace?.({
            place_key: 'KJFK',
            product: 'metar',
            latitude: 40.6,
            longitude: -73.8,
            reports: [
              {
                tac: 'METAR KJFK 121251Z 18010KT 10SM FEW250 22/12 A3012',
                observed_at: '2026-11-12T12:51:00Z',
              },
            ],
          })
        }
      >
        Send
      </button>
    </div>
  ),
}));

function expectNoStationFinder(): void {
  expect(screen.queryByTestId('decode-visuals-station')).not.toBeInTheDocument();
  expect(document.getElementById('decode-visuals-station-input')).toBeNull();
}

describe('map full page success', () => {
  beforeEach(() => {
    publishDecodeVisuals({ station: '', segments: [] });
  });

  it('calls onOpenPlace with the TAC report when Send is clicked', async () => {
    const onOpenPlace = vi.fn();
    const user = userEvent.setup();
    render(<DecodeVisualsPage onOpenPlace={onOpenPlace} />);
    expectNoStationFinder();

    await user.click(screen.getByTestId('mock-send-place'));

    expect(onOpenPlace).toHaveBeenCalledTimes(1);
    expect(onOpenPlace).toHaveBeenCalledWith(
      expect.objectContaining({
        place_key: 'KJFK',
        product: 'metar',
        reports: [
          expect.objectContaining({
            tac: 'METAR KJFK 121251Z 18010KT 10SM FEW250 22/12 A3012',
          }),
        ],
      }),
    );
  });

  it('shows the station heading and passes focusStation from published Convert station', () => {
    publishDecodeVisuals({
      station: 'KJFK',
      segments: [{ code: '18010KT', explanation: 'wind' }],
    });
    render(<DecodeVisualsPage />);
    expectNoStationFinder();

    expect(screen.getByTestId('decode-visuals-heading')).toHaveTextContent('Kennedy');
    expect(screen.getByTestId('live-world-map')).toHaveAttribute(
      'data-focus-station',
      'KJFK',
    );
    publishDecodeVisuals({ station: '', segments: [] });
  });
});

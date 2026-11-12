/**
 * Decode visuals full-page failure paths (Send without handler, empty TAC forward, map error chrome).
 *
 * Empty/whitespace TAC guard lives in App.handleMapOpenPlace — DecodeVisualsPage always
 * forwards the place; App ignores empty TAC. This file asserts page forwarding only.
 */
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { DecodeVisualsPage } from './DecodeVisualsPage';
import { publishDecodeVisuals, writeStationDraft } from '@/utils/decodeVisualsStore';
import { DECODE_VISUALS_TITLE } from '@/utils/decodeVisualsCopy';
import type { LivePlace } from '@/utils/liveMap';

const emptyReportsPlace: LivePlace = {
  place_key: 'KJFK',
  product: 'metar',
  latitude: 40.6,
  longitude: -73.8,
  reports: [],
};

vi.mock('@/app/components/LiveWorldMap', () => ({
  LiveWorldMap: ({ onOpenPlace }: { onOpenPlace?: (place: LivePlace) => void }) => (
    <div data-testid="live-world-map">
      <p data-testid="live-map-error">Map cache unavailable</p>
      <button
        type="button"
        data-testid="mock-send-place"
        onClick={() => onOpenPlace?.(emptyReportsPlace)}
      >
        Send
      </button>
      <button
        type="button"
        data-testid="mock-send-whitespace-tac"
        onClick={() =>
          onOpenPlace?.({
            ...emptyReportsPlace,
            reports: [{ tac: '   ', observed_at: '' }],
          })
        }
      >
        Send whitespace TAC
      </button>
    </div>
  ),
}));

describe('mapFullPage failure paths', () => {
  beforeEach(() => {
    writeStationDraft(null);
    publishDecodeVisuals({ station: '', segments: [] });
  });

  it('does not throw when Send is clicked and onOpenPlace is omitted', async () => {
    const user = userEvent.setup();
    render(<DecodeVisualsPage />);
    await expect(
      user.click(screen.getByTestId('mock-send-place')),
    ).resolves.toBeUndefined();
  });

  it('forwards empty reports and whitespace TAC to onOpenPlace (App ignores empty TAC)', async () => {
    const user = userEvent.setup();
    const onOpenPlace = vi.fn();
    render(<DecodeVisualsPage onOpenPlace={onOpenPlace} />);

    await user.click(screen.getByTestId('mock-send-place'));
    expect(onOpenPlace).toHaveBeenCalledWith(emptyReportsPlace);

    await user.click(screen.getByTestId('mock-send-whitespace-tac'));
    expect(onOpenPlace).toHaveBeenCalledWith({
      ...emptyReportsPlace,
      reports: [{ tac: '   ', observed_at: null }],
    });
    expect(onOpenPlace).toHaveBeenCalledTimes(2);
  });

  it('still renders page chrome when the map mock shows an error child', () => {
    // Real LiveWorldMap fetch errors are covered in LiveWorldMap.test.tsx.
    render(<DecodeVisualsPage />);
    expect(screen.getByTestId('decode-visuals-page')).toBeInTheDocument();
    expect(
      screen.getByRole('heading', { name: DECODE_VISUALS_TITLE }),
    ).toBeInTheDocument();
    expect(screen.getByTestId('live-map-error')).toHaveTextContent(
      'Map cache unavailable',
    );
  });
});

/**
 * Live map station input guard rails (full-page map).
 *
 * Incomplete codes must not open the heading / WindCue path. Complete codes
 * matching STATION_ID (/^[A-Z][A-Z0-9]{3}$/) still take that path even when
 * the station is unknown — heading falls back to the typed code.
 */
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { DecodeVisualsPage } from './DecodeVisualsPage';

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
      <button
        type="button"
        data-testid="mock-send-empty-reports"
        onClick={() =>
          onOpenPlace?.({
            place_key: 'BLANK',
            product: 'metar',
            latitude: 0,
            longitude: 0,
            reports: [],
          })
        }
      >
        Send empty
      </button>
      <button
        type="button"
        data-testid="mock-send-blank-tac"
        onClick={() =>
          onOpenPlace?.({
            place_key: 'EMPTY',
            product: 'metar',
            latitude: 0,
            longitude: 0,
            reports: [{ tac: '   ', observed_at: null }],
          })
        }
      >
        Send blank TAC
      </button>
    </div>
  ),
}));

import { publishDecodeVisuals, writeStationDraft } from '@/utils/decodeVisualsStore';

/** Mirror App handleMapOpenPlace: empty / whitespace TAC is a no-op. */
function openPlaceGuard(
  onAccepted: (tac: string) => void,
): (place: { reports: { tac: string; observed_at: string | null }[] }) => void {
  return (place) => {
    const tac = place.reports[0]?.tac?.trim() ?? '';
    if (!tac) {
      return;
    }
    onAccepted(tac);
  };
}

describe('DecodeVisualsPage station validation', () => {
  beforeEach(() => {
    writeStationDraft(null);
    publishDecodeVisuals({ station: '', segments: [] });
  });

  it('shows decode-visuals-empty when the station field is empty', () => {
    render(<DecodeVisualsPage />);
    expect(screen.getByTestId('decode-visuals-empty')).toBeInTheDocument();
    expect(screen.queryByTestId('decode-visuals-heading')).not.toBeInTheDocument();
    expect(screen.queryByTestId('wind-cue')).not.toBeInTheDocument();
    expect(screen.getByTestId('live-world-map')).toHaveAttribute(
      'data-focus-station',
      '',
    );
  });

  it('does not show heading or WindCue for an incomplete ICAO (KJ)', async () => {
    const user = userEvent.setup();
    render(<DecodeVisualsPage />);
    await user.type(screen.getByTestId('decode-visuals-station'), 'KJ');
    expect(screen.getByTestId('decode-visuals-station')).toHaveValue('KJ');
    expect(screen.queryByTestId('decode-visuals-heading')).not.toBeInTheDocument();
    expect(screen.queryByTestId('wind-cue')).not.toBeInTheDocument();
    expect(screen.getByTestId('live-world-map')).toHaveAttribute(
      'data-focus-station',
      '',
    );
  });

  it('shows heading path for invalid/unknown complete codes (STATION_ID match)', async () => {
    // Unknown but complete: /^[A-Z][A-Z0-9]{3}$/ — DecodeVisualsPage still renders
    // decode-visuals-heading (display name falls back to the code) and WindCue.
    const user = userEvent.setup();
    render(<DecodeVisualsPage />);
    await user.type(screen.getByTestId('decode-visuals-station'), 'QXZX');
    expect(screen.getByTestId('decode-visuals-heading')).toHaveTextContent('QXZX');
    expect(screen.getByTestId('wind-cue')).toBeInTheDocument();
    expect(screen.getByTestId('live-world-map')).toHaveAttribute(
      'data-focus-station',
      'QXZX',
    );
  });

  it('no-ops Send when the place has empty TAC reports', async () => {
    const user = userEvent.setup();
    const accepted = vi.fn();
    render(<DecodeVisualsPage onOpenPlace={openPlaceGuard(accepted)} />);
    await user.click(screen.getByTestId('mock-send-empty-reports'));
    expect(accepted).not.toHaveBeenCalled();
    await user.click(screen.getByTestId('mock-send-blank-tac'));
    expect(accepted).not.toHaveBeenCalled();
    await user.click(screen.getByTestId('mock-send-place'));
    expect(accepted).toHaveBeenCalledTimes(1);
    expect(accepted).toHaveBeenCalledWith(
      'METAR KJFK 121251Z 18010KT 10SM FEW250 22/12 A3012',
    );
  });
});

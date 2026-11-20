/**
 * Live map page, region sketch, and wind cue.
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
    </div>
  ),
}));
import { RegionSchematic } from './RegionSchematic';
import { WindCue } from './WindCue';
import { publishDecodeVisuals } from '@/utils/decodeVisualsStore';

function expectNoStationFinder(): void {
  expect(screen.queryByTestId('decode-visuals-station')).not.toBeInTheDocument();
  expect(document.getElementById('decode-visuals-station-input')).toBeNull();
}

describe('RegionSchematic', () => {
  it('names the region and the station, or says the sketch is unavailable', () => {
    render(<RegionSchematic icao="KJFK" showStationName />);
    expect(screen.getByTestId('region-schematic-text')).toHaveTextContent(
      'United States',
    );
    expect(screen.getByTestId('region-schematic-text')).toHaveTextContent('Kennedy');
    expect(screen.getByTestId('region-schematic-svg')).toBeInTheDocument();
    render(<RegionSchematic icao="KJFK" />);
    expect(screen.getAllByTestId('region-schematic-text')[1]).toHaveTextContent(
      'Region sketch: United States.',
    );
    expect(screen.getAllByTestId('region-schematic-text')[1]).not.toHaveTextContent(
      'Kennedy',
    );
    render(<RegionSchematic icao="QQQQ" />);
    expect(screen.getByText('No region sketch for this station.')).toBeInTheDocument();
  });
});

describe('WindCue', () => {
  it('draws an arrow for a direction and a sentence when wind is absent', () => {
    render(<WindCue segments={[{ code: '18010KT', explanation: 'wind' }]} />);
    expect(screen.getByTestId('wind-cue-arrow')).toBeInTheDocument();
    expect(screen.getByTestId('wind-cue')).toHaveTextContent('Wind from 180 degrees');
    render(<WindCue segments={[]} />);
    expect(screen.getByText('No wind group in this decode.')).toBeInTheDocument();
  });
});

describe('DecodeVisualsPage', () => {
  beforeEach(() => {
    publishDecodeVisuals({ station: '', segments: [] });
  });

  it('renders the map without a station finder when Convert has no station', () => {
    render(<DecodeVisualsPage />);
    expectNoStationFinder();
    expect(screen.getByTestId('decode-visuals-empty')).toBeInTheDocument();
    expect(screen.getByTestId('live-world-map')).toBeInTheDocument();
    expect(screen.queryByTestId('decode-visuals-heading')).not.toBeInTheDocument();
  });

  it('uses the published Convert station for heading, wind, and map focus', () => {
    publishDecodeVisuals({
      station: 'EGLL',
      segments: [{ code: '27012KT', explanation: 'wind' }],
    });
    render(<DecodeVisualsPage />);
    expectNoStationFinder();
    expect(screen.queryByTestId('decode-visuals-empty')).not.toBeInTheDocument();
    expect(screen.getByTestId('decode-visuals-heading')).toHaveTextContent('Heathrow');
    expect(screen.getByTestId('wind-cue')).toHaveTextContent('Wind from 270 degrees');
    expect(screen.getByTestId('live-world-map')).toHaveAttribute(
      'data-focus-station',
      'EGLL',
    );
    publishDecodeVisuals({ station: '', segments: [] });
  });

  it('clears heading when Convert publishes an incomplete station', () => {
    publishDecodeVisuals({
      station: 'KJFK',
      segments: [{ code: '18010KT', explanation: 'wind' }],
    });
    const { rerender } = render(<DecodeVisualsPage />);
    expect(screen.getByTestId('decode-visuals-heading')).toBeInTheDocument();
    publishDecodeVisuals({
      station: 'T',
      segments: [{ code: '18010KT', explanation: 'wind' }],
    });
    rerender(<DecodeVisualsPage />);
    expectNoStationFinder();
    expect(screen.getByTestId('decode-visuals-empty')).toBeInTheDocument();
    expect(screen.queryByTestId('decode-visuals-heading')).not.toBeInTheDocument();
    expect(screen.queryByTestId('wind-cue')).not.toBeInTheDocument();
    publishDecodeVisuals({ station: '', segments: [] });
  });

  it('sends a map place to Convert when Send is used', async () => {
    const user = userEvent.setup();
    const onOpenPlace = vi.fn();
    render(<DecodeVisualsPage onOpenPlace={onOpenPlace} />);
    expectNoStationFinder();
    await user.click(screen.getByTestId('mock-send-place'));
    expect(onOpenPlace).toHaveBeenCalledWith(
      expect.objectContaining({
        place_key: 'KJFK',
        reports: [
          expect.objectContaining({
            tac: expect.stringContaining('METAR KJFK'),
          }),
        ],
      }),
    );
  });

  it('uses the tight column when Convert is set to tighter', () => {
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
    window.localStorage.clear();
  });
});

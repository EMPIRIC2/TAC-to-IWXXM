/**
 * Decode visuals tab, region sketch, and wind cue.
 */
import { describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { DecodeVisualsPage } from './DecodeVisualsPage';

vi.mock('@/app/components/StationMinimap', () => ({
  StationMinimap: ({ icao }: { icao: string }) => (
    <div data-testid="station-map">{icao}</div>
  ),
}));
import { RegionSchematic } from './RegionSchematic';
import { WindCue } from './WindCue';
import { publishDecodeVisuals } from '@/utils/decodeVisualsStore';

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
  it('starts empty, then shows a typed station without the published wind', async () => {
    publishDecodeVisuals({ station: '', segments: [] });
    const user = userEvent.setup();
    render(<DecodeVisualsPage />);
    expect(screen.getByTestId('decode-visuals-empty')).toBeInTheDocument();
    await user.type(screen.getByTestId('decode-visuals-station'), 'KJFK');
    expect(screen.getByTestId('decode-visuals-heading')).toHaveTextContent('Kennedy');
    expect(screen.getByTestId('station-map')).toHaveTextContent('KJFK');
    expect(screen.getByTestId('wind-cue')).toHaveTextContent('No wind group');
    await user.clear(screen.getByTestId('decode-visuals-station'));
    expect(screen.getByTestId('decode-visuals-station')).toHaveValue('');
    expect(screen.getByTestId('decode-visuals-empty')).toBeInTheDocument();
  });

  it('suggests stations that start with the typed letters', async () => {
    publishDecodeVisuals({ station: '', segments: [] });
    const user = userEvent.setup();
    render(<DecodeVisualsPage />);
    await user.type(screen.getByTestId('decode-visuals-station'), 'KJ');
    expect(screen.getByTestId('icao-suggestion-KJFK')).toHaveTextContent('Kennedy');
    await user.click(screen.getByTestId('icao-suggestion-KJFK'));
    expect(screen.getByTestId('decode-visuals-station')).toHaveValue('KJFK');
    expect(screen.getByTestId('decode-visuals-heading')).toHaveTextContent('Kennedy');
    publishDecodeVisuals({ station: '', segments: [] });
  });

  it('lets the operator clear a published station down to an empty field', async () => {
    publishDecodeVisuals({
      station: 'T',
      segments: [{ code: '18010KT', explanation: 'wind' }],
    });
    const user = userEvent.setup();
    render(<DecodeVisualsPage />);
    const input = screen.getByLabelText('Station ID');
    expect(input).toHaveValue('T');
    await user.clear(input);
    expect(input).toHaveValue('');
    expect(screen.getByTestId('decode-visuals-empty')).toBeInTheDocument();
    publishDecodeVisuals({ station: '', segments: [] });
  });

  it('uses the published station and its wind until the operator types', () => {
    publishDecodeVisuals({
      station: 'EGLL',
      segments: [{ code: '27012KT', explanation: 'wind' }],
    });
    render(<DecodeVisualsPage />);
    expect(screen.getByTestId('decode-visuals-station')).toHaveValue('EGLL');
    expect(screen.getByTestId('wind-cue')).toHaveTextContent('Wind from 270 degrees');
    publishDecodeVisuals({ station: '', segments: [] });
  });
});

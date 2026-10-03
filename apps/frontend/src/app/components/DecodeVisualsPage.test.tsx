/**
 * Decode visuals tab, region sketch, and wind cue.
 */
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { DecodeVisualsPage } from './DecodeVisualsPage';

vi.mock('@/app/components/LiveWorldMap', () => ({
  LiveWorldMap: () => <div data-testid="live-world-map" />,
}));
import { RegionSchematic } from './RegionSchematic';
import { WindCue } from './WindCue';
import { publishDecodeVisuals, writeStationDraft } from '@/utils/decodeVisualsStore';

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
    writeStationDraft(null);
  });

  it('starts empty, then shows a typed station without the published wind', async () => {
    publishDecodeVisuals({ station: '', segments: [] });
    const user = userEvent.setup();
    render(<DecodeVisualsPage />);
    expect(screen.getByTestId('decode-visuals-empty')).toBeInTheDocument();
    expect(screen.getByTestId('live-world-map')).toBeInTheDocument();
    await user.type(screen.getByTestId('decode-visuals-station'), 'KJFK');
    expect(screen.queryByTestId('icao-suggestion-KJFK')).not.toBeInTheDocument();
    expect(screen.getByTestId('decode-visuals-heading')).toHaveTextContent('Kennedy');
    expect(screen.getByTestId('live-world-map')).toBeInTheDocument();
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
    expect(screen.queryByTestId('icao-suggestion-KJFK')).not.toBeInTheDocument();
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

  it('keeps a typed station after leaving the tab', async () => {
    publishDecodeVisuals({ station: '', segments: [] });
    const user = userEvent.setup();
    const first = render(<DecodeVisualsPage />);
    await user.type(screen.getByTestId('decode-visuals-station'), 'KJFK');
    first.unmount();
    render(<DecodeVisualsPage />);
    expect(screen.getByTestId('decode-visuals-station')).toHaveValue('KJFK');
    expect(screen.getByTestId('decode-visuals-heading')).toHaveTextContent('Kennedy');
    writeStationDraft(null);
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
    publishDecodeVisuals({ station: '', segments: [] });
    render(<DecodeVisualsPage />);
    expect(screen.getByTestId('decode-visuals-page')).toHaveClass('max-w-6xl');
    window.localStorage.clear();
  });

  it('names the station status with the Station ID label', async () => {
    publishDecodeVisuals({ station: '', segments: [] });
    const user = userEvent.setup();
    render(<DecodeVisualsPage />);
    await user.type(screen.getByTestId('decode-visuals-station'), 'KJFK');
    expect(screen.getByLabelText('Valid Station ID')).toBeInTheDocument();
    expect(screen.queryByLabelText('Valid ICAO code')).not.toBeInTheDocument();
    await user.clear(screen.getByTestId('decode-visuals-station'));
    await user.type(screen.getByTestId('decode-visuals-station'), 'QXZX');
    expect(screen.getByLabelText('Invalid Station ID')).toBeInTheDocument();
    expect(screen.queryByLabelText('Invalid ICAO code')).not.toBeInTheDocument();
    writeStationDraft(null);
  });
});

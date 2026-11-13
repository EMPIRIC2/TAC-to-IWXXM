/**
 * Map-as-full-page regressions: shell Live map nav + DecodeVisualsPage map/search.
 *
 * [Corpus: ui-style] [Corpus: tests] [Corpus: product §F37]
 */

import { beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import { AppShellNav, SHELL_NAV_LABELS } from './AppShellNav';
import { DecodeVisualsPage } from './DecodeVisualsPage';
import { publishDecodeVisuals, writeStationDraft } from '@/utils/decodeVisualsStore';

vi.mock('@/app/components/LiveWorldMap', () => ({
  LiveWorldMap: ({ focusStation }: { focusStation?: string }) => (
    <div data-testid="live-world-map" data-focus-station={focusStation ?? ''} />
  ),
}));

describe('mapFullPage regression', () => {
  beforeEach(() => {
    writeStationDraft(null);
    publishDecodeVisuals({ station: '', segments: [] });
  });

  it('AppShellNav exposes shell-nav-visuals with Live map label', () => {
    render(<AppShellNav activeView="converter" onNavigate={() => undefined} />);

    expect(screen.getByTestId('shell-nav-visuals')).toHaveTextContent(
      SHELL_NAV_LABELS.visuals,
    );
    expect(screen.getByTestId('shell-nav-visuals')).toHaveTextContent('Live map');
    expect(screen.getByTestId('shell-nav-visuals')).not.toHaveTextContent(
      'Decode visuals',
    );
  });

  it('DecodeVisualsPage renders live-world-map and station search', () => {
    render(<DecodeVisualsPage />);

    expect(screen.getByTestId('live-world-map')).toBeInTheDocument();
    expect(screen.getByTestId('decode-visuals-station')).toBeInTheDocument();
    expect(screen.getByLabelText('Search')).toBeInTheDocument();
  });

  it('passes focusStation to LiveWorldMap when ICAO is complete', async () => {
    const user = userEvent.setup();
    render(<DecodeVisualsPage />);

    expect(screen.getByTestId('live-world-map')).toHaveAttribute(
      'data-focus-station',
      '',
    );

    await user.type(screen.getByTestId('decode-visuals-station'), 'KJ');
    expect(screen.getByTestId('live-world-map')).toHaveAttribute(
      'data-focus-station',
      '',
    );

    await user.type(screen.getByTestId('decode-visuals-station'), 'FK');
    expect(screen.getByTestId('live-world-map')).toHaveAttribute(
      'data-focus-station',
      'KJFK',
    );

    writeStationDraft(null);
  });
});

/**
 * Map-as-full-page regressions: shell Live map nav + DecodeVisualsPage map.
 *
 * [Corpus: ui-style] [Corpus: tests] [Corpus: product §F37]
 */

import { beforeEach, describe, expect, it, vi } from 'vitest';
import { act, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import { AppShellNav, SHELL_NAV_LABELS } from './AppShellNav';
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

describe('mapFullPage regression', () => {
  beforeEach(() => {
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

  it('DecodeVisualsPage renders live-world-map and omits station search', () => {
    render(<DecodeVisualsPage />);

    expect(screen.getByTestId('live-world-map')).toBeInTheDocument();
    expectNoStationFinder();
    expect(screen.queryByLabelText('Search')).not.toBeInTheDocument();
    expect(screen.queryByPlaceholderText('Find a station')).not.toBeInTheDocument();
  });

  it('passes focusStation from published station and updates after publish mutation', () => {
    render(<DecodeVisualsPage />);
    expectNoStationFinder();
    expect(screen.getByTestId('live-world-map')).toHaveAttribute(
      'data-focus-station',
      '',
    );

    act(() => {
      publishDecodeVisuals({ station: 'KJ', segments: [] });
    });
    expect(screen.getByTestId('live-world-map')).toHaveAttribute(
      'data-focus-station',
      '',
    );

    act(() => {
      publishDecodeVisuals({ station: 'KJFK', segments: [] });
    });
    expect(screen.getByTestId('live-world-map')).toHaveAttribute(
      'data-focus-station',
      'KJFK',
    );
    expectNoStationFinder();

    publishDecodeVisuals({ station: '', segments: [] });
  });

  it('keeps station finder absent after shell nav mutation to Live map', async () => {
    const user = userEvent.setup();
    const onNavigate = vi.fn();
    render(
      <>
        <AppShellNav activeView="converter" onNavigate={onNavigate} />
        <DecodeVisualsPage />
      </>,
    );
    await user.click(screen.getByTestId('shell-nav-visuals'));
    expect(onNavigate).toHaveBeenCalledWith('visuals');
    expectNoStationFinder();
  });
});

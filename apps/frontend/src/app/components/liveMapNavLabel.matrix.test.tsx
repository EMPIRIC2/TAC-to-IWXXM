/**
 * Evolve-auto test matrix: shell Live map label (was Decode visuals).
 *
 * Covers success, failure chrome, validation empty/complete station, and
 * theme × selected mutations. Keeps data-testid="shell-nav-visuals".
 *
 * [Corpus: product §F37] [Corpus: ui-style] [Corpus: tests]
 */

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import { AppShellNav, SHELL_NAV_LABELS } from './AppShellNav';
import { DecodeVisualsPage } from './DecodeVisualsPage';
import { DECODE_VISUALS_OPEN, DECODE_VISUALS_TITLE } from '@/utils/decodeVisualsCopy';
import { publishDecodeVisuals, writeStationDraft } from '@/utils/decodeVisualsStore';

vi.mock('@/app/components/LiveWorldMap', () => ({
  LiveWorldMap: ({ focusStation }: { focusStation?: string }) => (
    <div data-testid="live-world-map" data-focus-station={focusStation ?? ''} />
  ),
}));

const OLD_LABEL = 'Decode visuals';
const NEW_LABEL = 'Live map';

function assertLiveMapLabel(el: HTMLElement): void {
  expect(el).toHaveTextContent(NEW_LABEL);
  expect(el.textContent ?? '').not.toContain(OLD_LABEL);
}

describe('Live map nav label matrix', () => {
  beforeEach(() => {
    writeStationDraft(null);
    publishDecodeVisuals({ station: '', segments: [] });
    document.documentElement.classList.remove('dark');
  });

  afterEach(() => {
    document.documentElement.classList.remove('dark');
  });

  describe('S — success paths', () => {
    it('shows Live map on shell-nav-visuals and selects the page', async () => {
      const user = userEvent.setup();
      const onNavigate = vi.fn();
      render(<AppShellNav activeView="converter" onNavigate={onNavigate} />);

      const tab = screen.getByTestId('shell-nav-visuals');
      assertLiveMapLabel(tab);
      expect(SHELL_NAV_LABELS.visuals).toBe(NEW_LABEL);
      expect(tab).toHaveAttribute('aria-selected', 'false');

      await user.click(tab);
      expect(onNavigate).toHaveBeenCalledWith('visuals');
    });

    it('page heading uses Live map when the visuals view is active', () => {
      render(
        <>
          <AppShellNav activeView="visuals" onNavigate={() => undefined} />
          <DecodeVisualsPage />
        </>,
      );
      assertLiveMapLabel(screen.getByTestId('shell-nav-visuals'));
      expect(screen.getByTestId('shell-nav-visuals')).toHaveAttribute(
        'aria-selected',
        'true',
      );
      expect(
        screen.getByRole('heading', { name: DECODE_VISUALS_TITLE }),
      ).toHaveTextContent(NEW_LABEL);
      expect(screen.getByTestId('decode-visuals-page')).toBeInTheDocument();
    });
  });

  describe('F — failure / empty chrome still shows Live map', () => {
    it('empty station state keeps Live map title and never Decode visuals', () => {
      render(<DecodeVisualsPage />);
      expect(
        screen.getByRole('heading', { name: DECODE_VISUALS_TITLE }),
      ).toHaveTextContent(NEW_LABEL);
      expect(screen.getByTestId('decode-visuals-empty')).toBeInTheDocument();
      expect(screen.queryByText(OLD_LABEL)).not.toBeInTheDocument();
    });

    it('page still labeled Live map when the map region is present without a station', () => {
      render(<DecodeVisualsPage />);
      expect(screen.getByTestId('decode-visuals-page')).toBeInTheDocument();
      expect(screen.getByTestId('live-world-map')).toBeInTheDocument();
      expect(screen.getByRole('heading', { name: NEW_LABEL })).toBeInTheDocument();
      expect(document.body.textContent ?? '').not.toContain(OLD_LABEL);
    });
  });

  describe('V — validation success and failure on page chrome', () => {
    it('V+: complete ICAO keeps Live map title while heading shows station', async () => {
      const user = userEvent.setup();
      render(<DecodeVisualsPage />);
      await user.type(screen.getByTestId('decode-visuals-station'), 'KJFK');
      expect(
        screen.getByRole('heading', { name: DECODE_VISUALS_TITLE }),
      ).toHaveTextContent(NEW_LABEL);
      expect(screen.getByTestId('decode-visuals-heading')).toBeInTheDocument();
      expect(screen.queryByText(OLD_LABEL)).not.toBeInTheDocument();
    });

    it('V−: incomplete ICAO keeps empty chrome and Live map title', async () => {
      const user = userEvent.setup();
      render(<DecodeVisualsPage />);
      await user.type(screen.getByTestId('decode-visuals-station'), 'KJ');
      expect(screen.getByTestId('decode-visuals-empty')).toBeInTheDocument();
      expect(
        screen.getByRole('heading', { name: DECODE_VISUALS_TITLE }),
      ).toHaveTextContent(NEW_LABEL);
      expect(screen.queryByText(OLD_LABEL)).not.toBeInTheDocument();
    });
  });

  describe('M — theme × selected mutations (label stable)', () => {
    const themes = ['light', 'dark'] as const;
    const selections = [
      { activeView: 'converter' as const, selected: false },
      { activeView: 'visuals' as const, selected: true },
    ];

    for (const theme of themes) {
      for (const { activeView, selected } of selections) {
        it(`${theme} × ${selected ? 'selected' : 'unselected'} shows Live map`, () => {
          if (theme === 'dark') {
            document.documentElement.classList.add('dark');
          } else {
            document.documentElement.classList.remove('dark');
          }
          render(<AppShellNav activeView={activeView} onNavigate={() => undefined} />);
          const tab = screen.getByTestId('shell-nav-visuals');
          assertLiveMapLabel(tab);
          expect(tab).toHaveAttribute('aria-selected', selected ? 'true' : 'false');
          expect(within(tab).queryByText(OLD_LABEL)).not.toBeInTheDocument();
        });
      }
    }
  });

  describe('Read / affordance copy', () => {
    it('Open Live map affordance string never says Decode visuals', () => {
      expect(DECODE_VISUALS_OPEN).toBe('Open Live map');
      expect(DECODE_VISUALS_OPEN).not.toContain(OLD_LABEL);
      expect(DECODE_VISUALS_TITLE).toBe(NEW_LABEL);
    });
  });
});

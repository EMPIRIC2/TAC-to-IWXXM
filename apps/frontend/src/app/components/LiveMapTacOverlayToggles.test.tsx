/**
 * TAC overlay toggle UI — independent layers + empty hint.
 */

import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import {
  defaultTacOverlayVisibility,
  toggleTacOverlay,
} from '@/utils/liveMapTacLayers';
import { LiveMapTacOverlayToggles } from './LiveMapTacOverlayToggles';

describe('LiveMapTacOverlayToggles', () => {
  it('toggles each overlay independently and shows empty hint when on with no data', async () => {
    const user = userEvent.setup();
    const onToggle = vi.fn();
    const { rerender } = render(
      <LiveMapTacOverlayToggles
        visibility={defaultTacOverlayVisibility()}
        onToggle={onToggle}
        places={[]}
      />,
    );
    expect(screen.getByTestId('live-map-tac-overlays')).toBeInTheDocument();
    expect(screen.queryByTestId('live-map-tac-overlay-empty')).not.toBeInTheDocument();
    await user.click(screen.getByTestId('tac-overlay-thunder'));
    expect(onToggle).toHaveBeenCalledWith('thunder');
    const thunderOn = toggleTacOverlay(defaultTacOverlayVisibility(), 'thunder');
    rerender(
      <LiveMapTacOverlayToggles
        visibility={thunderOn}
        onToggle={onToggle}
        places={[]}
      />,
    );
    expect(screen.getByTestId('live-map-tac-overlay-empty')).toBeInTheDocument();
    expect(screen.getByTestId('tac-overlay-thunder')).toBeChecked();
    expect(screen.getByTestId('tac-overlay-ice')).not.toBeChecked();
  });

  it('hides the empty hint when a place feeds the active overlay', () => {
    const thunderOn = toggleTacOverlay(defaultTacOverlayVisibility(), 'thunder');
    render(
      <LiveMapTacOverlayToggles
        visibility={thunderOn}
        onToggle={() => undefined}
        places={[
          {
            reports: [
              {
                tac: 'METAR KJFK 131200Z 18010KT TSRA',
              },
            ],
          },
        ]}
      />,
    );
    expect(screen.queryByTestId('live-map-tac-overlay-empty')).not.toBeInTheDocument();
  });
});

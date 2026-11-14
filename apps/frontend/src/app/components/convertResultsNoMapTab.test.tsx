/**
 * Results drawer must never expose a Map tab; Live map page keeps the map.
 *
 * Success / failure / validation / combinatorial coverage for the Results chrome.
 *
 * [Corpus: product §F7] [Corpus: product §F37] [Corpus: journeys §UJ-089] [Corpus: tests]
 */

import { describe, expect, it, vi } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import { ConvertResultsDrawer } from './ConvertResultsDrawer';
import { DecodeVisualsPage } from './DecodeVisualsPage';
import {
  CONVERT_RESULTS_TABS,
  type ConvertResultsTab,
} from '/utils/convertResultsDrawer';
import { publishDecodeVisuals } from '@/utils/decodeVisualsStore';

vi.mock('@/app/components/LiveWorldMap', () => ({
  LiveWorldMap: () => <div data-testid="live-world-map">map-page</div>,
}));

const bodies = {
  iwxxm: <div data-testid="body-iwxxm">iwxxm</div>,
  console: <div data-testid="body-console">console</div>,
  decoder: <div data-testid="body-decoder">decoder</div>,
  downloads: <div data-testid="body-downloads">downloads</div>,
};

const PRODUCTS = ['METAR', 'SPECI', 'TAF', 'SIGMET'] as const;
const TABS: ConvertResultsTab[] = ['iwxxm', 'console', 'decoder', 'downloads'];
const OPEN_STATES = [true, false] as const;

function assertNoMapInResults(root: HTMLElement = document.body): void {
  expect(within(root).queryByTestId('convert-results-tab-map')).not.toBeInTheDocument();
  expect(within(root).queryByRole('tab', { name: 'Map' })).not.toBeInTheDocument();
  expect(
    within(root).queryByTestId('convert-results-panel-map'),
  ).not.toBeInTheDocument();
  expect(within(root).queryByTestId('convert-weather-map')).not.toBeInTheDocument();
  expect(
    within(root).queryByTestId('convert-open-decode-visuals'),
  ).not.toBeInTheDocument();
}

describe('Results drawer without Map tab', () => {
  it('success: open drawer shows four tabs and never Map', async () => {
    const user = userEvent.setup();
    const onTabChange = vi.fn();
    render(
      <ConvertResultsDrawer
        open
        onOpenChange={() => undefined}
        tab="iwxxm"
        onTabChange={onTabChange}
        height={320}
        onHeightChange={() => undefined}
        {...bodies}
      />,
    );

    expect(screen.getByTestId('convert-results-drawer-chrome')).toBeInTheDocument();
    expect(CONVERT_RESULTS_TABS).toHaveLength(4);
    for (const id of TABS) {
      expect(screen.getByTestId(`convert-results-tab-${id}`)).toBeInTheDocument();
    }
    assertNoMapInResults();

    await user.click(screen.getByTestId('convert-results-tab-console'));
    expect(onTabChange).toHaveBeenCalledWith('console');
    await user.click(screen.getByTestId('convert-results-tab-decoder'));
    expect(onTabChange).toHaveBeenCalledWith('decoder');
    await user.click(screen.getByTestId('convert-results-tab-downloads'));
    expect(onTabChange).toHaveBeenCalledWith('downloads');
    assertNoMapInResults();
  });

  it('success: Live map page still renders the map', () => {
    publishDecodeVisuals({ station: 'KJFK', segments: [] });
    render(<DecodeVisualsPage />);
    expect(screen.getByTestId('decode-visuals-page')).toBeInTheDocument();
    expect(screen.getByTestId('live-world-map')).toBeInTheDocument();
  });

  it('failure: empty / missing result bodies still omit Map from chrome', () => {
    render(
      <ConvertResultsDrawer
        open
        onOpenChange={() => undefined}
        tab="iwxxm"
        onTabChange={() => undefined}
        height={240}
        onHeightChange={() => undefined}
        iwxxm={<p data-testid="empty-iwxxm">No IWXXM yet.</p>}
        console={<p data-testid="empty-console">No convert log.</p>}
        decoder={<p data-testid="empty-decoder">No decode.</p>}
        downloads={<p data-testid="empty-downloads">No files.</p>}
      />,
    );
    expect(screen.getByTestId('empty-iwxxm')).toBeInTheDocument();
    assertNoMapInResults();
  });

  it('failure: API-error style console copy still has no Map tab', () => {
    render(
      <ConvertResultsDrawer
        open
        onOpenChange={() => undefined}
        tab="console"
        onTabChange={() => undefined}
        height={240}
        onHeightChange={() => undefined}
        iwxxm={<div />}
        console={<pre data-testid="api-error-console">Convert failed: 502</pre>}
        decoder={<div />}
        downloads={<div />}
      />,
    );
    expect(screen.getByTestId('api-error-console')).toBeVisible();
    assertNoMapInResults();
  });

  it('validation: soft-fail and terminator-style cues never add a Map tab', () => {
    render(
      <ConvertResultsDrawer
        open
        onOpenChange={() => undefined}
        tab="iwxxm"
        onTabChange={() => undefined}
        height={240}
        onHeightChange={() => undefined}
        iwxxm={
          <div>
            <div data-testid="soft-fail-banner">Soft preview incomplete</div>
            <div data-testid="terminator-cue">Missing report terminator</div>
          </div>
        }
        console={<div data-testid="lint-error-console">TAC lint errors present</div>}
        decoder={<div data-testid="invalid-tac-decode">Could not decode TAC</div>}
        downloads={<div />}
      />,
    );
    expect(screen.getByTestId('soft-fail-banner')).toBeInTheDocument();
    expect(screen.getByTestId('terminator-cue')).toBeInTheDocument();
    expect(screen.getByTestId('lint-error-console')).toBeInTheDocument();
    expect(screen.getByTestId('invalid-tac-decode')).toBeInTheDocument();
    assertNoMapInResults();
  });

  it('mutation: product × tab × open/closed permutations never show Map in Results', () => {
    for (const product of PRODUCTS) {
      for (const tab of TABS) {
        for (const open of OPEN_STATES) {
          const { unmount } = render(
            <div data-testid={`combo-${product}-${tab}-${open}`}>
              <span data-testid="product-label">{product}</span>
              <ConvertResultsDrawer
                open={open}
                onOpenChange={() => undefined}
                tab={tab}
                onTabChange={() => undefined}
                height={200}
                onHeightChange={() => undefined}
                {...bodies}
              />
            </div>,
          );
          expect(
            screen.getByTestId('convert-results-drawer-chrome'),
          ).toBeInTheDocument();
          assertNoMapInResults(screen.getByTestId(`combo-${product}-${tab}-${open}`));
          if (open) {
            expect(
              screen.getByTestId(`convert-results-tab-${tab}`),
            ).toBeInTheDocument();
          }
          unmount();
        }
      }
    }
  });

  it('mutation: with and without decode/map companion pages, Results still omits Map', () => {
    publishDecodeVisuals({ station: '', segments: [] });
    const { unmount } = render(
      <>
        <ConvertResultsDrawer
          open
          onOpenChange={() => undefined}
          tab="decoder"
          onTabChange={() => undefined}
          height={280}
          onHeightChange={() => undefined}
          {...bodies}
        />
        <DecodeVisualsPage />
      </>,
    );
    assertNoMapInResults(screen.getByTestId('convert-results-drawer'));
    expect(screen.getByTestId('live-world-map')).toBeInTheDocument();
    expect(screen.getByTestId('decode-visuals-page')).toBeInTheDocument();
    unmount();
  });
});

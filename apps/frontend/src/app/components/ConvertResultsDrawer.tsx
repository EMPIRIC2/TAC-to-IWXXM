/**
 * Bottom Convert results drawer — one tab panel visible at a time (UJ-089).
 *
 * Map is on the Live map page only (not a Results tab).
 *
 * [Corpus: product §F7] [Corpus: product §F37] [Corpus: journeys §UJ-089]
 */

import type { ReactNode } from 'react';

import {
  CONVERT_RESULTS_TABS,
  type ConvertResultsTab,
} from '/utils/convertResultsDrawer';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Button } from './ui/button';
import { VerticalResizeHandle } from './VerticalResizeHandle';

/**
 * Props for {@link ConvertResultsDrawer}.
 * @example
 * const _ = true;
 */
export interface ConvertResultsDrawerProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  tab: ConvertResultsTab;
  onTabChange: (tab: ConvertResultsTab) => void;
  /** Open body height in pixels (drag-resized like Convert panes). */
  height: number;
  onHeightChange: (height: number) => void;
  iwxxm: ReactNode;
  console: ReactNode;
  decoder: ReactNode;
  downloads: ReactNode;
}

const PANEL: Record<ConvertResultsTab, 'iwxxm' | 'console' | 'decoder' | 'downloads'> =
  {
    iwxxm: 'iwxxm',
    console: 'console',
    decoder: 'decoder',
    downloads: 'downloads',
  };

/**
 * Collapsible results host with IWXXM / Console / Decoder / Downloads tabs.
 *
 * Title + Hide and the tab strip stay outside the scrolling tab body so chrome
 * remains visible while panel content scrolls.
 *
 * @param props - Open state, active tab, height, and tab bodies
 * @returns Drawer chrome for Convert secondary surfaces
 * @example
 * const _ = true;
 */
export function ConvertResultsDrawer({
  open,
  onOpenChange,
  tab,
  onTabChange,
  height,
  onHeightChange,
  iwxxm,
  console: consolePanel,
  decoder,
  downloads,
}: ConvertResultsDrawerProps) {
  const bodies: Record<ConvertResultsTab, ReactNode> = {
    iwxxm,
    console: consolePanel,
    decoder,
    downloads,
  };

  return (
    <section
      className="mt-4 rounded-lg border border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-900"
      data-testid="convert-results-drawer"
      data-open={open ? 'true' : 'false'}
      aria-label="Convert results"
    >
      <div
        className="flex items-center justify-between gap-2 border-b border-gray-200 px-3 py-2 dark:border-gray-700"
        data-testid="convert-results-drawer-chrome"
      >
        <h2 className="text-sm font-semibold text-gray-900 dark:text-white">Results</h2>
        <Button
          type="button"
          variant="ghost"
          size="sm"
          data-testid="convert-results-drawer-toggle"
          aria-expanded={open}
          onClick={() => onOpenChange(!open)}
        >
          {open ? 'Hide' : 'Show'}
        </Button>
      </div>
      <div
        className={`flex min-h-0 flex-col ${open ? '' : 'hidden'}`}
        style={open ? { height } : undefined}
        data-testid="convert-results-drawer-shell"
        hidden={!open}
      >
        <Tabs
          value={tab}
          onValueChange={(value) => onTabChange(value as ConvertResultsTab)}
          className="flex min-h-0 flex-1 flex-col gap-0"
          data-testid="convert-results-tabs"
          hidden={!open}
        >
          <div
            className="shrink-0 px-3 pt-3"
            data-testid="convert-results-drawer-tab-chrome"
          >
            <TabsList
              className="mb-3 flex h-auto w-full flex-wrap justify-start gap-1"
              aria-label="Results panels"
              data-testid="convert-results-tablist"
            >
              {CONVERT_RESULTS_TABS.map((entry) => (
                <TabsTrigger
                  key={entry.id}
                  value={entry.id}
                  data-testid={`convert-results-tab-${entry.id}`}
                >
                  {entry.label}
                </TabsTrigger>
              ))}
            </TabsList>
          </div>
          <div
            className="flex min-h-0 flex-1 flex-col overflow-auto px-3 pb-3"
            data-testid="convert-results-drawer-body"
          >
            {(Object.keys(PANEL) as ConvertResultsTab[]).map((id) => (
              <TabsContent
                key={id}
                value={id}
                forceMount
                hidden={tab !== id}
                data-testid={`convert-results-panel-${id}`}
                className={tab === id ? 'flex h-full min-h-0 flex-col' : 'hidden'}
              >
                {bodies[id]}
              </TabsContent>
            ))}
          </div>
        </Tabs>
      </div>
      {open ? (
        <VerticalResizeHandle
          height={height}
          onHeightChange={onHeightChange}
          label="Resize results drawer"
          testId="results-drawer-vertical-resize"
        />
      ) : null}
    </section>
  );
}

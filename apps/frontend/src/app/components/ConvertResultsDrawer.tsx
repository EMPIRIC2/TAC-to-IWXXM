/**
 * Bottom Convert results drawer — one tab panel visible at a time (UJ-089).
 *
 * [Corpus: product §F7] [Corpus: journeys §UJ-089]
 */

import type { ReactNode } from 'react';

import {
  CONVERT_RESULTS_TABS,
  type ConvertResultsTab,
} from '/utils/convertResultsDrawer';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Button } from './ui/button';

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
  iwxxm: ReactNode;
  console: ReactNode;
  decoder: ReactNode;
  map: ReactNode;
  downloads: ReactNode;
}

const PANEL: Record<
  ConvertResultsTab,
  'iwxxm' | 'console' | 'decoder' | 'map' | 'downloads'
> = {
  iwxxm: 'iwxxm',
  console: 'console',
  decoder: 'decoder',
  map: 'map',
  downloads: 'downloads',
};

/**
 * Collapsible results host with IWXXM / Console / Decoder / Map / Downloads tabs.
 *
 * @param props - Open state, active tab, and tab bodies
 * @returns Drawer chrome for Convert secondary surfaces
 * @example
 * const _ = true;
 */
export function ConvertResultsDrawer({
  open,
  onOpenChange,
  tab,
  onTabChange,
  iwxxm,
  console: consolePanel,
  decoder,
  map,
  downloads,
}: ConvertResultsDrawerProps) {
  const bodies: Record<ConvertResultsTab, ReactNode> = {
    iwxxm,
    console: consolePanel,
    decoder,
    map,
    downloads,
  };

  return (
    <section
      className="mt-4 rounded-lg border border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-900"
      data-testid="convert-results-drawer"
      data-open={open ? 'true' : 'false'}
      aria-label="Convert results"
    >
      <div className="flex items-center justify-between gap-2 border-b border-gray-200 px-3 py-2 dark:border-gray-700">
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
      <Tabs
        value={tab}
        onValueChange={(value) => onTabChange(value as ConvertResultsTab)}
        className={`gap-0 p-3 ${open ? '' : 'hidden'}`}
        data-testid="convert-results-tabs"
        hidden={!open}
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
        {(Object.keys(PANEL) as ConvertResultsTab[]).map((id) => (
          <TabsContent
            key={id}
            value={id}
            forceMount
            hidden={tab !== id}
            data-testid={`convert-results-panel-${id}`}
            className={tab === id ? undefined : 'hidden'}
          >
            {bodies[id]}
          </TabsContent>
        ))}
      </Tabs>
    </section>
  );
}

/**
 * Primary operator shell navigation — Convert, Live map, History, Rule catalogs, Code names, Glossary, Station health.
 *
 * Peer tabs for the operator shell; not a FileConverter panel.
 */

import { DECODE_VISUALS_TITLE } from '@/utils/decodeVisualsCopy';
import { shellFrameClass, useLiveConvertLayout } from '@/utils/liveConvertLayout';

/**
 * Type `ShellPrimaryView`.
 * @example
 * const _ = true;
 */
export type ShellPrimaryView =
  | 'converter'
  | 'visuals'
  | 'history'
  | 'catalog'
  | 'dictionary'
  | 'glossary'
  | 'stations';

export const SHELL_NAV_LABELS = {
  converter: 'Convert',
  visuals: DECODE_VISUALS_TITLE,
  history: 'History',
  catalog: 'Rule catalogs',
  dictionary: 'Code names',
  glossary: 'Glossary',
  stations: 'Station health',
} as const;

interface AppShellNavProps {
  /** Active primary view. */
  activeView: ShellPrimaryView;
  /** Navigate to another primary shell view. */
  onNavigate: (view: ShellPrimaryView) => void;
}

const TABS: ShellPrimaryView[] = [
  'converter',
  'visuals',
  'history',
  'catalog',
  'dictionary',
  'glossary',
  'stations',
];

/**
 * Render Convert, Live map, History, Rule catalogs, Code names, Glossary, and Station health.
 *
 * @param props.activeView - Currently selected shell view
 * @param props.onNavigate - View change handler
 * @example
 * const _ = true;
 */
export function AppShellNav({ activeView, onNavigate }: AppShellNavProps) {
  const { layout } = useLiveConvertLayout();
  const frame = shellFrameClass(layout.span);
  return (
    <nav
      className="border-b border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-950"
      aria-label="Primary"
      data-testid="app-shell-nav"
    >
      <div className={`mx-auto flex w-full flex-wrap gap-1 px-4 py-2 ${frame}`}>
        {TABS.map((view) => {
          const selected = activeView === view;
          return (
            <button
              key={view}
              type="button"
              role="tab"
              aria-selected={selected}
              data-testid={`shell-nav-${view}`}
              className={
                selected
                  ? 'inline-flex items-center gap-1.5 rounded-md bg-gray-900 px-3 py-1.5 text-sm font-medium text-white dark:bg-gray-100 dark:text-gray-900'
                  : 'inline-flex items-center gap-1.5 rounded-md px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-800'
              }
              onClick={() => onNavigate(view)}
            >
              {SHELL_NAV_LABELS[view]}
            </button>
          );
        })}
      </div>
    </nav>
  );
}

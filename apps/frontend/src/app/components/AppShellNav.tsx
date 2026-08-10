/**
 * Primary operator shell navigation — Convert | History | Quality metrics.
 *
 * Peer tabs for F7 / F7.q (EV-054); not a FileConverter panel.
 */

export type ShellPrimaryView = 'converter' | 'history' | 'quality';

export const SHELL_NAV_LABELS = {
  converter: 'Convert',
  history: 'History',
  quality: 'Quality metrics',
} as const;

interface AppShellNavProps {
  /** Active primary view. */
  activeView: ShellPrimaryView;
  /** Navigate to another primary shell view. */
  onNavigate: (view: ShellPrimaryView) => void;
}

const TABS: ShellPrimaryView[] = ['converter', 'history', 'quality'];

/**
 * Render Convert / History / Quality metrics primary tabs.
 *
 * @param props.activeView - Currently selected shell view
 * @param props.onNavigate - View change handler
 */
export function AppShellNav({ activeView, onNavigate }: AppShellNavProps) {
  return (
    <nav
      className="border-b border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-950"
      aria-label="Primary"
      data-testid="app-shell-nav"
    >
      <div className="mx-auto flex max-w-6xl gap-1 px-4 py-2">
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
                  ? 'rounded-md bg-gray-900 px-3 py-1.5 text-sm font-medium text-white dark:bg-gray-100 dark:text-gray-900'
                  : 'rounded-md px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-800'
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

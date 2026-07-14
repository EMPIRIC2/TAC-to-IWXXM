/**
 * Pull-up structured console for the F7 live workbench (UJ-017 / #694).
 */

import { useState } from 'react';
import { ChevronDown, ChevronUp, Terminal } from 'lucide-react';
import type { LiveWorkbenchConsoleLine } from '@/hooks/useLiveWorkbenchAssist';

export interface WorkbenchConsoleProps {
  lines: LiveWorkbenchConsoleLine[];
  onClear?: () => void;
  defaultOpen?: boolean;
}

/**
 * Collapsible pull-up console for live-assist messages.
 *
 * @param props.lines - Structured console entries
 */
export function WorkbenchConsole({
  lines,
  onClear,
  defaultOpen = false,
}: WorkbenchConsoleProps) {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <section
      className="mt-3 rounded-md border border-gray-300 bg-gray-50 dark:border-gray-700 dark:bg-gray-900/60"
      aria-label="Workbench console"
      data-testid="workbench-console"
    >
      <div className="flex items-center gap-2 px-3 py-2">
        <button
          type="button"
          className="flex flex-1 items-center gap-2 text-left text-sm font-medium text-gray-900 dark:text-white"
          aria-expanded={open}
          onClick={() => setOpen((v) => !v)}
          data-testid="workbench-console-toggle"
        >
          {open ? (
            <ChevronDown className="h-4 w-4 shrink-0" aria-hidden />
          ) : (
            <ChevronUp className="h-4 w-4 shrink-0" aria-hidden />
          )}
          <Terminal className="h-4 w-4 shrink-0" aria-hidden />
          Console
          <span className="font-normal text-gray-500 dark:text-gray-400">
            ({lines.length})
          </span>
        </button>
        {onClear ? (
          <button
            type="button"
            className="text-xs text-gray-600 underline dark:text-gray-300"
            onClick={onClear}
            data-testid="workbench-console-clear"
          >
            Clear
          </button>
        ) : null}
      </div>
      {open ? (
        <ul
          className="max-h-40 space-y-1 overflow-y-auto border-t border-gray-200 px-3 py-2 font-mono text-xs dark:border-gray-700"
          data-testid="workbench-console-lines"
        >
          {lines.length === 0 ? (
            <li className="text-gray-500 dark:text-gray-400">No messages yet.</li>
          ) : (
            lines.map((line, index) => (
              <li
                key={`${line.at}-${index}`}
                className={
                  line.level === 'error'
                    ? 'text-rose-700 dark:text-rose-300'
                    : line.level === 'warn'
                      ? 'text-amber-800 dark:text-amber-200'
                      : 'text-gray-800 dark:text-gray-200'
                }
                data-level={line.level}
              >
                <span className="text-gray-500 dark:text-gray-400">
                  [{line.source}]
                </span>{' '}
                {line.message}
              </li>
            ))
          )}
        </ul>
      ) : null}
    </section>
  );
}

/**
 * Pull-up structured console for the F7 live workbench (UJ-017 / #694).
 * F15: registry code tooltips + lightweight catalog panel (E11-29 / E11-31).
 */

import { useState, type ReactNode } from 'react';
import { ChevronDown, ChevronUp, Terminal } from 'lucide-react';
import type { LiveWorkbenchConsoleLine } from '@/hooks/useLiveWorkbenchAssist';
import type { LintIssueCatalogEntry } from '@/utils/api';
import { resolveLintIssueTooltip } from '@/utils/lintIssueCatalog';
import { consoleLevelPasses, type ConvertLogLevel } from '/utils/convertParams';

const CODE_TOKEN = /(\[[A-Z][A-Z0-9_]*\])/g;

export interface WorkbenchConsoleProps {
  lines: LiveWorkbenchConsoleLine[];
  onClear?: () => void;
  /** Invoked when a console line action button is clicked (e.g. add_terminator). */
  onLineAction?: (actionId: string) => void;
  defaultOpen?: boolean;
  /** Minimum severity to show (operator Log Level). Default INFO. */
  minLogLevel?: ConvertLogLevel;
  /** Registry catalog keyed by code (GET /lint-issue-catalog). */
  catalogByCode?: Map<string, LintIssueCatalogEntry>;
  /** Full catalog rows for the lightweight panel. */
  catalogEntries?: LintIssueCatalogEntry[];
}

function messageWithCodeTooltips(
  message: string,
  catalogByCode: Map<string, LintIssueCatalogEntry> | undefined,
): ReactNode {
  if (!catalogByCode || catalogByCode.size === 0) {
    return message;
  }
  const parts = message.split(CODE_TOKEN);
  return parts.map((part, index) => {
    const match = /^\[([A-Z][A-Z0-9_]*)\]$/.exec(part);
    if (!match) {
      return <span key={index}>{part}</span>;
    }
    const code = match[1];
    return (
      <span
        key={index}
        title={resolveLintIssueTooltip(catalogByCode, code)}
        className="cursor-help underline decoration-dotted underline-offset-2"
        data-testid={`lint-code-tooltip-${code}`}
      >
        {part}
      </span>
    );
  });
}

/**
 * Collapsible pull-up console for live-assist messages.
 *
 * @param props.minLogLevel - Filter lines below this severity (client-side)
 * @param props.catalogByCode - Optional registry map for code tooltips
 */
export function WorkbenchConsole({
  lines,
  onClear,
  onLineAction,
  defaultOpen = false,
  minLogLevel = 'INFO',
  catalogByCode,
  catalogEntries = [],
}: WorkbenchConsoleProps) {
  const [open, setOpen] = useState(defaultOpen);
  const [catalogOpen, setCatalogOpen] = useState(false);
  const visibleLines = lines.filter((line) =>
    consoleLevelPasses(line.level, minLogLevel),
  );

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
            ({visibleLines.length}
            {visibleLines.length !== lines.length ? `/${lines.length}` : ''})
          </span>
        </button>
        {onClear ? (
          <button
            type="button"
            className="text-xs text-gray-600 underline dark:text-gray-300"
            onClick={onClear}
            data-testid="workbench-console-clear"
          >
            Clear log
          </button>
        ) : null}
      </div>
      {open ? (
        <ul
          className="max-h-40 space-y-1 overflow-y-auto border-t border-gray-200 px-3 py-2 font-mono text-xs dark:border-gray-700"
          data-testid="workbench-console-lines"
        >
          {visibleLines.length === 0 ? (
            <li className="text-gray-500 dark:text-gray-400">
              {lines.length === 0
                ? 'No messages yet.'
                : `No messages at ${minLogLevel} or above.`}
            </li>
          ) : (
            visibleLines.map((line, index) => (
              <li
                key={`${line.at}-${index}`}
                className={
                  line.level === 'error'
                    ? 'text-rose-700 dark:text-rose-300'
                    : line.level === 'warn'
                      ? 'text-amber-800 dark:text-amber-200'
                      : line.level === 'info'
                        ? 'text-sky-700 dark:text-sky-300'
                        : 'text-gray-800 dark:text-gray-200'
                }
                data-level={line.level}
              >
                <span className="text-gray-500 dark:text-gray-400">
                  [{line.source}]
                </span>{' '}
                {messageWithCodeTooltips(line.message, catalogByCode)}
                {line.action && onLineAction ? (
                  <button
                    type="button"
                    className="ml-2 rounded border border-sky-400 px-1.5 py-0.5 text-[11px] font-sans text-sky-800 hover:bg-sky-100 dark:border-sky-600 dark:text-sky-200 dark:hover:bg-sky-950"
                    data-testid={`console-action-${line.action.id}`}
                    onClick={() => onLineAction(line.action!.id)}
                  >
                    {line.action.label}
                  </button>
                ) : null}
              </li>
            ))
          )}
        </ul>
      ) : null}
      {catalogEntries.length > 0 ? (
        <div
          className="border-t border-gray-200 px-3 py-2 dark:border-gray-700"
          data-testid="lint-issue-catalog-panel"
        >
          <button
            type="button"
            className="text-xs font-medium text-gray-700 underline dark:text-gray-200"
            aria-expanded={catalogOpen}
            onClick={() => setCatalogOpen((v) => !v)}
            data-testid="lint-issue-catalog-toggle"
          >
            Lint issue catalog ({catalogEntries.length})
          </button>
          {catalogOpen ? (
            <ul
              className="mt-2 max-h-36 space-y-1 overflow-y-auto font-mono text-[11px] text-gray-700 dark:text-gray-300"
              data-testid="lint-issue-catalog-list"
            >
              {catalogEntries.slice(0, 80).map((entry) => (
                <li key={entry.code} title={entry.message_template}>
                  <span className="font-semibold">{entry.code}</span>{' '}
                  <span className="text-gray-500 dark:text-gray-400">
                    ({entry.severity})
                  </span>
                </li>
              ))}
              {catalogEntries.length > 80 ? (
                <li className="text-gray-500">
                  …and {catalogEntries.length - 80} more
                </li>
              ) : null}
            </ul>
          ) : null}
        </div>
      ) : null}
    </section>
  );
}

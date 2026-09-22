/**
 * IDE-style library workbench shell: catalog | editor | optional previews.
 */

import { useState } from 'react';
import type { ReactNode } from 'react';

import {
  PROFILES_WORKBENCH_CATALOG_LABEL,
  PROFILES_WORKBENCH_EDITOR_LABEL,
  PROFILES_WORKBENCH_PREVIEW_IWXXM,
  PROFILES_WORKBENCH_PREVIEW_IWXXM_HELP,
  PROFILES_WORKBENCH_PREVIEW_ISSUES,
  PROFILES_WORKBENCH_PREVIEW_ISSUES_HELP,
  PROFILES_WORKBENCH_PREVIEW_IWXXM_PLACEHOLDER,
  PROFILES_WORKBENCH_PREVIEW_ISSUES_PLACEHOLDER,
  PROFILES_TOOLTIP_WORKBENCH,
} from '../../utils/conversionProfilesCopy';
import { Tooltip, TooltipContent, TooltipTrigger } from './ui/tooltip';

/**
 * Type `LibraryWorkbenchShellProps`.
 * @example
 * const _ = true;
 */
export type LibraryWorkbenchShellProps = {
  kind: string;
  catalog: ReactNode;
  editor: ReactNode;
};

/**
 * Three-pane workbench for Profile Builder library tabs.
 *
 * Preview toggles default off (IWXXM preview + validation issues).
 *
 * @param props.kind - Library kind slug for testids
 * @param props.catalog - Catalog / asset list column
 * @param props.editor - Item editor column
 * @example
 * const _ = true;
 */
export function LibraryWorkbenchShell({
  kind,
  catalog,
  editor,
}: LibraryWorkbenchShellProps) {
  const [iwxxmPreview, setIwxxmPreview] = useState(false);
  const [issuesPreview, setIssuesPreview] = useState(false);

  return (
    <div
      className="space-y-3"
      data-testid={`library-workbench-${kind}`}
      data-workbench-kind={kind}
    >
      <Tooltip>
        <TooltipTrigger asChild>
          <p
            className="cursor-default text-xs text-gray-600 dark:text-gray-400"
            data-testid={`library-workbench-hint-${kind}`}
          >
            {PROFILES_TOOLTIP_WORKBENCH}
          </p>
        </TooltipTrigger>
        <TooltipContent side="bottom" className="max-w-xs text-balance">
          {PROFILES_TOOLTIP_WORKBENCH}
        </TooltipContent>
      </Tooltip>

      <div className="grid grid-cols-1 gap-3 lg:grid-cols-2">
        <section
          className="min-w-0 space-y-2 rounded border border-gray-200 p-3 dark:border-gray-700"
          data-testid={`library-workbench-catalog-${kind}`}
          aria-label={PROFILES_WORKBENCH_CATALOG_LABEL}
        >
          <h3 className="text-xs font-medium uppercase tracking-wide text-gray-500">
            {PROFILES_WORKBENCH_CATALOG_LABEL}
          </h3>
          {catalog}
        </section>
        <section
          className="min-w-0 space-y-2 rounded border border-gray-200 p-3 dark:border-gray-700"
          data-testid={`library-workbench-editor-${kind}`}
          aria-label={PROFILES_WORKBENCH_EDITOR_LABEL}
        >
          <h3 className="text-xs font-medium uppercase tracking-wide text-gray-500">
            {PROFILES_WORKBENCH_EDITOR_LABEL}
          </h3>
          {editor}
        </section>
      </div>

      <div
        className="flex flex-wrap items-center gap-4 rounded border border-dashed border-gray-300 p-3 dark:border-gray-600"
        data-testid={`library-workbench-previews-${kind}`}
      >
        <label className="flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            data-testid={`library-workbench-preview-iwxxm-${kind}`}
            checked={iwxxmPreview}
            onChange={(e) => setIwxxmPreview(e.target.checked)}
          />
          <Tooltip>
            <TooltipTrigger asChild>
              <span className="cursor-default">{PROFILES_WORKBENCH_PREVIEW_IWXXM}</span>
            </TooltipTrigger>
            <TooltipContent side="top" className="max-w-xs text-balance">
              {PROFILES_WORKBENCH_PREVIEW_IWXXM_HELP}
            </TooltipContent>
          </Tooltip>
        </label>
        <label className="flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            data-testid={`library-workbench-preview-issues-${kind}`}
            checked={issuesPreview}
            onChange={(e) => setIssuesPreview(e.target.checked)}
          />
          <Tooltip>
            <TooltipTrigger asChild>
              <span className="cursor-default">
                {PROFILES_WORKBENCH_PREVIEW_ISSUES}
              </span>
            </TooltipTrigger>
            <TooltipContent side="top" className="max-w-xs text-balance">
              {PROFILES_WORKBENCH_PREVIEW_ISSUES_HELP}
            </TooltipContent>
          </Tooltip>
        </label>
      </div>

      {iwxxmPreview ? (
        <div
          className="rounded border border-gray-200 bg-gray-50 p-3 text-sm dark:border-gray-700 dark:bg-gray-900/40"
          data-testid={`library-workbench-preview-iwxxm-panel-${kind}`}
        >
          {PROFILES_WORKBENCH_PREVIEW_IWXXM_PLACEHOLDER}
        </div>
      ) : null}
      {issuesPreview ? (
        <div
          className="rounded border border-gray-200 bg-gray-50 p-3 text-sm dark:border-gray-700 dark:bg-gray-900/40"
          data-testid={`library-workbench-preview-issues-panel-${kind}`}
        >
          {PROFILES_WORKBENCH_PREVIEW_ISSUES_PLACEHOLDER}
        </div>
      ) : null}
    </div>
  );
}

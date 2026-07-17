/**
 * Side-by-side IWXXM preview pane for Soft-preview / Live IWXXM (F10 / UJ-021).
 */

import { prettyPrintXml } from '/utils/prettyXml';

export type IwxxmPreviewStatus = 'empty' | 'passed' | 'soft-fail';
export type IwxxmPreviewMode = 'idle' | 'soft-preview' | 'live' | 'hard';

export interface IwxxmPreviewPaneProps {
  xml: string;
  status: IwxxmPreviewStatus;
  mode: IwxxmPreviewMode;
  /** Plain-language soft-fail copy (no raw LAYER12_SOFT_FAIL as primary text). */
  softFailDetail?: string;
  failedSpanCount?: number;
  onFailedSpanFocus?: () => void;
  className?: string;
}

/**
 * Dedicated preview surface for Soft-preview and Live IWXXM output.
 *
 * @param props.xml - Most recent IWXXM XML (pretty-printed for display)
 * @param props.status - empty | passed | soft-fail
 * @param props.mode - Which path produced the XML
 */
export function IwxxmPreviewPane({
  xml,
  status,
  mode,
  softFailDetail,
  failedSpanCount = 0,
  onFailedSpanFocus,
  className = '',
}: IwxxmPreviewPaneProps) {
  const pretty = xml.trim() ? prettyPrintXml(xml) : '';
  const showSoftBadge = mode === 'soft-preview' || status === 'soft-fail';

  return (
    <section
      data-testid="iwxxm-preview-pane"
      aria-label="IWXXM preview"
      className={`flex min-h-[12rem] flex-col rounded-md border border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-900 lg:min-h-0 ${className}`}
    >
      <header className="flex flex-wrap items-center gap-2 border-b border-gray-200 px-3 py-2 dark:border-gray-700">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-white">
          IWXXM preview
        </h3>
        {status === 'passed' ? (
          <span
            data-testid="iwxxm-preview-badge"
            className="rounded-full bg-emerald-100 px-2 py-0.5 text-xs font-medium text-emerald-900 dark:bg-emerald-950 dark:text-emerald-100"
          >
            Passed
          </span>
        ) : null}
        {showSoftBadge && status !== 'passed' ? (
          <span
            data-testid="iwxxm-preview-badge"
            className="rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-950 dark:bg-amber-950 dark:text-amber-100"
          >
            Soft preview — not for publish
          </span>
        ) : null}
        {showSoftBadge && status === 'passed' ? (
          <span className="text-xs text-gray-500 dark:text-gray-400">Soft preview</span>
        ) : null}
        {failedSpanCount > 0 ? (
          <button
            type="button"
            data-testid="iwxxm-preview-failed-count"
            className="ml-auto text-xs font-medium text-rose-700 underline-offset-2 hover:underline dark:text-rose-300"
            onClick={onFailedSpanFocus}
          >
            {failedSpanCount} failed span{failedSpanCount === 1 ? '' : 's'}
          </button>
        ) : null}
      </header>

      {status === 'soft-fail' && softFailDetail ? (
        <p
          data-testid="iwxxm-preview-soft-fail"
          className="border-b border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-950 dark:border-amber-900 dark:bg-amber-950/40 dark:text-amber-100"
          role="status"
        >
          {softFailDetail}
        </p>
      ) : null}

      <div className="min-h-0 flex-1 overflow-auto p-3">
        {pretty ? (
          <pre
            data-testid="iwxxm-preview-xml"
            className="whitespace-pre-wrap break-all font-mono text-xs text-gray-800 dark:text-gray-100"
          >
            {pretty}
          </pre>
        ) : (
          <p
            data-testid="iwxxm-preview-empty"
            className="text-sm text-gray-500 dark:text-gray-400"
          >
            Soft-preview or Live IWXXM output will appear here.
          </p>
        )}
      </div>
    </section>
  );
}

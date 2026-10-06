/**
 * Side-by-side IWXXM preview pane for Soft-preview / Live IWXXM (F10 / UJ-021).
 */

import { prettyPrintXml } from '/utils/prettyXml';
import { xmlLinesForSelection, type GroupTrace } from '/utils/liveConvertTrace';

/**
 * Type `IwxxmPreviewStatus`.
 * @example
 * const _ = true;
 */
export type IwxxmPreviewStatus = 'empty' | 'passed' | 'soft-fail';
/**
 * Type `IwxxmPreviewMode`.
 * @example
 * const _ = true;
 */
export type IwxxmPreviewMode = 'idle' | 'soft-preview' | 'live' | 'hard';

/**
 * Type `IwxxmPreviewPaneProps`.
 * @example
 * const _ = true;
 */
export interface IwxxmPreviewPaneProps {
  xml: string;
  status: IwxxmPreviewStatus;
  mode: IwxxmPreviewMode;
  /** Plain-language soft-fail copy (no raw LAYER12_SOFT_FAIL as primary text). */
  softFailDetail?: string;
  failedSpanCount?: number;
  onFailedSpanFocus?: () => void;
  className?: string;
  /** Line numbers for the live Convert pane. */
  numbered?: boolean;
  /** TAC group text to mark in the preview. */
  highlightToken?: string;
  /** Selected group offsets. Used with the convert pairing. */
  highlightStart?: number;
  highlightEnd?: number;
  /** TAC group to IWXXM element pairing from the convert preview. */
  groupTrace?: GroupTrace[];
  /** TAC errors or undecoded groups mean the preview is not complete. */
  incomplete?: boolean;
  /** Conversion profile that emitted this preview. */
  conversionProfile?: string;
  /** Wrap long XML lines. Off keeps each line on one row. */
  wrapXml?: boolean;
}

/**
 * Dedicated preview surface for Soft-preview and Live IWXXM output.
 *
 * @param props.xml - Most recent IWXXM XML (pretty-printed for display)
 * @param props.status - empty | passed | soft-fail
 * @param props.mode - Which path produced the XML
 * @example
 * const _ = true;
 */
export function IwxxmPreviewPane({
  xml,
  status,
  mode,
  softFailDetail,
  failedSpanCount = 0,
  onFailedSpanFocus,
  className = '',
  numbered = false,
  highlightToken = '',
  highlightStart,
  highlightEnd,
  groupTrace = [],
  incomplete = false,
  conversionProfile,
  wrapXml = true,
}: IwxxmPreviewPaneProps) {
  const pretty = xml.trim() ? prettyPrintXml(xml) : '';
  const showSoftBadge = mode === 'soft-preview' || status === 'soft-fail';
  const highlighted = new Set(
    xmlLinesForSelection(
      pretty,
      highlightToken,
      highlightStart,
      highlightEnd,
      groupTrace,
    ),
  );
  const lines = pretty ? pretty.split('\n') : [];

  return (
    <section
      data-testid="iwxxm-preview-pane"
      aria-label="IWXXM preview"
      className={`flex max-h-80 min-h-0 flex-col overflow-hidden rounded-md border border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-900 ${className}`}
    >
      <header className="flex flex-wrap items-center gap-2 border-b border-gray-200 px-3 py-2 dark:border-gray-700">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-white">
          Live IWXXM
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
            Soft preview, not for publishing
          </span>
        ) : null}
        {showSoftBadge && status === 'passed' ? (
          <span className="text-xs text-gray-500 dark:text-gray-400">Soft preview</span>
        ) : null}
        {conversionProfile ? (
          <span
            className="text-xs text-gray-600 dark:text-gray-300"
            data-testid="iwxxm-conversion-profile"
          >
            Conversion profile: {conversionProfile}
          </span>
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

      {incomplete ? (
        <p
          data-testid="iwxxm-preview-incomplete"
          className="border-b border-gray-200 px-3 py-2 text-xs font-medium text-gray-900 dark:border-gray-700 dark:text-gray-100"
          role="status"
        >
          Incomplete: fix TAC errors
        </p>
      ) : null}

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
            className={`${wrapXml ? 'whitespace-pre-wrap break-all' : 'whitespace-pre'} font-mono text-xs text-gray-800 dark:text-gray-100`}
          >
            {numbered
              ? lines.map((line, index) => {
                  const lineNumber = index + 1;
                  const marked = highlighted.has(lineNumber);
                  return (
                    <div
                      key={`${lineNumber}-${line}`}
                      data-testid={marked ? 'iwxxm-preview-line-hit' : undefined}
                      className={
                        marked
                          ? 'bg-sky-100 text-sky-950 dark:bg-sky-950 dark:text-sky-50'
                          : undefined
                      }
                    >
                      <span className="mr-2 inline-block w-6 text-right text-gray-500">
                        {lineNumber}
                      </span>
                      {line || ' '}
                    </div>
                  );
                })
              : pretty}
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

/**
 * Per-stem Quality metrics detail — TAC/XML panes, diagnostics, XML diff.
 *
 * F7.q / EV-054 M4 + EV-055 M4 (AC1/AC6 — C14N panes + validate chips) +
 * EV-056 collapsible equal-context hunks (`D-S066-context-n=1`) +
 * EV-058 selectable Inline vs Side-by-side (`D-S068-01-control=3a`).
 */

import { useEffect, useMemo, useRef, useState, type Ref } from 'react';
import type { QualityMetricsDetailResponse } from '@/utils/openapiTypes';
import {
  collapseEqualContext,
  DEFAULT_DIFF_CONTEXT,
  type CollapsedDiffSegment,
} from '@/utils/collapseEqualContext';
import {
  readDiffLayoutPreference,
  sideBySideFromUnified,
  writeDiffLayoutPreference,
  type QualityMetricsDiffLayout,
  type SideBySideDiffRow,
} from '@/utils/qualityMetricsDiffLayout';
import { qualityMetricsDisplayXml } from '@/utils/qualityMetricsDisplayXml';
import {
  isUnifiedDiffEmpty,
  unifiedLineDiff,
  type UnifiedDiffLine,
} from '@/utils/unifiedLineDiff';
import { validateDispositionChips } from '@/utils/validateDispositionChips';
import {
  formatMatchStatusLabel,
  QUALITY_METRICS_DEFERRED_LABEL,
} from '@/utils/qualityMetricsCopy';
import { Card } from './ui/card';

export const QUALITY_METRICS_DIFF_EMPTY_LABEL = 'No XML differences';
export const QUALITY_METRICS_EMPTY_DIAGNOSTICS = 'None';
export const QUALITY_METRICS_XML_VIEW_NORMALIZED = 'Normalized XML';
export const QUALITY_METRICS_XML_VIEW_RAW = 'Raw XML';
export const QUALITY_METRICS_XML_VIEW_HELP =
  'Official and converted panes default to normalized, pretty-printed XML so formatting noise is hidden. Turn on Raw XML to inspect original whitespace. The line-by-line diff below always compares the normalized forms.';
export const QUALITY_METRICS_DIFF_EXPAND_ALL = 'Show all unchanged lines';
export const QUALITY_METRICS_DIFF_COLLAPSE_ALL = 'Hide distant unchanged lines';
export const QUALITY_METRICS_BACK_TO_LIST = 'Back to list';
export const QUALITY_METRICS_DIFF_HEADING = 'Line-by-line XML differences';
export const QUALITY_METRICS_DIFF_LAYOUT_INLINE = 'Inline (unified)';
export const QUALITY_METRICS_DIFF_LAYOUT_SIDE_BY_SIDE = 'Side-by-side';
export const QUALITY_METRICS_DIFF_LAYOUT_LEGEND =
  'Choose how to compare official vs converted XML. The default is a single inline (unified) diff.';
export const QUALITY_METRICS_RESIDUALS_HELP =
  'TAC tokens left over after conversion (should usually be empty).';
export const QUALITY_METRICS_LINT_HELP =
  'TAC business-rule findings from the lint engine.';
export const QUALITY_METRICS_VALIDATE_HELP =
  'IWXXM schema and Schematron findings from the validate engine.';

interface QualityMetricsDetailProps {
  /** Detail payload from GET /quality-metrics/{stem}. */
  detail: QualityMetricsDetailResponse;
  /** Clear selection / return to list focus. */
  onClose?: () => void;
  /** Label for the close / back control (default Close detail). */
  closeLabel?: string;
}

/**
 * Render inspectable TAC/XML panes, match status, diagnostics, and XML diff.
 *
 * @param props.detail - Stem detail response
 * @param props.onClose - Optional close handler
 * @param props.closeLabel - Optional close button label
 */
export function QualityMetricsDetail({
  detail,
  onClose,
  closeLabel = 'Close detail',
}: QualityMetricsDetailProps) {
  const [showRawXml, setShowRawXml] = useState(false);
  const [expandAll, setExpandAll] = useState(false);
  const [expandedCollapseKeys, setExpandedCollapseKeys] = useState<Set<string>>(
    () => new Set(),
  );
  const [diffLayout, setDiffLayout] = useState<QualityMetricsDiffLayout>(() =>
    readDiffLayoutPreference(),
  );
  const sideBySideLeftRef = useRef<HTMLPreElement | null>(null);
  const sideBySideRightRef = useRef<HTMLPreElement | null>(null);
  const syncingScroll = useRef(false);

  useEffect(() => {
    writeDiffLayoutPreference(diffLayout);
  }, [diffLayout]);

  const officialC14n = useMemo(
    () => qualityMetricsDisplayXml(detail.official_xml ?? ''),
    [detail.official_xml],
  );
  const convertedC14n = useMemo(
    () => qualityMetricsDisplayXml(detail.converted_xml ?? ''),
    [detail.converted_xml],
  );

  const officialPane = showRawXml ? (detail.official_xml ?? '') : officialC14n;
  const convertedPane = showRawXml ? (detail.converted_xml ?? '') : convertedC14n;

  const diffLines = useMemo(
    () => unifiedLineDiff(officialC14n, convertedC14n),
    [convertedC14n, officialC14n],
  );
  const diffEmpty = isUnifiedDiffEmpty(diffLines);

  const collapsedSegments = useMemo(
    () => collapseEqualContext(diffLines, { context: DEFAULT_DIFF_CONTEXT }),
    [diffLines],
  );

  const sideBySideRows = useMemo(() => sideBySideFromUnified(diffLines), [diffLines]);

  const dispositionChips = useMemo(
    () => validateDispositionChips(detail.validate_issues ?? []),
    [detail.validate_issues],
  );

  const hasCollapseSegments = collapsedSegments.some((s) => s.type === 'collapse');

  const collapseKey = (segment: CollapsedDiffSegment): string =>
    `c-${segment.startIndex}-${segment.lines.length}`;

  const toggleCollapse = (key: string) => {
    setExpandedCollapseKeys((prev) => {
      const next = new Set(prev);
      if (next.has(key)) {
        next.delete(key);
      } else {
        next.add(key);
      }
      return next;
    });
  };

  /** Best-effort synced scroll between side-by-side panes (`D-S068-01-ac=2b`). */
  const onSideBySideScroll = (source: 'left' | 'right') => {
    if (syncingScroll.current) {
      return;
    }
    const from =
      source === 'left' ? sideBySideLeftRef.current : sideBySideRightRef.current;
    const to =
      source === 'left' ? sideBySideRightRef.current : sideBySideLeftRef.current;
    if (!from || !to) {
      return;
    }
    syncingScroll.current = true;
    to.scrollTop = from.scrollTop;
    to.scrollLeft = from.scrollLeft;
    requestAnimationFrame(() => {
      syncingScroll.current = false;
    });
  };

  return (
    <section
      className="space-y-4"
      data-testid="quality-metrics-detail"
      aria-label={`Quality metrics detail for ${detail.stem}`}
    >
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
            {detail.stem}
          </h2>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            {detail.product.toUpperCase()} · {detail.tier} ·{' '}
            <span data-testid="quality-metrics-match-status">
              {formatMatchStatusLabel(detail.match_status)}
            </span>
            {detail.deferred && detail.match_status !== 'deferred'
              ? ` · ${QUALITY_METRICS_DEFERRED_LABEL}`
              : ''}
          </p>
          {detail.deferral_reason ? (
            <p className="mt-1 text-sm text-amber-800 dark:text-amber-200">
              {detail.deferral_reason}
            </p>
          ) : null}
          <div
            className="mt-2 flex flex-wrap gap-2"
            data-testid="quality-metrics-validate-chips"
            aria-label="Validation status"
          >
            {dispositionChips.map((chip) => (
              <span
                key={chip.id}
                data-testid={`quality-metrics-validate-chip-${chip.id}`}
                data-ok={chip.ok ? 'true' : 'false'}
                className={
                  chip.ok
                    ? 'rounded-md border border-emerald-300 bg-emerald-50 px-2 py-0.5 text-xs text-emerald-900 dark:border-emerald-700 dark:bg-emerald-950 dark:text-emerald-100'
                    : 'rounded-md border border-amber-300 bg-amber-50 px-2 py-0.5 text-xs text-amber-900 dark:border-amber-700 dark:bg-amber-950 dark:text-amber-100'
                }
              >
                {chip.label}
              </span>
            ))}
          </div>
        </div>
        {onClose ? (
          <button
            type="button"
            className="rounded-md border border-gray-300 px-3 py-1.5 text-sm dark:border-gray-600"
            data-testid="quality-metrics-detail-close"
            onClick={onClose}
          >
            {closeLabel}
          </button>
        ) : null}
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <label
          className="inline-flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300"
          data-testid="quality-metrics-xml-view-toggle"
        >
          <input
            type="checkbox"
            checked={showRawXml}
            onChange={(event) => setShowRawXml(event.target.checked)}
            data-testid="quality-metrics-xml-view-raw"
          />
          <span>{QUALITY_METRICS_XML_VIEW_RAW}</span>
        </label>
        <span
          className="text-xs text-gray-500 dark:text-gray-400"
          data-testid="quality-metrics-xml-view-mode"
        >
          {showRawXml
            ? QUALITY_METRICS_XML_VIEW_RAW
            : QUALITY_METRICS_XML_VIEW_NORMALIZED}
        </span>
        <p className="basis-full text-xs text-gray-500 dark:text-gray-400">
          {QUALITY_METRICS_XML_VIEW_HELP}
        </p>
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <TextPane
          title="Source TAC"
          testId="quality-metrics-pane-tac"
          emptyLabel="No TAC available"
          value={detail.tac}
        />
        <TextPane
          title="Official XML"
          testId="quality-metrics-pane-official-xml"
          emptyLabel="No official XML available"
          value={officialPane}
        />
        <TextPane
          title="Converted XML"
          testId="quality-metrics-pane-converted-xml"
          emptyLabel="No converted XML available"
          value={convertedPane}
        />
      </div>

      <Card className="p-4" data-testid="quality-metrics-unified-diff">
        <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            {QUALITY_METRICS_DIFF_HEADING}
          </h3>
          <div className="flex flex-wrap items-center gap-2">
            <div
              className="inline-flex rounded-md border border-gray-300 dark:border-gray-600"
              role="radiogroup"
              aria-label="XML diff layout"
              data-testid="quality-metrics-diff-layout"
            >
              <button
                type="button"
                role="radio"
                aria-checked={diffLayout === 'unified'}
                className={
                  diffLayout === 'unified'
                    ? 'bg-gray-800 px-2 py-1 text-xs text-white dark:bg-gray-200 dark:text-gray-900'
                    : 'px-2 py-1 text-xs text-gray-700 dark:text-gray-300'
                }
                data-testid="quality-metrics-diff-layout-unified"
                onClick={() => setDiffLayout('unified')}
              >
                {QUALITY_METRICS_DIFF_LAYOUT_INLINE}
              </button>
              <button
                type="button"
                role="radio"
                aria-checked={diffLayout === 'side-by-side'}
                className={
                  diffLayout === 'side-by-side'
                    ? 'bg-gray-800 px-2 py-1 text-xs text-white dark:bg-gray-200 dark:text-gray-900'
                    : 'px-2 py-1 text-xs text-gray-700 dark:text-gray-300'
                }
                data-testid="quality-metrics-diff-layout-side-by-side"
                onClick={() => setDiffLayout('side-by-side')}
              >
                {QUALITY_METRICS_DIFF_LAYOUT_SIDE_BY_SIDE}
              </button>
            </div>
            {diffLayout === 'unified' && !diffEmpty && hasCollapseSegments ? (
              <button
                type="button"
                className="rounded-md border border-gray-300 px-2 py-1 text-xs dark:border-gray-600"
                data-testid="quality-metrics-diff-expand-all"
                onClick={() => {
                  setExpandAll((prev) => !prev);
                  if (expandAll) {
                    setExpandedCollapseKeys(new Set());
                  }
                }}
              >
                {expandAll
                  ? QUALITY_METRICS_DIFF_COLLAPSE_ALL
                  : QUALITY_METRICS_DIFF_EXPAND_ALL}
              </button>
            ) : null}
          </div>
        </div>
        <p className="mb-2 text-xs text-gray-500 dark:text-gray-400">
          {QUALITY_METRICS_DIFF_LAYOUT_LEGEND}
        </p>
        {diffEmpty ? (
          <p
            className="text-sm text-gray-500 dark:text-gray-400"
            data-testid="quality-metrics-diff-empty"
          >
            {QUALITY_METRICS_DIFF_EMPTY_LABEL}
          </p>
        ) : diffLayout === 'side-by-side' ? (
          <SideBySideDiff
            rows={sideBySideRows}
            leftRef={sideBySideLeftRef}
            rightRef={sideBySideRightRef}
            onScrollLeft={() => onSideBySideScroll('left')}
            onScrollRight={() => onSideBySideScroll('right')}
          />
        ) : (
          <pre
            className="max-h-96 overflow-auto rounded border border-gray-200 bg-gray-950 p-3 font-mono text-xs text-gray-100 dark:border-gray-700"
            data-testid="quality-metrics-diff-body"
          >
            {collapsedSegments.map((segment) => {
              if (segment.type === 'lines') {
                return segment.lines.map((line, index) => (
                  <DiffLineRow key={`l-${segment.startIndex}-${index}`} line={line} />
                ));
              }
              const key = collapseKey(segment);
              const expanded = expandAll || expandedCollapseKeys.has(key);
              if (expanded) {
                return segment.lines.map((line, index) => (
                  <DiffLineRow key={`${key}-${index}`} line={line} />
                ));
              }
              return (
                <button
                  key={key}
                  type="button"
                  className="block w-full bg-gray-900 py-1 text-left text-blue-300 hover:bg-gray-800"
                  data-testid="quality-metrics-diff-expand-hunk"
                  data-hidden-count={segment.lines.length}
                  onClick={() => toggleCollapse(key)}
                >
                  {`Expand ${segment.lines.length} unchanged line${
                    segment.lines.length === 1 ? '' : 's'
                  }`}
                </button>
              );
            })}
          </pre>
        )}
      </Card>

      <div className="grid gap-4 md:grid-cols-3">
        <DiagnosticsPane
          title="Residuals"
          help={QUALITY_METRICS_RESIDUALS_HELP}
          testId="quality-metrics-pane-residuals"
          items={detail.residuals}
        />
        <DiagnosticsPane
          title="Lint issues"
          help={QUALITY_METRICS_LINT_HELP}
          testId="quality-metrics-pane-lint"
          items={detail.lint_issues}
        />
        <DiagnosticsPane
          title="Validation issues"
          help={QUALITY_METRICS_VALIDATE_HELP}
          testId="quality-metrics-pane-validate"
          items={detail.validate_issues}
        />
      </div>
    </section>
  );
}

function TextPane({
  title,
  testId,
  value,
  emptyLabel,
}: {
  title: string;
  testId: string;
  value: string;
  emptyLabel: string;
}) {
  const trimmed = value?.trim() ?? '';
  return (
    <Card className="p-3" data-testid={testId}>
      <h3 className="mb-2 text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">
        {title}
      </h3>
      {trimmed ? (
        <pre className="max-h-64 overflow-auto whitespace-pre-wrap break-all font-mono text-xs text-gray-800 dark:text-gray-200">
          {value}
        </pre>
      ) : (
        <p className="text-sm italic text-gray-500 dark:text-gray-400">{emptyLabel}</p>
      )}
    </Card>
  );
}

function DiagnosticsPane({
  title,
  help,
  testId,
  items,
}: {
  title: string;
  help: string;
  testId: string;
  items: Record<string, unknown>[];
}) {
  return (
    <Card className="p-3" data-testid={testId}>
      <h3 className="mb-1 text-sm font-semibold text-gray-900 dark:text-gray-100">
        {title}
      </h3>
      <p className="mb-2 text-xs text-gray-500 dark:text-gray-400">{help}</p>
      {items.length === 0 ? (
        <p
          className="text-sm text-gray-500 dark:text-gray-400"
          data-testid={`${testId}-empty`}
        >
          {QUALITY_METRICS_EMPTY_DIAGNOSTICS}
        </p>
      ) : (
        <ul className="space-y-2 text-xs text-gray-800 dark:text-gray-200">
          {items.map((item, index) => (
            <li
              key={index}
              className="rounded border border-gray-200 bg-gray-50 p-2 font-mono dark:border-gray-700 dark:bg-gray-950"
            >
              {formatDiagnostic(item)}
            </li>
          ))}
        </ul>
      )}
    </Card>
  );
}

function DiffLineRow({ line }: { line: UnifiedDiffLine }) {
  const prefix = line.op === 'add' ? '+' : line.op === 'remove' ? '-' : ' ';
  const color =
    line.op === 'add'
      ? 'text-green-400'
      : line.op === 'remove'
        ? 'text-red-400'
        : 'text-gray-300';
  return (
    <div className={`${color} whitespace-pre-wrap break-all`}>
      {prefix}
      {line.text}
    </div>
  );
}

function SideBySideDiff({
  rows,
  leftRef,
  rightRef,
  onScrollLeft,
  onScrollRight,
}: {
  rows: SideBySideDiffRow[];
  leftRef: Ref<HTMLPreElement>;
  rightRef: Ref<HTMLPreElement>;
  onScrollLeft: () => void;
  onScrollRight: () => void;
}) {
  return (
    <div
      className="grid max-h-96 grid-cols-2 gap-2"
      data-testid="quality-metrics-diff-side-by-side"
    >
      <div>
        <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">
          Official
        </p>
        <pre
          ref={leftRef}
          className="max-h-80 overflow-auto rounded border border-gray-200 bg-gray-950 p-3 font-mono text-xs text-gray-100 dark:border-gray-700"
          data-testid="quality-metrics-diff-side-left"
          onScroll={onScrollLeft}
        >
          {rows.map((row, index) => (
            <SideBySideCell
              key={`L-${index}`}
              text={row.left}
              op={row.leftOp}
              side="left"
            />
          ))}
        </pre>
      </div>
      <div>
        <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">
          Converted
        </p>
        <pre
          ref={rightRef}
          className="max-h-80 overflow-auto rounded border border-gray-200 bg-gray-950 p-3 font-mono text-xs text-gray-100 dark:border-gray-700"
          data-testid="quality-metrics-diff-side-right"
          onScroll={onScrollRight}
        >
          {rows.map((row, index) => (
            <SideBySideCell
              key={`R-${index}`}
              text={row.right}
              op={row.rightOp}
              side="right"
            />
          ))}
        </pre>
      </div>
    </div>
  );
}

function SideBySideCell({
  text,
  op,
  side,
}: {
  text: string | null;
  op: SideBySideDiffRow['leftOp'] | SideBySideDiffRow['rightOp'];
  side: 'left' | 'right';
}) {
  const color =
    op === 'add'
      ? 'text-green-400'
      : op === 'remove'
        ? 'text-red-400'
        : op === 'empty'
          ? 'text-gray-600'
          : 'text-gray-300';
  const display = text === null ? ' ' : text;
  return (
    <div
      className={`${color} whitespace-pre-wrap break-all`}
      data-op={op}
      data-side={side}
    >
      {display}
    </div>
  );
}

function formatDiagnostic(item: Record<string, unknown>): string {
  const message =
    typeof item.message === 'string' && item.message.trim()
      ? item.message.trim()
      : typeof item.detail === 'string' && item.detail.trim()
        ? item.detail.trim()
        : '';
  const code =
    typeof item.code === 'string' && item.code.trim() ? item.code.trim() : '';
  if (message && code) {
    return `${code}: ${message}`;
  }
  if (message) {
    return message;
  }
  if (code) {
    return code;
  }
  try {
    return JSON.stringify(item);
  } catch {
    return String(item);
  }
}

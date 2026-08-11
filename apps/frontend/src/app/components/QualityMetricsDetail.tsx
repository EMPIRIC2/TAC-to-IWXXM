/**
 * Per-stem Quality metrics detail — TAC/XML panes, diagnostics, unified diff.
 *
 * F7.q / EV-054 M4 (AC2 / AC3).
 */

import { useMemo } from 'react';
import type { QualityMetricsDetailResponse } from '@/utils/openapiTypes';
import {
  isUnifiedDiffEmpty,
  unifiedLineDiff,
  type UnifiedDiffLine,
} from '@/utils/unifiedLineDiff';
import { Card } from './ui/card';

export const QUALITY_METRICS_DIFF_EMPTY_LABEL = 'No XML differences';
export const QUALITY_METRICS_EMPTY_DIAGNOSTICS = 'None';

interface QualityMetricsDetailProps {
  /** Detail payload from GET /quality-metrics/{stem}. */
  detail: QualityMetricsDetailResponse;
  /** Clear selection / return to list focus. */
  onClose?: () => void;
}

/**
 * Render inspectable TAC/XML panes, match status, diagnostics, and unified diff.
 *
 * @param props.detail - Stem detail response
 * @param props.onClose - Optional close handler
 */
export function QualityMetricsDetail({ detail, onClose }: QualityMetricsDetailProps) {
  const diffLines = useMemo(
    () => unifiedLineDiff(detail.official_xml ?? '', detail.converted_xml ?? ''),
    [detail.converted_xml, detail.official_xml],
  );
  const diffEmpty = isUnifiedDiffEmpty(diffLines);

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
            {detail.product.toUpperCase()} · {detail.tier} · match{' '}
            <span data-testid="quality-metrics-match-status">
              {detail.match_status}
            </span>
            {detail.deferred ? ' · deferred' : ''}
          </p>
          {detail.deferral_reason ? (
            <p className="mt-1 text-sm text-amber-800 dark:text-amber-200">
              {detail.deferral_reason}
            </p>
          ) : null}
        </div>
        {onClose ? (
          <button
            type="button"
            className="rounded-md border border-gray-300 px-3 py-1.5 text-sm dark:border-gray-600"
            data-testid="quality-metrics-detail-close"
            onClick={onClose}
          >
            Close detail
          </button>
        ) : null}
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
          value={detail.official_xml}
        />
        <TextPane
          title="Converted XML"
          testId="quality-metrics-pane-converted-xml"
          emptyLabel="No converted XML available"
          value={detail.converted_xml}
        />
      </div>

      <Card className="p-4" data-testid="quality-metrics-unified-diff">
        <h3 className="mb-2 text-sm font-semibold text-gray-900 dark:text-gray-100">
          Unified XML diff
        </h3>
        {diffEmpty ? (
          <p
            className="text-sm text-gray-500 dark:text-gray-400"
            data-testid="quality-metrics-diff-empty"
          >
            {QUALITY_METRICS_DIFF_EMPTY_LABEL}
          </p>
        ) : (
          <pre
            className="max-h-96 overflow-auto rounded border border-gray-200 bg-gray-950 p-3 font-mono text-xs text-gray-100 dark:border-gray-700"
            data-testid="quality-metrics-diff-body"
          >
            {diffLines.map((line, index) => (
              <DiffLineRow key={`${line.op}-${index}`} line={line} />
            ))}
          </pre>
        )}
      </Card>

      <div className="grid gap-4 md:grid-cols-3">
        <DiagnosticsPane
          title="Residuals"
          testId="quality-metrics-pane-residuals"
          items={detail.residuals}
        />
        <DiagnosticsPane
          title="Lint issues"
          testId="quality-metrics-pane-lint"
          items={detail.lint_issues}
        />
        <DiagnosticsPane
          title="Validate issues"
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
  testId,
  items,
}: {
  title: string;
  testId: string;
  items: Record<string, unknown>[];
}) {
  return (
    <Card className="p-3" data-testid={testId}>
      <h3 className="mb-2 text-sm font-semibold text-gray-900 dark:text-gray-100">
        {title}
      </h3>
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
    <div className={color}>
      {prefix}
      {line.text}
    </div>
  );
}

function formatDiagnostic(item: Record<string, unknown>): string {
  if (typeof item.message === 'string' && item.message.trim()) {
    const code = typeof item.code === 'string' ? `${item.code}: ` : '';
    return `${code}${item.message}`;
  }
  try {
    return JSON.stringify(item);
  } catch {
    return String(item);
  }
}

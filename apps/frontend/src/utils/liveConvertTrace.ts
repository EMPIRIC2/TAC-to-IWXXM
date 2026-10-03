/**
 * Helpers for the live Convert panes: lint wording, selection spans, and
 * which preview lines mention the selected TAC group.
 */

import type { TacSpanMark } from '/utils/tacEditorSpans';

/**
 * Type `LiveTraceTarget`.
 * @example
 * const _ = true;
 */
export interface LiveTraceTarget {
  start: number;
  end: number;
  code: string;
}

/**
 * Type `LintSeverityCount`.
 * @example
 * const _ = true;
 */
export interface LintSeverityCount {
  severity?: string;
}

/**
 * Count TAC lint errors. Warning and info do not count.
 *
 * @param issues - Lint issues from the live assist hook
 * @returns Number of error-severity issues
 * @example
 * const _ = true;
 */
export function lintErrorCount(issues: LintSeverityCount[]): number {
  return issues.filter((issue) => issue.severity === 'error').length;
}

/**
 * Count TAC lint warnings.
 *
 * @param issues - Lint issues from the live assist hook
 * @returns Number of warning-severity issues
 * @example
 * const _ = true;
 */
export function lintWarningCount(issues: LintSeverityCount[]): number {
  return issues.filter(
    (issue) => issue.severity === 'warning' || issue.severity === 'warn',
  ).length;
}

/**
 * Plain-language TAC lint summary. The words Error and Warning are in the text.
 *
 * @param issues - Lint issues from the live assist hook
 * @returns One-line summary for the TAC pane
 * @example
 * const _ = true;
 */
export function lintSummaryLabel(issues: LintSeverityCount[]): string {
  const errors = lintErrorCount(issues);
  if (errors > 0) {
    return errors === 1 ? '1 error in the TAC' : `${errors} errors in the TAC`;
  }
  const warnings = lintWarningCount(issues);
  if (warnings > 0) {
    return warnings === 1 ? 'TAC lint: 1 warning' : `TAC lint: ${warnings} warnings`;
  }
  const notes = issues.filter((issue) => issue.severity === 'info').length;
  if (notes === 1) return 'TAC lint: 1 note';
  if (notes > 1) return `TAC lint: ${notes} notes`;
  return 'TAC lint: passed';
}

/**
 * Preview is incomplete when TAC lint has an error, a group was not decoded,
 * or soft-preview reported a failed span.
 *
 * @param errorCount - TAC lint errors
 * @param residualCount - Undecoded groups
 * @param failedSpanCount - Soft-preview failed spans
 * @returns Whether the XML preview should be marked incomplete
 * @example
 * const _ = true;
 */
export function previewIsIncomplete(
  errorCount: number,
  residualCount: number,
  failedSpanCount: number,
): boolean {
  return errorCount > 0 || residualCount > 0 || failedSpanCount > 0;
}

/**
 * 1-based line numbers whose text contains the selected group.
 *
 * @param xml - Pretty-printed preview XML
 * @param token - Selected TAC group text
 * @returns Line numbers to highlight
 * @example
 * const _ = true;
 */
export function xmlLinesMatchingToken(xml: string, token: string): number[] {
  const needle = token.trim();
  if (!needle || !xml.trim()) {
    return [];
  }
  const lines = xml.split('\n');
  const hits: number[] = [];
  for (let index = 0; index < lines.length; index += 1) {
    if (lines[index]?.includes(needle)) {
      hits.push(index + 1);
    }
  }
  return hits;
}

const GROUP_ELEMENTS: { test: RegExp; needles: string[] }[] = [
  {
    test: /^(METAR|SPECI|TAF|SIGMET|AIRMET|VAA|TCA|SWXA|VONA)$/i,
    needles: [
      'iwxxm:METAR',
      'iwxxm:SPECI',
      'iwxxm:TAF',
      'iwxxm:SIGMET',
      'iwxxm:AIRMET',
    ],
  },
  { test: /^[A-Z][A-Z0-9]{3}$/, needles: ['aerodrome', 'designator'] },
  { test: /^\d{6}Z$/, needles: ['issueTime', 'observationTime', 'phenomenonTime'] },
  {
    test: /^(VRB|\d{3})\d{2,3}(G\d{2,3})?(KT|MPS)$/,
    needles: ['windDirection', 'windSpeed', 'AerodromeSurfaceWind'],
  },
  {
    test: /^(\d{4}|\d{1,2}SM|CAVOK)$/,
    needles: ['prevailingVisibility', 'cloudAndVisibilityOK'],
  },
  {
    test: /^(FEW|SCT|BKN|OVC|NSC|NCD|VV)/,
    needles: ['CloudLayer', 'cloudBase', 'cloud'],
  },
  { test: /^M?\d{2}\/M?\d{2}$/, needles: ['airTemperature', 'dewpointTemperature'] },
  { test: /^[QA]\d{3,4}$/, needles: ['qnh'] },
  { test: /^(NOSIG|BECMG|TEMPO)$/, needles: ['trendForecast', 'changeForecast'] },
];

/**
 * Type `GroupTrace`.
 * @example
 * const _ = true;
 */
export interface GroupTrace {
  start: number;
  end: number;
  token: string;
  element: string;
  occurrence: number;
  scope: 'line' | 'block';
}

/**
 * Keep pairing rows the preview can mark. Drop anything else.
 *
 * @param payload - Convert response, which may omit the pairing
 * @returns Rows with offsets, an element name, and a scope
 * @example
 * const _ = true;
 */
export function readGroupTrace(payload: { group_trace?: unknown }): GroupTrace[] {
  if (!Array.isArray(payload.group_trace)) {
    return [];
  }
  const rows: GroupTrace[] = [];
  for (const item of payload.group_trace) {
    if (!item || typeof item !== 'object') {
      continue;
    }
    const row = item as Partial<GroupTrace>;
    if (
      typeof row.start !== 'number' ||
      typeof row.end !== 'number' ||
      typeof row.token !== 'string' ||
      typeof row.element !== 'string' ||
      typeof row.occurrence !== 'number' ||
      (row.scope !== 'line' && row.scope !== 'block')
    ) {
      continue;
    }
    rows.push({
      start: row.start,
      end: row.end,
      token: row.token,
      element: row.element,
      occurrence: row.occurrence,
      scope: row.scope,
    });
  }
  return rows;
}

/**
 * Opening-tag pattern for an element local name.
 *
 * @param element - Local element name
 * @returns Regular expression source
 * @example
 * const _ = true;
 */
function elementPattern(element: string): string {
  return `<(?:[A-Za-z0-9]+:)?${element.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}(?=[\\s>/])`;
}

/**
 * 1-based lines for one emitted element.
 *
 * @param xml - Pretty-printed preview XML
 * @param element - Local element name
 * @param occurrence - Zero-based count among elements of that name
 * @param scope - Opening line, or the whole element
 * @returns Line numbers to highlight
 * @example
 * const _ = true;
 */
export function xmlLinesForElement(
  xml: string,
  element: string,
  occurrence: number,
  scope: 'line' | 'block',
): number[] {
  if (!xml.trim() || !element || occurrence < 0) {
    return [];
  }
  const open = new RegExp(elementPattern(element), 'g');
  const lines = xml.split('\n');
  let seen = 0;
  for (const [index, line] of lines.entries()) {
    const opens = line.match(open);
    if (!opens) {
      continue;
    }
    for (let nth = 0; nth < opens.length; nth += 1) {
      if (seen !== occurrence) {
        seen += 1;
        continue;
      }
      if (scope === 'line') {
        return [index + 1];
      }
      return elementBlock(lines, index, element);
    }
  }
  return [];
}

/**
 * Lines from an opening tag through its closing tag.
 *
 * @param lines - Preview XML split into lines
 * @param start - Zero-based line of the opening tag
 * @param element - Local element name
 * @returns 1-based line numbers
 * @example
 * const _ = true;
 */
function elementBlock(lines: string[], start: number, element: string): number[] {
  const open = new RegExp(elementPattern(element), 'g');
  const close = new RegExp(
    `</(?:[A-Za-z0-9]+:)?${element.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}>`,
    'g',
  );
  const selfClose = new RegExp(`${elementPattern(element)}[^>]*/>`);
  const hits: number[] = [];
  let depth = 0;
  for (const [index, line] of lines.entries()) {
    if (index < start) {
      continue;
    }
    hits.push(index + 1);
    const opens = line.match(open)?.length ?? 0;
    const closes = line.match(close)?.length ?? 0;
    const selves = line.match(new RegExp(selfClose.source, 'g'))?.length ?? 0;
    depth += opens - selves - closes;
    if (selves > 0 && opens === selves && closes === 0) {
      return hits;
    }
    if (closes > 0 && depth <= 0) {
      return hits;
    }
  }
  return hits;
}

/**
 * Preview lines for the selected group.
 *
 * Uses the converter pairing when the selected offsets are in it. Otherwise
 * falls back to element-name guesses.
 *
 * @param xml - Pretty-printed preview XML
 * @param token - Selected TAC group
 * @param start - Selected start offset
 * @param end - Selected end offset
 * @param traces - Pairing from the convert preview
 * @returns 1-based line numbers
 * @example
 * const _ = true;
 */
export function xmlLinesForSelection(
  xml: string,
  token: string,
  start: number | undefined,
  end: number | undefined,
  traces: GroupTrace[],
): number[] {
  const rows =
    start === undefined || end === undefined
      ? []
      : traces.filter((row) => row.start === start && row.end === end);
  if (rows.length === 0) {
    return xmlLinesForGroup(xml, token);
  }
  const hits = rows.flatMap((row) =>
    xmlLinesForElement(xml, row.element, row.occurrence, row.scope),
  );
  if (hits.length === 0) {
    return xmlLinesForGroup(xml, token);
  }
  return [...new Set(hits)].sort((left, right) => left - right);
}

/**
 * Preview lines for a selected TAC group.
 *
 * Uses the element names the converter writes for that group. Falls back to
 * the group text when the preview still contains the token itself.
 *
 * @param xml - Pretty-printed preview XML
 * @param token - Selected TAC group
 * @returns 1-based line numbers
 * @example
 * const _ = true;
 */
export function xmlLinesForGroup(xml: string, token: string): number[] {
  const group = token.trim();
  if (!group || !xml.trim()) {
    return [];
  }
  const rule = GROUP_ELEMENTS.find((item) => item.test.test(group));
  if (rule) {
    const hits: number[] = [];
    for (const [index, line] of xml.split('\n').entries()) {
      if (rule.needles.some((needle) => line.includes(needle))) {
        hits.push(index + 1);
      }
    }
    if (hits.length > 0) {
      return hits;
    }
  }
  return xmlLinesMatchingToken(xml, group);
}

/**
 * Drop issue marks that overlap the selection, then append the selection mark.
 * CodeMirror decorations cannot overlap.
 *
 * @param issues - Live lint spans
 * @param selected - Group the operator selected, if any
 * @returns Spans safe to paint together
 * @example
 * const _ = true;
 */
export function spansWithSelection(
  issues: TacSpanMark[],
  selected: LiveTraceTarget | null,
): TacSpanMark[] {
  if (!selected || selected.end <= selected.start) {
    return issues;
  }
  const rest = issues.filter(
    (span) => span.end <= selected.start || span.start >= selected.end,
  );
  return [
    ...rest,
    {
      start: selected.start,
      end: selected.end,
      code: selected.code,
      message: 'Selected group',
      severity: 'selected',
    },
  ];
}

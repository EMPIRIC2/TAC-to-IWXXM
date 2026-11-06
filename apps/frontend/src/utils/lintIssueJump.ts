/**
 * Step through live TAC lint issues and pair them with editor offsets.
 */

/**
 * Lint issue that has a selectable character span.
 * @example
 * const _ = true;
 */
export interface JumpableLintIssue {
  start: number;
  end: number;
  message: string;
  severity: string;
  code?: string;
}

/**
 * Keep issues that can move the editor caret.
 *
 * @param issues - Raw lint issues from the live assist hook
 * @returns Issues with a non-empty span
 * @example
 * const _ = true;
 */
export function jumpableLintIssues(
  issues: Array<{
    start?: number | null;
    end?: number | null;
    message: string;
    severity: string;
    code?: string;
  }>,
): JumpableLintIssue[] {
  const ready: JumpableLintIssue[] = [];
  for (const issue of issues) {
    if (issue.start == null || issue.end == null || issue.end <= issue.start) {
      continue;
    }
    ready.push({
      start: issue.start,
      end: issue.end,
      message: issue.message,
      severity: issue.severity,
      code: issue.code,
    });
  }
  return ready;
}

/**
 * Plain-language severity for an issue button.
 *
 * @param severity - Engine severity token
 * @returns Error, Warning, or Note
 * @example
 * const _ = true;
 */
export function lintSeverityLabel(severity: string): string {
  if (severity === 'error') return 'Error';
  if (severity === 'warning' || severity === 'warn') return 'Warning';
  return 'Note';
}

/**
 * Next index in a circular issue list.
 *
 * @param count - Number of jumpable issues
 * @param index - Current index, or null when none is selected
 * @param delta - +1 or -1
 * @returns Index in range, or 0 when the list is empty
 * @example
 * const _ = true;
 */
export function stepLintIssue(
  count: number,
  index: number | null,
  delta: number,
): number {
  if (count <= 0) return 0;
  if (index === null || index < 0 || index >= count) {
    return delta < 0 ? count - 1 : 0;
  }
  return (index + delta + count) % count;
}

/**
 * Issue selected by Alt+Arrow on the TAC pane.
 *
 * @param event - Key event fields
 * @param issues - Jumpable issues in document order
 * @param index - Current index, or null
 * @returns The issue to select, or null when the key is not a jump
 * @example
 * const _ = true;
 */
export function lintIssueFromKey(
  event: { altKey: boolean; key: string },
  issues: JumpableLintIssue[],
  index: number | null,
): JumpableLintIssue | null {
  if (!event.altKey) return null;
  if (event.key !== 'ArrowDown' && event.key !== 'ArrowUp') return null;
  if (issues.length === 0) return null;
  const next = stepLintIssue(issues.length, index, event.key === 'ArrowUp' ? -1 : 1);
  for (const [position, issue] of issues.entries()) {
    if (position === next && issue) return issue;
  }
  return null;
}

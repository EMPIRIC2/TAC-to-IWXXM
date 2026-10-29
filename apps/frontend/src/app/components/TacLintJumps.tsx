/**
 * Direct jumps for live TAC lint issues (list under the TAC pane).
 */

import { lintSeverityLabel, type JumpableLintIssue } from '/utils/lintIssueJump';

/**
 * Type `TacLintJumpsProps`.
 * @example
 * const _ = true;
 */
export interface TacLintJumpsProps {
  issues: JumpableLintIssue[];
  activeIndex: number | null;
  onSelect: (issue: JumpableLintIssue) => void;
}

/**
 * List rows for jumpable issues, skipping empty slots.
 *
 * @param issues - Jumpable issues
 * @param activeIndex - Selected index, or null
 * @param onSelect - Called with the chosen issue
 * @returns List items
 * @example
 * const _ = true;
 */
function lintJumpItems(
  issues: JumpableLintIssue[],
  activeIndex: number | null,
  onSelect: (issue: JumpableLintIssue) => void,
) {
  const rows = [];
  for (const [index, issue] of issues.entries()) {
    if (!issue) continue;
    rows.push(
      <li key={`${issue.start}-${issue.end}-${issue.message}`}>
        <button
          type="button"
          aria-pressed={activeIndex === index}
          className="rounded px-2 py-0.5 text-left text-xs text-gray-900 dark:text-gray-100"
          onClick={() => onSelect(issue)}
        >
          {lintSeverityLabel(issue.severity)}: {issue.message}
        </button>
      </li>,
    );
  }
  return rows;
}

/**
 * Issue list under the TAC pane. Severity is written out, not colour alone.
 *
 * @param props.issues - Jumpable lint issues
 * @param props.activeIndex - Selected index, or null
 * @param props.onSelect - Called with the chosen issue
 * @example
 * const _ = true;
 */
export function TacLintJumps({ issues, activeIndex, onSelect }: TacLintJumpsProps) {
  if (issues.length === 0) return null;
  return (
    <div className="mt-2" role="group" aria-label="TAC lint issues">
      <ol className="space-y-1">{lintJumpItems(issues, activeIndex, onSelect)}</ol>
    </div>
  );
}

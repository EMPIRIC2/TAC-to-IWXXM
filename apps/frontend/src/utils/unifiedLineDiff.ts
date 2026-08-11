/**
 * Client-side unified line diff for Quality metrics XML panes (F7.q / EV-054).
 *
 * No external npm dependency — LCS over split lines (`D-S063-diff-impl`).
 */

export type UnifiedDiffOp = 'equal' | 'add' | 'remove';

export type UnifiedDiffLine = {
  /** Diff operation for this line. */
  op: UnifiedDiffOp;
  /** Line text without trailing newline. */
  text: string;
  /** 1-based line number in the left (official) text when applicable. */
  leftLine: number | null;
  /** 1-based line number in the right (converted) text when applicable. */
  rightLine: number | null;
};

/**
 * Split text into lines, preserving empty trailing line semantics of `split('\n')`.
 *
 * @param text - Source text
 * @returns Line array
 */
export function splitLines(text: string): string[] {
  if (text.length === 0) {
    return [];
  }
  return text.replace(/\r\n/g, '\n').replace(/\r/g, '\n').split('\n');
}

/**
 * Compute a unified line-oriented diff via longest common subsequence.
 *
 * @param left - Official / reference text
 * @param right - Converted / candidate text
 * @returns Ordered unified diff lines
 */
export function unifiedLineDiff(left: string, right: string): UnifiedDiffLine[] {
  const a = splitLines(left);
  const b = splitLines(right);
  const n = a.length;
  const m = b.length;

  const dp: number[][] = Array.from({ length: n + 1 }, () =>
    Array.from({ length: m + 1 }, () => 0),
  );
  for (let i = n - 1; i >= 0; i -= 1) {
    for (let j = m - 1; j >= 0; j -= 1) {
      if (a[i] === b[j]) {
        dp[i][j] = dp[i + 1][j + 1] + 1;
      } else {
        dp[i][j] = Math.max(dp[i + 1][j], dp[i][j + 1]);
      }
    }
  }

  const out: UnifiedDiffLine[] = [];
  let i = 0;
  let j = 0;
  let leftLine = 1;
  let rightLine = 1;
  while (i < n && j < m) {
    if (a[i] === b[j]) {
      out.push({
        op: 'equal',
        text: a[i] ?? '',
        leftLine,
        rightLine,
      });
      i += 1;
      j += 1;
      leftLine += 1;
      rightLine += 1;
    } else if (dp[i + 1][j] >= dp[i][j + 1]) {
      out.push({
        op: 'remove',
        text: a[i] ?? '',
        leftLine,
        rightLine: null,
      });
      i += 1;
      leftLine += 1;
    } else {
      out.push({
        op: 'add',
        text: b[j] ?? '',
        leftLine: null,
        rightLine,
      });
      j += 1;
      rightLine += 1;
    }
  }
  while (i < n) {
    out.push({
      op: 'remove',
      text: a[i] ?? '',
      leftLine,
      rightLine: null,
    });
    i += 1;
    leftLine += 1;
  }
  while (j < m) {
    out.push({
      op: 'add',
      text: b[j] ?? '',
      leftLine: null,
      rightLine,
    });
    j += 1;
    rightLine += 1;
  }
  return out;
}

/**
 * True when the unified diff has no add/remove operations.
 *
 * @param lines - Diff lines from {@link unifiedLineDiff}
 * @returns Whether left and right are line-equal
 */
export function isUnifiedDiffEmpty(lines: UnifiedDiffLine[]): boolean {
  return lines.every((line) => line.op === 'equal');
}

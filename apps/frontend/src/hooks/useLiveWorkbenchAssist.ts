/**
 * Debounced live lint/decode for the F7 operator workbench (UJ-017 / #694).
 */

import { useCallback, useEffect, useRef, useState } from 'react';
import {
  decodeTac,
  lintTac,
  type DecodeResidual,
  type DecodeSegment,
  type LintFix,
  type LintIssue,
} from '/utils/api';
import {
  LIVE_ASSIST_DEBOUNCE_MS,
  LiveAssistScheduler,
  isAbortError,
} from '/utils/liveAssist';
import type { TacSpanMark } from '/utils/tacEditorSpans';

export interface LiveWorkbenchConsoleLine {
  level: 'info' | 'warn' | 'error';
  source: string;
  message: string;
  at: number;
  /** Optional one-click fix action (e.g. Add `=` for MISSING_TERMINATOR). */
  action?: { id: string; label: string };
}

export interface UseLiveWorkbenchAssistOptions {
  text: string;
  product: string;
  accessToken?: string;
  enabled?: boolean;
  /** When true, also run soft-preview convert (live IWXXM). Default off. */
  liveIwxxm?: boolean;
  liveIwxxmRunner?: (signal: AbortSignal) => Promise<void>;
}

export interface UseLiveWorkbenchAssistResult {
  issueSpans: TacSpanMark[];
  lintIssues: LintIssue[];
  lintFixes: LintFix[];
  decodeSegments: DecodeSegment[];
  decodeResiduals: DecodeResidual[];
  decodeProduct: string | undefined;
  decodeSummary: string;
  loading: boolean;
  consoleLines: LiveWorkbenchConsoleLine[];
  appendConsole: (line: Omit<LiveWorkbenchConsoleLine, 'at'>) => void;
  clearConsole: () => void;
}

/**
 * Schedule lint + decode on text changes (300ms debounce, AbortController).
 *
 * @param options.text - Current TAC editor text
 * @param options.product - Resolved product id
 * @param options.liveIwxxm - Optional live IWXXM path (default off)
 */
export function useLiveWorkbenchAssist({
  text,
  product,
  accessToken,
  enabled = true,
  liveIwxxm = false,
  liveIwxxmRunner,
}: UseLiveWorkbenchAssistOptions): UseLiveWorkbenchAssistResult {
  const [issueSpans, setIssueSpans] = useState<TacSpanMark[]>([]);
  const [lintIssues, setLintIssues] = useState<LintIssue[]>([]);
  const [lintFixes, setLintFixes] = useState<LintFix[]>([]);
  const [decodeSegments, setDecodeSegments] = useState<DecodeSegment[]>([]);
  const [decodeResiduals, setDecodeResiduals] = useState<DecodeResidual[]>([]);
  const [decodeProduct, setDecodeProduct] = useState<string | undefined>();
  const [decodeSummary, setDecodeSummary] = useState('');
  const [loading, setLoading] = useState(false);
  const [consoleLines, setConsoleLines] = useState<LiveWorkbenchConsoleLine[]>([]);

  const schedulerRef = useRef<LiveAssistScheduler | null>(null);
  if (schedulerRef.current === null) {
    schedulerRef.current = new LiveAssistScheduler(LIVE_ASSIST_DEBOUNCE_MS);
  }

  const liveIwxxmRunnerRef = useRef(liveIwxxmRunner);
  liveIwxxmRunnerRef.current = liveIwxxmRunner;

  const appendConsole = useCallback((line: Omit<LiveWorkbenchConsoleLine, 'at'>) => {
    setConsoleLines((prev) => [...prev.slice(-199), { ...line, at: Date.now() }]);
  }, []);

  const clearConsole = useCallback(() => setConsoleLines([]), []);

  useEffect(() => {
    const scheduler = schedulerRef.current;
    if (!scheduler) {
      return;
    }

    if (!enabled || !text.trim()) {
      scheduler.cancel();
      setIssueSpans([]);
      setLintIssues([]);
      setLintFixes([]);
      setDecodeSegments([]);
      setDecodeResiduals([]);
      setDecodeProduct(undefined);
      setDecodeSummary('');
      setLoading(false);
      return;
    }

    setLoading(true);
    scheduler.schedule(async (signal) => {
      try {
        const [lintResult, decodeResult] = await Promise.all([
          lintTac({
            manualText: text,
            product,
            accessToken,
            signal,
          }),
          decodeTac({
            manualText: text,
            product,
            accessToken,
            signal,
          }),
        ]);

        if (signal.aborted) {
          return;
        }

        const spans: TacSpanMark[] = lintResult.issues
          .filter(
            (i): i is LintIssue & { start: number; end: number } =>
              typeof i.start === 'number' && typeof i.end === 'number',
          )
          .map((i) => ({
            start: i.start,
            end: i.end,
            message: i.message,
            severity: i.severity,
            code: i.code,
          }));

        const fixes = lintResult.fixes ?? [];
        setLintIssues(lintResult.issues);
        setLintFixes(fixes);
        const fixByCode = new Map(fixes.map((f) => [f.code, f]));
        const spansWithFixes: TacSpanMark[] = spans.map((span) => {
          if (span.code === 'MISSING_TERMINATOR' && fixByCode.has('add_terminator')) {
            return {
              ...span,
              fixCode: 'add_terminator',
              fixLabel: 'Add `=`',
            };
          }
          return span;
        });
        setIssueSpans(spansWithFixes);
        setDecodeSegments(decodeResult.segments);
        setDecodeResiduals(decodeResult.residuals);
        setDecodeProduct(decodeResult.product);
        setDecodeSummary(decodeResult.summary ?? '');

        const summaryLevel = lintResult.ok ? 'info' : 'warn';
        const nextLines: LiveWorkbenchConsoleLine[] = [
          {
            level: summaryLevel,
            source: 'lint-tac',
            message: lintResult.ok
              ? `ok (${lintResult.issues.length} messages)`
              : `${lintResult.issues.length} issue(s)`,
            at: Date.now(),
          },
        ];
        // EV-040 / F10: one console line per issue (no truncated "+N more" summary).
        for (const issue of lintResult.issues) {
          const code = issue.code ? `[${issue.code}] ` : '';
          const level =
            issue.severity === 'error'
              ? 'error'
              : issue.severity === 'warning' || issue.severity === 'warn'
                ? 'warn'
                : 'info';
          if (issue.code === 'MISSING_TERMINATOR' && fixByCode.has('add_terminator')) {
            nextLines.push({
              level: 'info',
              source: 'lint-tac',
              message: `${code}${issue.message}`,
              at: Date.now(),
              action: { id: 'add_terminator', label: 'Add `=`' },
            });
          } else {
            nextLines.push({
              level,
              source: 'lint-tac',
              message: `${code}${issue.message}`,
              at: Date.now(),
            });
          }
        }
        setConsoleLines((prev) => [
          ...prev.slice(-200 + nextLines.length),
          ...nextLines,
        ]);

        if (liveIwxxm && liveIwxxmRunnerRef.current) {
          await liveIwxxmRunnerRef.current(signal);
        }
      } catch (err) {
        if (isAbortError(err) || signal.aborted) {
          return;
        }
        setConsoleLines((prev) => [
          ...prev.slice(-198),
          {
            level: 'error',
            source: 'live-assist',
            message: err instanceof Error ? err.message : 'Live assist failed',
            at: Date.now(),
          },
        ]);
      } finally {
        if (!signal.aborted) {
          setLoading(false);
        }
      }
    });

    return () => {
      scheduler.cancel();
    };
  }, [text, product, accessToken, enabled, liveIwxxm]);

  return {
    issueSpans,
    lintIssues,
    lintFixes,
    decodeSegments,
    decodeResiduals,
    decodeProduct,
    decodeSummary,
    loading,
    consoleLines,
    appendConsole,
    clearConsole,
  };
}

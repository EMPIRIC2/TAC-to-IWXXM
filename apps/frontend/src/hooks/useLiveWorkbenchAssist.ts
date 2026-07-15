/**
 * Debounced live lint/decode for the F7 operator workbench (UJ-017 / #694).
 */

import { useCallback, useEffect, useRef, useState } from 'react';
import {
  decodeTac,
  lintTac,
  type DecodeResidual,
  type DecodeSegment,
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
  decodeSegments: DecodeSegment[];
  decodeResiduals: DecodeResidual[];
  decodeProduct: string | undefined;
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
  const [decodeSegments, setDecodeSegments] = useState<DecodeSegment[]>([]);
  const [decodeResiduals, setDecodeResiduals] = useState<DecodeResidual[]>([]);
  const [decodeProduct, setDecodeProduct] = useState<string | undefined>();
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
      setDecodeSegments([]);
      setDecodeResiduals([]);
      setDecodeProduct(undefined);
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

        setLintIssues(lintResult.issues);
        setIssueSpans(spans);
        setDecodeSegments(decodeResult.segments);
        setDecodeResiduals(decodeResult.residuals);
        setDecodeProduct(decodeResult.product);

        const summaryLevel = lintResult.ok ? 'info' : 'warn';
        const issuePreview = lintResult.issues
          .slice(0, 3)
          .map((i) => {
            const code = i.code ? `[${i.code}] ` : '';
            return `${code}${i.message}`;
          })
          .join('; ');
        const more =
          lintResult.issues.length > 3
            ? ` (+${lintResult.issues.length - 3} more)`
            : '';
        setConsoleLines((prev) => [
          ...prev.slice(-198),
          {
            level: summaryLevel,
            source: 'lint-tac',
            message: lintResult.ok
              ? `ok (${lintResult.issues.length} messages)`
              : lintResult.issues.length === 0
                ? '0 issue(s)'
                : `${lintResult.issues.length} issue(s): ${issuePreview}${more}`,
            at: Date.now(),
          },
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
    decodeSegments,
    decodeResiduals,
    decodeProduct,
    loading,
    consoleLines,
    appendConsole,
    clearConsole,
  };
}

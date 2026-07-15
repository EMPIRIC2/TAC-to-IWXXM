/**
 * Distinct Failed-TAC visual cue for soft-preview / partial convert (UJ-016 / #665).
 */

export interface FailedSpanView {
  start: number;
  end: number;
  code?: string;
  message?: string;
}

export interface FailedTacCueProps {
  failedSpans: FailedSpanView[];
}

/**
 * Surface soft-preview failed spans as a status cue distinct from toast errors.
 *
 * @param props.failedSpans - Character spans from convert ``failed_spans``
 */
export function FailedTacCue({ failedSpans }: FailedTacCueProps) {
  if (!failedSpans.length) {
    return null;
  }

  const primary = failedSpans[0];
  const extra = failedSpans.length > 1 ? failedSpans.length : null;

  return (
    <div
      data-testid="failed-tac-cue"
      role="status"
      className="mb-3 rounded-md border border-rose-400 bg-rose-50 px-3 py-2 text-sm text-rose-950 dark:border-rose-700 dark:bg-rose-950/50 dark:text-rose-100"
    >
      <p className="font-semibold">
        Failed-TAC
        {extra != null ? (
          <span className="ml-1 font-normal">({extra} spans)</span>
        ) : null}
      </p>
      {primary.code ? (
        <p className="mt-1 font-mono text-xs opacity-90">{primary.code}</p>
      ) : null}
      {primary.message ? (
        <p className="mt-0.5 text-xs opacity-90">{primary.message}</p>
      ) : null}
      <p className="mt-1 text-xs opacity-80">
        Soft-preview only — not a Schematron-passed publish.
      </p>
    </div>
  );
}

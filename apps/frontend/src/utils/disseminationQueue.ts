/**
 * Interleaved dissemination queue (F16 / EV-018 / E18-10/11/15).
 *
 * For each selected candidate: preflight → (optional) send → next.
 * Continues after failures and aggregates per-file results.
 */

import {
  isPreflightGreen,
  type PreflightResponse,
  type SendResponse,
  type SinkType,
} from './dissemination';
import type { ExportCandidate } from './exportSelection';

/** Queue run mode — Disseminate vs Preflight only (E18-15). */
export type DisseminationQueueMode = 'disseminate' | 'preflight_only';

/** Sink params held in memory for the queue run (BYOC; never persisted). */
export interface QueueSinkContext {
  sinkType: SinkType;
  uri?: string | null;
  ddl?: boolean;
  product?: string | null;
  iwxxmVersion?: string | null;
  params?: Record<string, unknown>;
}

/** Per-file terminal or in-progress phase. */
export type DisseminationPhase = 'preflight' | 'send';

/** Aggregated per-file outcome. */
export interface DisseminationFileResult {
  candidateId: string;
  status: 'success' | 'failed' | 'skipped';
  phase: DisseminationPhase;
  detail?: string;
  preflight?: PreflightResponse;
  send?: SendResponse;
}

/** Live progress while a file is in flight. */
export interface DisseminationProgressEvent {
  type: 'progress';
  candidateId: string;
  phase: DisseminationPhase;
}

/** Terminal event for one file. */
export interface DisseminationFileDoneEvent {
  type: 'file_done';
  result: DisseminationFileResult;
}

export type DisseminationQueueEvent =
  | DisseminationProgressEvent
  | DisseminationFileDoneEvent;

export type PreflightFn = (
  candidate: ExportCandidate,
  sink: QueueSinkContext,
) => Promise<PreflightResponse>;

export type SendFn = (
  candidate: ExportCandidate,
  handle: string,
  sink: QueueSinkContext,
) => Promise<SendResponse>;

export interface RunDisseminationQueueOptions {
  candidates: readonly ExportCandidate[];
  mode: DisseminationQueueMode;
  sink: QueueSinkContext;
  preflight: PreflightFn;
  send: SendFn;
}

/**
 * Run interleaved preflight→send (or preflight-only) across candidates.
 *
 * Yields progress and file_done events. Never stops the loop on a single failure
 * (E18-11).
 *
 * @param options - Candidates, mode, sink context, and injectable API fns
 * @yields Progress and per-file done events
 */
export async function* runDisseminationQueue(
  options: RunDisseminationQueueOptions,
): AsyncGenerator<DisseminationQueueEvent> {
  const { candidates, mode, sink, preflight, send } = options;

  for (const candidate of candidates) {
    yield { type: 'progress', candidateId: candidate.id, phase: 'preflight' };

    let pre: PreflightResponse;
    try {
      pre = await preflight(candidate, sink);
    } catch (err) {
      yield {
        type: 'file_done',
        result: {
          candidateId: candidate.id,
          status: 'failed',
          phase: 'preflight',
          detail: err instanceof Error ? err.message : String(err),
        },
      };
      continue;
    }

    if (!isPreflightGreen(pre)) {
      yield {
        type: 'file_done',
        result: {
          candidateId: candidate.id,
          status: 'failed',
          phase: 'preflight',
          detail: pre.detail ?? 'Preflight not green',
          preflight: pre,
        },
      };
      continue;
    }

    if (mode === 'preflight_only') {
      yield {
        type: 'file_done',
        result: {
          candidateId: candidate.id,
          status: 'success',
          phase: 'preflight',
          preflight: pre,
        },
      };
      continue;
    }

    // isPreflightGreen already requires a non-empty handle.
    const handle = pre.handle!;

    yield { type: 'progress', candidateId: candidate.id, phase: 'send' };

    try {
      const sendRes = await send(candidate, handle, sink);
      if (!sendRes.ok) {
        yield {
          type: 'file_done',
          result: {
            candidateId: candidate.id,
            status: 'failed',
            phase: 'send',
            detail: sendRes.detail ?? 'Send failed',
            preflight: pre,
            send: sendRes,
          },
        };
        continue;
      }
      yield {
        type: 'file_done',
        result: {
          candidateId: candidate.id,
          status: 'success',
          phase: 'send',
          preflight: pre,
          send: sendRes,
        },
      };
    } catch (err) {
      yield {
        type: 'file_done',
        result: {
          candidateId: candidate.id,
          status: 'failed',
          phase: 'send',
          detail: err instanceof Error ? err.message : String(err),
          preflight: pre,
        },
      };
    }
  }
}

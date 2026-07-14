/**
 * Debounced live-assist scheduler with AbortController cancellation (UJ-017 / #694).
 *
 * Used by the F7 workbench for lint/decode (and optional live IWXXM) so rapid
 * keystrokes coalesce to one request and prior in-flight fetches abort.
 */

/** Debounce window for live lint/decode (04 Batch 1 A). */
export const LIVE_ASSIST_DEBOUNCE_MS = 300;

export type LiveAssistRunner = (signal: AbortSignal) => Promise<void>;

/**
 * Schedules work after {@link LIVE_ASSIST_DEBOUNCE_MS}, aborting any previous
 * timer and in-flight AbortController when rescheduled.
 */
export class LiveAssistScheduler {
  private timer: ReturnType<typeof setTimeout> | null = null;
  private controller: AbortController | null = null;
  private readonly debounceMs: number;

  constructor(debounceMs: number = LIVE_ASSIST_DEBOUNCE_MS) {
    this.debounceMs = debounceMs;
  }

  /**
   * Queue a runner. Resets the debounce timer and aborts the previous request.
   *
   * @param runner - Async work that must honor ``signal.aborted``
   */
  schedule(runner: LiveAssistRunner): void {
    this.cancelPending();
    this.timer = setTimeout(() => {
      this.timer = null;
      const controller = new AbortController();
      this.controller = controller;
      void runner(controller.signal).catch((err: unknown) => {
        if (isAbortError(err) || controller.signal.aborted) {
          return;
        }
        throw err;
      });
    }, this.debounceMs);
  }

  /**
   * Clear the debounce timer and abort any in-flight request.
   */
  cancel(): void {
    this.cancelPending();
  }

  /**
   * Whether a debounce timer is waiting (not yet fired).
   */
  get isPending(): boolean {
    return this.timer !== null;
  }

  /**
   * Active AbortController for the in-flight run, if any.
   */
  get activeController(): AbortController | null {
    return this.controller;
  }

  private cancelPending(): void {
    if (this.timer !== null) {
      clearTimeout(this.timer);
      this.timer = null;
    }
    if (this.controller !== null) {
      this.controller.abort();
      this.controller = null;
    }
  }
}

/**
 * @param err - Caught rejection from fetch/runner
 * @returns True when the error is an abort
 */
export function isAbortError(err: unknown): boolean {
  if (err instanceof DOMException && err.name === 'AbortError') {
    return true;
  }
  if (err instanceof Error && err.name === 'AbortError') {
    return true;
  }
  return false;
}

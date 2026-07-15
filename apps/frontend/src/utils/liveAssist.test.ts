/**
 * T4.1 — Debounce 300ms + AbortController cancels in-flight (UJ-017 / TC-F7-004).
 */

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import {
  LIVE_ASSIST_DEBOUNCE_MS,
  LiveAssistScheduler,
  isAbortError,
} from './liveAssist';

describe('LiveAssistScheduler (T4.1 / UJ-017)', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('exports a 300ms debounce constant', () => {
    expect(LIVE_ASSIST_DEBOUNCE_MS).toBe(300);
  });

  it('does not run the runner until the debounce window elapses', () => {
    const scheduler = new LiveAssistScheduler();
    const runner = vi.fn().mockResolvedValue(undefined);

    scheduler.schedule(runner);
    expect(runner).not.toHaveBeenCalled();
    expect(scheduler.isPending).toBe(true);

    vi.advanceTimersByTime(LIVE_ASSIST_DEBOUNCE_MS - 1);
    expect(runner).not.toHaveBeenCalled();

    vi.advanceTimersByTime(1);
    expect(runner).toHaveBeenCalledTimes(1);
    expect(scheduler.isPending).toBe(false);
  });

  it('coalesces rapid schedule calls into a single run after 300ms', () => {
    const scheduler = new LiveAssistScheduler();
    const runner = vi.fn().mockResolvedValue(undefined);

    scheduler.schedule(runner);
    vi.advanceTimersByTime(100);
    scheduler.schedule(runner);
    vi.advanceTimersByTime(100);
    scheduler.schedule(runner);

    expect(runner).not.toHaveBeenCalled();
    vi.advanceTimersByTime(LIVE_ASSIST_DEBOUNCE_MS);
    expect(runner).toHaveBeenCalledTimes(1);
  });

  it('aborts the in-flight AbortController when rescheduled after fire', async () => {
    const scheduler = new LiveAssistScheduler();
    let firstSignal: AbortSignal | undefined;
    let resolveFirst: (() => void) | undefined;

    const first = vi.fn(
      (signal: AbortSignal) =>
        new Promise<void>((resolve) => {
          firstSignal = signal;
          resolveFirst = resolve;
        }),
    );
    const second = vi.fn().mockResolvedValue(undefined);

    scheduler.schedule(first);
    vi.advanceTimersByTime(LIVE_ASSIST_DEBOUNCE_MS);
    expect(first).toHaveBeenCalledTimes(1);
    expect(firstSignal?.aborted).toBe(false);

    scheduler.schedule(second);
    expect(firstSignal?.aborted).toBe(true);

    resolveFirst?.();
    vi.advanceTimersByTime(LIVE_ASSIST_DEBOUNCE_MS);
    expect(second).toHaveBeenCalledTimes(1);
    expect(second.mock.calls[0]?.[0]?.aborted).toBe(false);
  });

  it('cancel() clears pending debounce and aborts in-flight', () => {
    const scheduler = new LiveAssistScheduler();
    let signal: AbortSignal | undefined;
    const runner = vi.fn(
      (s: AbortSignal) =>
        new Promise<void>(() => {
          signal = s;
        }),
    );

    scheduler.schedule(runner);
    scheduler.cancel();
    expect(scheduler.isPending).toBe(false);

    vi.advanceTimersByTime(LIVE_ASSIST_DEBOUNCE_MS);
    expect(runner).not.toHaveBeenCalled();

    scheduler.schedule(runner);
    vi.advanceTimersByTime(LIVE_ASSIST_DEBOUNCE_MS);
    expect(runner).toHaveBeenCalledTimes(1);
    scheduler.cancel();
    expect(signal?.aborted).toBe(true);
  });

  it('isAbortError recognizes AbortError', () => {
    expect(isAbortError(new DOMException('Aborted', 'AbortError'))).toBe(true);
    const err = new Error('aborted');
    err.name = 'AbortError';
    expect(isAbortError(err)).toBe(true);
    expect(isAbortError(new Error('network'))).toBe(false);
  });
});

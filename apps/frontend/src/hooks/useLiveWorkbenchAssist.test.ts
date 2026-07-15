/**
 * T4.2/T4.6 — useLiveWorkbenchAssist debounce + lint/decode paths.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { LIVE_ASSIST_DEBOUNCE_MS } from '/utils/liveAssist';

const lintTac = vi.hoisted(() =>
  vi.fn().mockResolvedValue({
    ok: false,
    issues: [
      {
        severity: 'error',
        code: 'demo',
        message: 'bad wind',
        start: 0,
        end: 5,
      },
    ],
    fixes: [],
  }),
);
const decodeTac = vi.hoisted(() =>
  vi.fn().mockResolvedValue({
    product: 'METAR',
    segments: [{ start: 0, end: 5, code: 'METAR', explanation: 'type' }],
    residuals: [],
  }),
);

vi.mock('/utils/api', () => ({
  lintTac,
  decodeTac,
}));

import { useLiveWorkbenchAssist } from './useLiveWorkbenchAssist';

async function flushDebouncedAssist(): Promise<void> {
  await act(async () => {
    await vi.advanceTimersByTimeAsync(LIVE_ASSIST_DEBOUNCE_MS + 5);
  });
  await act(async () => {
    await Promise.resolve();
    await Promise.resolve();
  });
}

describe('useLiveWorkbenchAssist', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    lintTac.mockReset();
    decodeTac.mockReset();
    lintTac.mockResolvedValue({
      ok: false,
      issues: [
        {
          severity: 'error',
          code: 'demo',
          message: 'bad wind',
          start: 0,
          end: 5,
        },
      ],
      fixes: [],
    });
    decodeTac.mockResolvedValue({
      product: 'METAR',
      segments: [{ start: 0, end: 5, code: 'METAR', explanation: 'type' }],
      residuals: [],
    });
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('does not call APIs when text is empty', async () => {
    renderHook(() =>
      useLiveWorkbenchAssist({
        text: '   ',
        product: 'METAR',
        enabled: true,
      }),
    );
    await flushDebouncedAssist();
    expect(lintTac).not.toHaveBeenCalled();
    expect(decodeTac).not.toHaveBeenCalled();
  });

  it('does not call APIs when disabled', async () => {
    renderHook(() =>
      useLiveWorkbenchAssist({
        text: 'METAR KJFK',
        product: 'METAR',
        enabled: false,
      }),
    );
    await flushDebouncedAssist();
    expect(lintTac).not.toHaveBeenCalled();
  });

  it('debounces then fills spans, decode, and console', async () => {
    const { result } = renderHook(() =>
      useLiveWorkbenchAssist({
        text: 'METAR KJFK',
        product: 'METAR',
        accessToken: 'tok',
        enabled: true,
      }),
    );

    expect(lintTac).not.toHaveBeenCalled();
    await flushDebouncedAssist();

    expect(lintTac).toHaveBeenCalled();
    expect(decodeTac).toHaveBeenCalled();
    expect(result.current.issueSpans).toEqual([
      {
        start: 0,
        end: 5,
        message: 'bad wind',
        severity: 'error',
        code: 'demo',
      },
    ]);
    expect(result.current.decodeSegments).toHaveLength(1);
    expect(result.current.decodeProduct).toBe('METAR');
    expect(result.current.consoleLines.at(-1)?.source).toBe('lint-tac');
  });

  it('runs liveIwxxmRunner when liveIwxxm is enabled', async () => {
    const runner = vi.fn().mockResolvedValue(undefined);
    renderHook(() =>
      useLiveWorkbenchAssist({
        text: 'METAR KJFK',
        product: 'METAR',
        enabled: true,
        liveIwxxm: true,
        liveIwxxmRunner: runner,
      }),
    );
    await flushDebouncedAssist();
    expect(runner).toHaveBeenCalled();
  });

  it('appendConsole and clearConsole mutate console lines', () => {
    const { result } = renderHook(() =>
      useLiveWorkbenchAssist({
        text: '',
        product: 'METAR',
        enabled: false,
      }),
    );
    act(() => {
      result.current.appendConsole({
        level: 'info',
        source: 'test',
        message: 'hello',
      });
    });
    expect(result.current.consoleLines).toHaveLength(1);
    act(() => {
      result.current.clearConsole();
    });
    expect(result.current.consoleLines).toHaveLength(0);
  });

  it('records console error when lint fails with non-abort error', async () => {
    lintTac.mockRejectedValueOnce(new Error('boom'));
    const { result } = renderHook(() =>
      useLiveWorkbenchAssist({
        text: 'METAR KJFK',
        product: 'METAR',
        enabled: true,
      }),
    );
    await flushDebouncedAssist();
    expect(result.current.consoleLines.some((l) => l.message.includes('boom'))).toBe(
      true,
    );
  });
});

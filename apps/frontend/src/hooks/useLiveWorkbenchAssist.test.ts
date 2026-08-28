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
  fetchSchemaStatus: vi.fn().mockResolvedValue({
    profile_pins: {
      ca_eccc: { extension_bundle_available: true, iwxxm_version: '3.0.0' },
    },
  }),
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

  it('attaches MISSING_TERMINATOR fix affordances and warning/info levels', async () => {
    lintTac.mockResolvedValue({
      ok: true,
      issues: [
        {
          severity: 'warning',
          code: 'MISSING_TERMINATOR',
          message: 'add =',
          start: 0,
          end: 1,
        },
        {
          severity: 'warn',
          code: 'W2',
          message: 'warn alias',
          start: 2,
          end: 3,
        },
        {
          severity: 'info',
          code: 'I1',
          message: 'info only',
        },
      ],
      fixes: [{ code: 'add_terminator', label: 'Add `=`' }],
    });
    decodeTac.mockResolvedValue({
      product: 'METAR',
      segments: [],
      residuals: [],
      summary: 'ok',
    });

    const { result } = renderHook(() =>
      useLiveWorkbenchAssist({
        text: 'METAR KJFK',
        product: 'METAR',
        enabled: true,
      }),
    );
    await flushDebouncedAssist();

    expect(result.current.issueSpans[0]?.fixCode).toBe('add_terminator');
    expect(result.current.decodeSummary).toBe('ok');
    expect(
      result.current.consoleLines.some((l) => l.action?.id === 'add_terminator'),
    ).toBe(true);
    expect(result.current.consoleLines.some((l) => l.level === 'warn')).toBe(true);
    expect(result.current.consoleLines.some((l) => l.level === 'info')).toBe(true);
  });

  it('ignores abort errors and aborted signals without console noise', async () => {
    const abortErr = new DOMException('Aborted', 'AbortError');
    lintTac.mockRejectedValueOnce(abortErr);
    const { result } = renderHook(() =>
      useLiveWorkbenchAssist({
        text: 'METAR KJFK',
        product: 'METAR',
        enabled: true,
      }),
    );
    await flushDebouncedAssist();
    expect(result.current.consoleLines.every((l) => l.source !== 'live-assist')).toBe(
      true,
    );
  });

  it('records non-Error live-assist failures as generic message', async () => {
    lintTac.mockRejectedValueOnce('string-fail');
    const { result } = renderHook(() =>
      useLiveWorkbenchAssist({
        text: 'METAR KJFK',
        product: 'METAR',
        enabled: true,
      }),
    );
    await flushDebouncedAssist();
    expect(
      result.current.consoleLines.some((l) => l.message === 'Live assist failed'),
    ).toBe(true);
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

  it('skips applying results when the request signal aborted mid-flight', async () => {
    let resolveLint: ((v: unknown) => void) | undefined;
    lintTac.mockImplementation(
      () =>
        new Promise((resolve) => {
          resolveLint = resolve;
        }),
    );
    const { unmount, result } = renderHook(() =>
      useLiveWorkbenchAssist({
        text: 'METAR KJFK',
        product: 'METAR',
        enabled: true,
      }),
    );
    await act(async () => {
      await vi.advanceTimersByTimeAsync(LIVE_ASSIST_DEBOUNCE_MS + 5);
    });
    unmount();
    resolveLint?.({
      ok: true,
      issues: [{ severity: 'error', code: 'x', message: 'late', start: 0, end: 1 }],
      fixes: [],
    });
    await act(async () => {
      await Promise.resolve();
      await Promise.resolve();
    });
    expect(result.current.issueSpans).toEqual([]);
  });

  it('handles missing fixes array and issues without codes', async () => {
    lintTac.mockResolvedValue({
      ok: true,
      issues: [{ severity: 'info', message: 'no code here', start: 0, end: 1 }],
    });
    const { result } = renderHook(() =>
      useLiveWorkbenchAssist({
        text: 'METAR KJFK',
        product: 'METAR',
        enabled: true,
      }),
    );
    await flushDebouncedAssist();
    expect(result.current.lintFixes).toEqual([]);
    expect(result.current.consoleLines.some((l) => l.message === 'no code here')).toBe(
      true,
    );
  });
});

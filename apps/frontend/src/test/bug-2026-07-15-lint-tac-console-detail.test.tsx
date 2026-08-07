/**
 * BUG-2026-07-15 — lint-tac console must show issue detail, not only a count.
 *
 * Report: docs/bug-reports/BUG-2026-07-15-empty-bearer-lint-tac.md
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { LIVE_ASSIST_DEBOUNCE_MS } from '@/utils/liveAssist';

const lintTac = vi.hoisted(() =>
  vi.fn().mockResolvedValue({
    ok: false,
    issues: [
      {
        severity: 'error',
        code: 'TAC_PARSE',
        message: 'Unrecognized group fjgfjf',
        start: 0,
        end: 6,
      },
    ],
    fixes: [],
  }),
);
const decodeTac = vi.hoisted(() =>
  vi.fn().mockResolvedValue({
    product: 'METAR',
    segments: [],
    residuals: [],
  }),
);

vi.mock('/utils/api', () => ({
  lintTac,
  decodeTac,
}));

import { useLiveWorkbenchAssist } from '@/hooks/useLiveWorkbenchAssist';

async function flushDebouncedAssist(): Promise<void> {
  await act(async () => {
    await vi.advanceTimersByTimeAsync(LIVE_ASSIST_DEBOUNCE_MS + 5);
  });
  await act(async () => {
    await Promise.resolve();
    await Promise.resolve();
  });
}

describe('BUG-2026-07-15 descriptive lint-tac console', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    lintTac.mockClear();
    decodeTac.mockClear();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('console line includes lint issue message (not only issue count)', async () => {
    const { result } = renderHook(() =>
      useLiveWorkbenchAssist({
        text: 'fjgfjf',
        product: 'METAR',
        accessToken: 'tok',
        enabled: true,
      }),
    );

    await flushDebouncedAssist();

    const lines = result.current.consoleLines.filter((l) => l.source === 'lint-tac');
    expect(lines.some((l) => l.message === '1 issue(s)')).toBe(true);
    expect(
      lines.some((l) => /Unrecognized group fjgfjf|TAC_PARSE/.test(l.message)),
    ).toBe(true);
    expect(lines.every((l) => !l.message.includes('more)'))).toBe(true);
  });

  it('EV-040: emits one console line per lint issue (no +N more truncation)', async () => {
    lintTac.mockResolvedValueOnce({
      ok: false,
      issues: [
        { severity: 'error', code: 'A', message: 'first', start: 0, end: 1 },
        { severity: 'info', code: 'B', message: 'second', start: 2, end: 3 },
        { severity: 'info', code: 'C', message: 'third', start: 4, end: 5 },
        { severity: 'info', code: 'D', message: 'fourth', start: 6, end: 7 },
      ],
      fixes: [],
    });
    const { result } = renderHook(() =>
      useLiveWorkbenchAssist({
        text: 'METAR KJFK 010000Z 00000KT 10SM SKC 10/00 A2992=',
        product: 'METAR',
        accessToken: 'tok',
        enabled: true,
      }),
    );
    await flushDebouncedAssist();
    const detail = result.current.consoleLines.filter(
      (l) => l.source === 'lint-tac' && l.message.includes('['),
    );
    expect(detail).toHaveLength(4);
    expect(detail.map((l) => l.message).join('\n')).not.toMatch(/\(\+\d+ more\)/);
  });
});

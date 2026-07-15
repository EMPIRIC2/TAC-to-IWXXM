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

    const last = result.current.consoleLines.at(-1);
    expect(last?.source).toBe('lint-tac');
    expect(last?.message).toContain('1 issue(s):');
    expect(last?.message).toMatch(/Unrecognized group fjgfjf|TAC_PARSE/);
    expect(last?.message).not.toBe('1 issue(s)');
  });
});

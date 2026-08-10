/**
 * Coverage for useLintIssueCatalog hook (F15 / E11-31).
 */

import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { useLintIssueCatalog } from './useLintIssueCatalog';

const fetchLintIssueCatalog = vi.fn();

vi.mock('@/utils/api', () => ({
  fetchLintIssueCatalog: (...args: unknown[]) => fetchLintIssueCatalog(...args),
}));

describe('useLintIssueCatalog', () => {
  beforeEach(() => {
    fetchLintIssueCatalog.mockReset();
    fetchLintIssueCatalog.mockResolvedValue({
      issues: [
        {
          code: 'MISSING_TERMINATOR',
          severity: 'info',
          message_template: "end with '='",
          product: null,
          tags: ['terminator'],
        },
      ],
    });
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('loads catalog entries and indexes by code', async () => {
    const { result } = renderHook(() =>
      useLintIssueCatalog({ product: 'metar', accessToken: 'tok' }),
    );
    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });
    expect(result.current.entries).toHaveLength(1);
    expect(result.current.byCode.get('MISSING_TERMINATOR')?.severity).toBe('info');
    expect(fetchLintIssueCatalog).toHaveBeenCalled();
  });

  it('surfaces fetch errors', async () => {
    fetchLintIssueCatalog.mockRejectedValueOnce(new Error('boom'));
    const { result } = renderHook(() => useLintIssueCatalog({ accessToken: 'tok' }));
    await waitFor(() => {
      expect(result.current.error).toBe('boom');
    });
    expect(result.current.entries).toEqual([]);
  });

  it('skips fetch when disabled', async () => {
    const { result } = renderHook(() => useLintIssueCatalog({ enabled: false }));
    expect(result.current.loading).toBe(false);
    expect(fetchLintIssueCatalog).not.toHaveBeenCalled();
  });

  it('ignores errors after the hook unmounts', async () => {
    fetchLintIssueCatalog.mockImplementation(
      ({ signal }) =>
        new Promise((_resolve, reject) => {
          const timer = window.setTimeout(() => reject(new Error('boom')), 0);
          signal?.addEventListener('abort', () => {
            window.clearTimeout(timer);
            reject(new Error('aborted'));
          });
        }),
    );
    const { result, unmount } = renderHook(() =>
      useLintIssueCatalog({ accessToken: 'tok' }),
    );
    expect(result.current.loading).toBe(true);
    unmount();
    await waitFor(() => {
      expect(result.current.error).toBeNull();
    });
  });

  it('uses a generic message for non-Error fetch failures', async () => {
    fetchLintIssueCatalog.mockRejectedValueOnce('offline');
    const { result } = renderHook(() => useLintIssueCatalog({ accessToken: 'tok' }));
    await waitFor(() => {
      expect(result.current.error).toBe('Catalog load failed');
    });
  });
});

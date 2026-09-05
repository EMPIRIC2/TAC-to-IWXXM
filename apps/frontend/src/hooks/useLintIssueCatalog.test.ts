/**
 * TC-EV1120-009 — workbench catalog follows Profile / Exchange selections.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';

const fetchLintIssueCatalog = vi.hoisted(() =>
  vi.fn().mockResolvedValue({
    issues: [
      {
        code: 'MISSING_TERMINATOR',
        severity: 'info',
        message_template: "Reports end with '='",
        product: null,
        tags: ['terminator'],
      },
    ],
  }),
);

vi.mock('@/utils/api', () => ({
  fetchLintIssueCatalog,
}));

import { useLintIssueCatalog } from './useLintIssueCatalog';

describe('useLintIssueCatalog', () => {
  beforeEach(() => {
    fetchLintIssueCatalog.mockClear();
    fetchLintIssueCatalog.mockResolvedValue({
      issues: [
        {
          code: 'MISSING_TERMINATOR',
          severity: 'info',
          message_template: "Reports end with '='",
          product: null,
          tags: ['terminator'],
        },
      ],
    });
  });

  it('fetches and refetches when profile filters change', async () => {
    const { rerender } = renderHook(
      ({ product, semanticProfile, exchangeProfile }) =>
        useLintIssueCatalog({
          product,
          semanticProfile,
          exchangeProfile,
          enabled: true,
        }),
      {
        initialProps: {
          product: 'TAF',
          semanticProfile: 'US_FAA_NWS',
          exchangeProfile: 'GLOBAL_AFS',
        },
      },
    );

    await waitFor(() => {
      expect(fetchLintIssueCatalog).toHaveBeenCalledWith(
        expect.objectContaining({
          product: 'TAF',
          semantic_profile: 'US_FAA_NWS',
          exchange_profile: 'GLOBAL_AFS',
        }),
      );
    });

    rerender({
      product: 'METAR',
      semanticProfile: 'CA_ECCC',
      exchangeProfile: 'EUR_RODEX',
    });

    await waitFor(() => {
      expect(fetchLintIssueCatalog).toHaveBeenLastCalledWith(
        expect.objectContaining({
          product: 'METAR',
          semantic_profile: 'CA_ECCC',
          exchange_profile: 'EUR_RODEX',
        }),
      );
    });
  });

  it('surfaces a fallback error message when catalog load fails', async () => {
    fetchLintIssueCatalog.mockRejectedValueOnce('boom');

    const { result } = renderHook(() =>
      useLintIssueCatalog({
        product: 'METAR',
        enabled: true,
      }),
    );

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.entries).toEqual([]);
    expect(result.current.error).toBe('Catalog load failed');
  });

  it('surfaces the thrown error message when catalog load fails with an Error', async () => {
    fetchLintIssueCatalog.mockRejectedValueOnce(new Error('catalog exploded'));

    const { result } = renderHook(() =>
      useLintIssueCatalog({
        product: 'METAR',
        enabled: true,
      }),
    );

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.entries).toEqual([]);
    expect(result.current.error).toBe('catalog exploded');
  });

  it('ignores rejected results after unmount aborts the request', async () => {
    let rejectFetch: ((reason?: unknown) => void) | undefined;
    fetchLintIssueCatalog.mockImplementationOnce(
      () =>
        new Promise((_, reject) => {
          rejectFetch = reject;
        }),
    );

    const { unmount } = renderHook(() =>
      useLintIssueCatalog({
        product: 'METAR',
        enabled: true,
      }),
    );

    unmount();
    rejectFetch?.(new Error('late failure'));

    await waitFor(() => {
      expect(fetchLintIssueCatalog).toHaveBeenCalled();
    });
  });
});

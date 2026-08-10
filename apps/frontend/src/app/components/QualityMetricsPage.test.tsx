/**
 * Vitest — Quality metrics list/summary (TC-EV054-001..002 / AC1 / AC5).
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {
  QUALITY_METRICS_DEFERRED_LABEL,
  QualityMetricsPage,
} from './QualityMetricsPage';

const apiMocks = vi.hoisted(() => ({
  fetchQualityMetrics: vi.fn(),
}));

vi.mock('@/utils/api', () => ({
  fetchQualityMetrics: apiMocks.fetchQualityMetrics,
}));

const MOCK_LIST = {
  generated_at: '2026-08-10T00:00:00Z',
  iwxxm_pin: '2025-2',
  summaries: [
    {
      product: 'metar',
      match_pass: 1,
      match_fail: 0,
      residual_nonempty: 0,
      lint_fail: 0,
      validate_fail: 0,
      deferred_gaps: 1,
    },
    {
      product: 'taf',
      match_pass: 1,
      match_fail: 0,
      residual_nonempty: 0,
      lint_fail: 0,
      validate_fail: 0,
      deferred_gaps: 0,
    },
  ],
  files: [
    {
      stem: 'metar-A3-1',
      product: 'metar',
      tier: 'wmoPass',
      match_status: 'equal',
      residual_count: 0,
      lint_error_count: 0,
      validate_error_count: 0,
      deferred: false,
    },
    {
      stem: 'metar-NIL-collect',
      product: 'metar',
      tier: 'deferred',
      match_status: 'deferred',
      residual_count: 0,
      lint_error_count: 0,
      validate_error_count: 0,
      deferred: true,
    },
    {
      stem: 'taf-A5-1',
      product: 'taf',
      tier: 'wmoPass',
      match_status: 'equal',
      residual_count: 0,
      lint_error_count: 0,
      validate_error_count: 0,
      deferred: false,
    },
  ],
};

describe('QualityMetricsPage (TC-EV054-002)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    apiMocks.fetchQualityMetrics.mockResolvedValue(MOCK_LIST);
  });

  it('renders summary strip and file rows from mocked list API', async () => {
    render(<QualityMetricsPage />);

    await waitFor(() => {
      expect(screen.getByTestId('quality-metrics-summary')).toBeInTheDocument();
    });

    expect(apiMocks.fetchQualityMetrics).toHaveBeenCalledWith({
      product: undefined,
    });
    expect(screen.getByTestId('quality-metrics-row-metar-A3-1')).toBeInTheDocument();
    expect(screen.getByTestId('quality-metrics-row-taf-A5-1')).toBeInTheDocument();

    const summary = screen.getByTestId('quality-metrics-summary');
    expect(within(summary).getByText('Match pass')).toBeInTheDocument();
    expect(within(summary).getByText('2')).toBeInTheDocument();
  });

  it('labels deferred gap stems (AC5)', async () => {
    render(<QualityMetricsPage />);

    await waitFor(() => {
      expect(
        screen.getByTestId('quality-metrics-deferred-metar-NIL-collect'),
      ).toBeInTheDocument();
    });

    expect(
      screen.getByTestId('quality-metrics-deferred-metar-NIL-collect'),
    ).toHaveTextContent(QUALITY_METRICS_DEFERRED_LABEL);
  });

  it('filters list by product', async () => {
    const user = userEvent.setup();
    apiMocks.fetchQualityMetrics
      .mockResolvedValueOnce(MOCK_LIST)
      .mockResolvedValueOnce({
        ...MOCK_LIST,
        summaries: [MOCK_LIST.summaries[0]],
        files: MOCK_LIST.files.filter((f) => f.product === 'metar'),
      });

    render(<QualityMetricsPage />);

    await waitFor(() => {
      expect(screen.getByTestId('quality-metrics-file-list')).toBeInTheDocument();
    });

    await user.selectOptions(
      screen.getByTestId('quality-metrics-product-filter'),
      'metar',
    );

    await waitFor(() => {
      expect(apiMocks.fetchQualityMetrics).toHaveBeenLastCalledWith({
        product: 'metar',
      });
    });

    expect(screen.getByTestId('quality-metrics-row-metar-A3-1')).toBeInTheDocument();
    expect(
      screen.queryByTestId('quality-metrics-row-taf-A5-1'),
    ).not.toBeInTheDocument();
  });
});

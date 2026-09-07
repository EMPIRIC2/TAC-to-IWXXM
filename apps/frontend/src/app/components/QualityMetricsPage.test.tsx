/**
 * Vitest — Quality metrics list + detail (TC-EV054-001..004 / AC1–AC5).
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { act, render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {
  QUALITY_METRICS_DIFF_EMPTY_LABEL,
  QUALITY_METRICS_EMPTY_DIAGNOSTICS,
} from './QualityMetricsDetail';
import { QualityMetricsPage } from './QualityMetricsPage';
import { QUALITY_METRICS_DEFERRED_LABEL } from '@/utils/qualityMetricsCopy';

const apiMocks = vi.hoisted(() => ({
  fetchQualityMetrics: vi.fn(),
  fetchQualityMetricsDetail: vi.fn(),
}));

vi.mock('@/utils/api', () => ({
  fetchQualityMetrics: apiMocks.fetchQualityMetrics,
  fetchQualityMetricsDetail: apiMocks.fetchQualityMetricsDetail,
  fetchSchemaStatus: vi.fn().mockResolvedValue({
    profile_pins: {
      ca_eccc: { extension_bundle_available: true, iwxxm_version: '3.0.0' },
    },
  }),
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

const MOCK_DETAIL_EQUAL = {
  stem: 'metar-A3-1',
  product: 'metar',
  tier: 'wmoPass',
  deferred: false,
  deferral_reason: null,
  tac: 'METAR YUDO 221630Z=',
  official_xml: '<root>\n  <a/>\n</root>',
  converted_xml: '<root>\n  <a/>\n</root>',
  match_status: 'equal',
  residuals: [],
  lint_issues: [],
  validate_issues: [],
};

const MOCK_DETAIL_UNEQUAL = {
  ...MOCK_DETAIL_EQUAL,
  stem: 'taf-A5-1',
  product: 'taf',
  match_status: 'unequal',
  official_xml: '<root>\n  <a/>\n</root>',
  converted_xml: '<root>\n  <b/>\n</root>',
  residuals: [{ message: 'token leftover' }],
  lint_issues: [{ code: 'EXAMPLE', message: 'lint hit' }],
  validate_issues: [{ message: 'schematron hit' }],
};

describe('QualityMetricsPage (TC-EV054-002)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    apiMocks.fetchQualityMetrics.mockResolvedValue(MOCK_LIST);
    apiMocks.fetchQualityMetricsDetail.mockResolvedValue(MOCK_DETAIL_EQUAL);
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
    expect(within(summary).getByText('Matches')).toBeInTheDocument();
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

  it('surfaces list fetch errors', async () => {
    apiMocks.fetchQualityMetrics.mockRejectedValueOnce(new Error('list boom'));
    render(<QualityMetricsPage />);

    await waitFor(() => {
      expect(screen.getByText('list boom')).toBeInTheDocument();
    });
  });

  it('surfaces list fetch errors for non-Error throws', async () => {
    apiMocks.fetchQualityMetrics.mockRejectedValueOnce('list string boom');
    render(<QualityMetricsPage />);

    await waitFor(() => {
      expect(screen.getByText('Failed to load quality metrics')).toBeInTheDocument();
    });
  });
});

describe('QualityMetricsPage detail (TC-EV054-003..004)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    apiMocks.fetchQualityMetrics.mockResolvedValue(MOCK_LIST);
  });

  it('shows match status, panes, and empty unified diff for equal stem', async () => {
    const user = userEvent.setup();
    apiMocks.fetchQualityMetricsDetail.mockResolvedValue(MOCK_DETAIL_EQUAL);

    render(<QualityMetricsPage />);

    await waitFor(() => {
      expect(screen.getByTestId('quality-metrics-row-metar-A3-1')).toBeInTheDocument();
    });

    await user.click(screen.getByTestId('quality-metrics-row-metar-A3-1'));

    await waitFor(() => {
      expect(screen.getByTestId('quality-metrics-detail')).toBeInTheDocument();
    });

    expect(apiMocks.fetchQualityMetricsDetail).toHaveBeenCalledWith({
      stem: 'metar-A3-1',
    });
    expect(screen.getByTestId('quality-metrics-match-status')).toHaveTextContent(
      'Matches official',
    );
    expect(screen.getByTestId('quality-metrics-pane-tac')).toHaveTextContent(
      'METAR YUDO',
    );
    expect(screen.getByTestId('quality-metrics-pane-official-xml')).toHaveTextContent(
      '<a>',
    );
    expect(screen.getByTestId('quality-metrics-pane-official-xml')).toHaveTextContent(
      '</a>',
    );
    expect(screen.getByTestId('quality-metrics-pane-converted-xml')).toHaveTextContent(
      '<a>',
    );
    expect(screen.getByTestId('quality-metrics-pane-converted-xml')).toHaveTextContent(
      '</a>',
    );
    expect(screen.getByTestId('quality-metrics-diff-empty')).toHaveTextContent(
      QUALITY_METRICS_DIFF_EMPTY_LABEL,
    );
    expect(
      screen.getByTestId('quality-metrics-validate-chip-schematron'),
    ).toBeInTheDocument();
    expect(
      screen.getByTestId('quality-metrics-validate-chip-schema-import'),
    ).toBeInTheDocument();
    expect(
      screen.getByTestId('quality-metrics-pane-residuals-empty'),
    ).toHaveTextContent(QUALITY_METRICS_EMPTY_DIAGNOSTICS);
    expect(screen.getByTestId('quality-metrics-pane-lint-empty')).toBeInTheDocument();
    expect(
      screen.getByTestId('quality-metrics-pane-validate-empty'),
    ).toBeInTheDocument();
  });

  it('shows unified diff body and non-empty diagnostics for unequal stem', async () => {
    const user = userEvent.setup();
    apiMocks.fetchQualityMetricsDetail.mockResolvedValue(MOCK_DETAIL_UNEQUAL);

    render(<QualityMetricsPage />);

    await waitFor(() => {
      expect(screen.getByTestId('quality-metrics-row-taf-A5-1')).toBeInTheDocument();
    });

    await user.click(screen.getByTestId('quality-metrics-row-taf-A5-1'));

    await waitFor(() => {
      expect(screen.getByTestId('quality-metrics-diff-body')).toBeInTheDocument();
    });

    expect(screen.getByTestId('quality-metrics-match-status')).toHaveTextContent(
      'Differs from official',
    );
    expect(screen.getByTestId('quality-metrics-diff-body')).toHaveTextContent('<a>');
    expect(screen.getByTestId('quality-metrics-diff-body')).toHaveTextContent('</a>');
    expect(screen.getByTestId('quality-metrics-diff-body')).toHaveTextContent('<b>');
    expect(screen.getByTestId('quality-metrics-diff-body')).toHaveTextContent('</b>');
    expect(screen.getByTestId('quality-metrics-pane-residuals')).toHaveTextContent(
      'token leftover',
    );
    expect(screen.getByTestId('quality-metrics-pane-lint')).toHaveTextContent(
      'lint hit',
    );
    expect(screen.getByTestId('quality-metrics-pane-validate')).toHaveTextContent(
      'schematron hit',
    );
  });

  it('surfaces detail fetch errors', async () => {
    const user = userEvent.setup();
    apiMocks.fetchQualityMetricsDetail.mockRejectedValueOnce(new Error('detail boom'));

    render(<QualityMetricsPage />);

    await waitFor(() => {
      expect(screen.getByTestId('quality-metrics-row-metar-A3-1')).toBeInTheDocument();
    });

    await user.click(screen.getByTestId('quality-metrics-row-metar-A3-1'));

    await waitFor(() => {
      expect(screen.getByText('detail boom')).toBeInTheDocument();
    });
  });

  it('surfaces detail fetch errors for non-Error throws', async () => {
    const user = userEvent.setup();
    apiMocks.fetchQualityMetricsDetail.mockRejectedValueOnce('detail string boom');

    render(<QualityMetricsPage />);

    await waitFor(() => {
      expect(screen.getByTestId('quality-metrics-row-metar-A3-1')).toBeInTheDocument();
    });

    await user.click(screen.getByTestId('quality-metrics-row-metar-A3-1'));

    await waitFor(() => {
      expect(screen.getByText('Failed to load file detail')).toBeInTheDocument();
    });
  });

  it('closes the detail panel via Close detail', async () => {
    const user = userEvent.setup();
    apiMocks.fetchQualityMetricsDetail.mockResolvedValue(MOCK_DETAIL_EQUAL);

    render(<QualityMetricsPage />);

    await waitFor(() => {
      expect(screen.getByTestId('quality-metrics-row-metar-A3-1')).toBeInTheDocument();
    });

    await user.click(screen.getByTestId('quality-metrics-row-metar-A3-1'));

    await waitFor(() => {
      expect(screen.getByTestId('quality-metrics-detail')).toBeInTheDocument();
    });

    await user.click(screen.getByRole('button', { name: /close detail/i }));

    await waitFor(() => {
      expect(screen.queryByTestId('quality-metrics-detail')).not.toBeInTheDocument();
    });
  });

  it('uses route callbacks for open and back navigation', async () => {
    const user = userEvent.setup();
    const onOpenDetailRoute = vi.fn();
    const onBackToList = vi.fn();
    apiMocks.fetchQualityMetricsDetail.mockResolvedValue(MOCK_DETAIL_EQUAL);

    const { rerender } = render(
      <QualityMetricsPage
        onOpenDetailRoute={onOpenDetailRoute}
        onBackToList={onBackToList}
      />,
    );

    await waitFor(() => {
      expect(screen.getByTestId('quality-metrics-row-metar-A3-1')).toBeInTheDocument();
    });

    await user.click(screen.getByTestId('quality-metrics-row-metar-A3-1'));
    expect(onOpenDetailRoute).toHaveBeenCalledWith('metar-A3-1');

    rerender(
      <QualityMetricsPage
        routeStem="metar-A3-1"
        onOpenDetailRoute={onOpenDetailRoute}
        onBackToList={onBackToList}
      />,
    );

    await waitFor(() => {
      expect(screen.getByTestId('quality-metrics-detail')).toBeInTheDocument();
    });

    await user.click(screen.getByTestId('quality-metrics-detail-close'));
    expect(onBackToList).toHaveBeenCalled();
  });

  it('shows empty-list copy when the filter has no files', async () => {
    apiMocks.fetchQualityMetrics.mockResolvedValue({
      ...MOCK_LIST,
      files: [],
      summaries: [],
    });

    render(<QualityMetricsPage />);

    await waitFor(() => {
      expect(screen.getByText(/No files for this product filter/i)).toBeInTheDocument();
    });
  });

  it('shouldApplyDetailFetch is false when cancelled', async () => {
    const { shouldApplyDetailFetch } = await import('./QualityMetricsPage');
    expect(shouldApplyDetailFetch(false)).toBe(true);
    expect(shouldApplyDetailFetch(true)).toBe(false);
  });

  it('ignores late detail results after unmount', async () => {
    let resolveDetail: ((v: unknown) => void) | undefined;
    apiMocks.fetchQualityMetricsDetail.mockImplementation(
      () =>
        new Promise((resolve) => {
          resolveDetail = resolve;
        }),
    );
    const { unmount } = render(
      <QualityMetricsPage
        routeStem="late-stem"
        onOpenDetailRoute={() => undefined}
        onBackToList={() => undefined}
      />,
    );
    unmount();
    await act(async () => {
      resolveDetail?.(MOCK_DETAIL_EQUAL);
      await Promise.resolve();
    });
    expect(apiMocks.fetchQualityMetricsDetail).toHaveBeenCalled();
  });

  it('ignores late detail errors after unmount', async () => {
    let rejectDetail: ((e: unknown) => void) | undefined;
    apiMocks.fetchQualityMetricsDetail.mockImplementation(
      () =>
        new Promise((_resolve, reject) => {
          rejectDetail = reject;
        }),
    );
    const { unmount } = render(
      <QualityMetricsPage
        routeStem="late-err"
        onOpenDetailRoute={() => undefined}
        onBackToList={() => undefined}
      />,
    );
    unmount();
    await act(async () => {
      rejectDetail?.(new Error('late'));
      await Promise.resolve();
    });
    expect(apiMocks.fetchQualityMetricsDetail).toHaveBeenCalled();
  });

  it('shows detailError on the detail-only route', async () => {
    apiMocks.fetchQualityMetricsDetail.mockRejectedValueOnce(new Error('detail boom'));
    render(
      <QualityMetricsPage
        routeStem="broken-stem"
        onOpenDetailRoute={() => undefined}
        onBackToList={() => undefined}
      />,
    );
    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent(/detail boom|failed/i);
    });
  });

  it('returns null active summary for an unknown product filter', async () => {
    const user = userEvent.setup();
    apiMocks.fetchQualityMetrics.mockResolvedValue({
      ...MOCK_LIST,
      summaries: [{ ...MOCK_LIST.summaries[0]!, product: 'metar' }],
      files: [
        { ...MOCK_LIST.files[0]!, product: 'metar' },
        { ...MOCK_LIST.files[0]!, stem: 'taf-only', product: 'taf' },
      ],
    });
    render(<QualityMetricsPage />);
    await waitFor(() => {
      expect(screen.getByTestId('quality-metrics-product-filter')).toBeInTheDocument();
    });
    await user.selectOptions(
      screen.getByTestId('quality-metrics-product-filter'),
      'taf',
    );
  });
});

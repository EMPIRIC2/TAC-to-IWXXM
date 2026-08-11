/**
 * Vitest — Quality metrics list + detail (TC-EV054-001..004 / AC1–AC5).
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {
  QUALITY_METRICS_DIFF_EMPTY_LABEL,
  QUALITY_METRICS_EMPTY_DIAGNOSTICS,
} from './QualityMetricsDetail';
import {
  QUALITY_METRICS_DEFERRED_LABEL,
  QualityMetricsPage,
} from './QualityMetricsPage';

const apiMocks = vi.hoisted(() => ({
  fetchQualityMetrics: vi.fn(),
  fetchQualityMetricsDetail: vi.fn(),
}));

vi.mock('@/utils/api', () => ({
  fetchQualityMetrics: apiMocks.fetchQualityMetrics,
  fetchQualityMetricsDetail: apiMocks.fetchQualityMetricsDetail,
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
      'equal',
    );
    expect(screen.getByTestId('quality-metrics-pane-tac')).toHaveTextContent(
      'METAR YUDO',
    );
    expect(screen.getByTestId('quality-metrics-pane-official-xml')).toHaveTextContent(
      '<a></a>',
    );
    expect(screen.getByTestId('quality-metrics-pane-converted-xml')).toHaveTextContent(
      '<a></a>',
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
      'unequal',
    );
    expect(screen.getByTestId('quality-metrics-diff-body')).toHaveTextContent(
      '<a></a>',
    );
    expect(screen.getByTestId('quality-metrics-diff-body')).toHaveTextContent(
      '<b></b>',
    );
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
      expect(screen.getByText('Failed to load stem detail')).toBeInTheDocument();
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
});

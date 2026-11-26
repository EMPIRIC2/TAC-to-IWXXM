/**
 * TC-SH-014 — Station health eval-benchmark panel (FR-047).
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { StationHealthEvalPanel } from './StationHealthEvalPanel';
import { STATION_HEALTH_EVAL_HEADING } from '@/utils/stationHealthCopy';

const fetchStationHealthEvalBenchmark = vi.fn();

vi.mock('@/utils/stationHealthApi', () => ({
  fetchStationHealthEvalBenchmark: (...args: unknown[]) =>
    fetchStationHealthEvalBenchmark(...args),
}));

const SAMPLE = {
  computed_at: '2026-11-26T12:00:00Z',
  window_hours: 24,
  products: ['metar', 'taf'],
  partial_decode_count: 1,
  lint_count: 3,
  top_lint_codes: [{ code: 'INVALID_WIND', count: 2 }],
  convert_failure_count: 2,
  iwxxm_validation: { pass: 10, fail: 2, skip: 1 },
  failure_locations: [],
  product_breakdown: [
    { product: 'metar', failure_count: 2 },
    { product: 'taf', failure_count: 1 },
  ],
  icao_filter: null,
};

describe('StationHealthEvalPanel', () => {
  beforeEach(() => {
    fetchStationHealthEvalBenchmark.mockReset();
  });

  it('S: renders live eval counts from a successful fetch', async () => {
    fetchStationHealthEvalBenchmark.mockResolvedValue(SAMPLE);
    render(<StationHealthEvalPanel />);
    expect(screen.getByText(STATION_HEALTH_EVAL_HEADING)).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByTestId('station-health-eval-stats')).toBeInTheDocument();
    });
    expect(screen.getByTestId('station-health-eval-lint')).toHaveTextContent('3');
    expect(screen.getByTestId('station-health-eval-iwxxm')).toHaveTextContent(
      '10 / 2 / 1',
    );
    expect(screen.getByTestId('station-health-eval-breakdown')).toHaveTextContent(
      'METAR 2',
    );
  });

  it('F: shows an error when the eval-benchmark fetch fails', async () => {
    fetchStationHealthEvalBenchmark.mockRejectedValue(new Error('boom'));
    render(<StationHealthEvalPanel />);
    await waitFor(() => {
      expect(screen.getByTestId('station-health-eval-error')).toBeInTheDocument();
    });
    expect(screen.queryByTestId('station-health-eval-stats')).toBeNull();
  });

  it('V+: accepts a valid empty snapshot body', async () => {
    fetchStationHealthEvalBenchmark.mockResolvedValue({
      ...SAMPLE,
      computed_at: '',
      lint_count: 0,
      convert_failure_count: 0,
      top_lint_codes: [],
      product_breakdown: [],
      products: [],
      iwxxm_validation: { pass: 0, fail: 0, skip: 0 },
    });
    render(<StationHealthEvalPanel />);
    await waitFor(() => {
      expect(screen.getByTestId('station-health-eval-top-codes')).toHaveTextContent(
        'None',
      );
    });
    expect(screen.getByTestId('station-health-eval-computed-at')).toHaveTextContent(
      'No snapshot yet',
    );
  });

  it('ignores AbortError from the eval-benchmark fetch', async () => {
    fetchStationHealthEvalBenchmark.mockImplementation(
      ({ signal }: { signal?: AbortSignal } = {}) =>
        new Promise((_resolve, reject) => {
          signal?.addEventListener('abort', () => {
            reject(new DOMException('Aborted', 'AbortError'));
          });
        }),
    );
    const { unmount } = render(<StationHealthEvalPanel />);
    await waitFor(() => {
      expect(fetchStationHealthEvalBenchmark).toHaveBeenCalled();
    });
    unmount();
    await waitFor(() => {
      expect(screen.queryByTestId('station-health-eval-error')).toBeNull();
    });
  });

  it('renders zero IWXXM counts when validation is missing', async () => {
    fetchStationHealthEvalBenchmark.mockResolvedValue({
      ...SAMPLE,
      iwxxm_validation: undefined,
    });
    render(<StationHealthEvalPanel />);
    await waitFor(() => {
      expect(screen.getByTestId('station-health-eval-iwxxm')).toHaveTextContent(
        '0 / 0 / 0',
      );
    });
  });
});

/**
 * TC-SH-005 — Station health shell page regressions.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { StationHealthPage } from './StationHealthPage';
import { STATION_HEALTH_PAGE_TITLE } from '@/utils/stationHealthCopy';

const fetchStationHealthList = vi.fn();
const fetchStationHealthMetrics = vi.fn();

vi.mock('@/utils/stationHealthApi', () => ({
  fetchStationHealthList: (...args: unknown[]) => fetchStationHealthList(...args),
  fetchStationHealthMetrics: (...args: unknown[]) => fetchStationHealthMetrics(...args),
}));

describe('StationHealthPage', () => {
  beforeEach(() => {
    fetchStationHealthList.mockReset();
    fetchStationHealthMetrics.mockReset();
    fetchStationHealthMetrics.mockResolvedValue({
      metrics: [
        {
          id: 'availability',
          label: 'Availability',
          description: 'Share of expected TAC reports received in the window',
          unit: 'percent',
          higher_is_better: true,
        },
      ],
    });
  });

  it('renders title, summary, and station rows', async () => {
    fetchStationHealthList.mockResolvedValue({
      window: '6h',
      computed_at: '2026-11-13T12:00:00Z',
      stations: [
        {
          icao: 'KJFK',
          name: 'John F Kennedy International',
          overall_grade: 'B',
          overall_score: 84.5,
          products: [
            {
              product: 'metar',
              grade: 'B',
              overall_score: 84.5,
              availability_score: 83.3,
              actual_count: 5,
              expected_count: 6,
              solidus_rate: 0.02,
              missing_digit_rate: 0,
              lint_severity_score: 100,
              lint_error_count: 0,
            },
          ],
        },
      ],
      summary: { station_count: 1, grade_counts: { A: 0, B: 1, C: 0, D: 0, F: 0 } },
    });
    render(<StationHealthPage />);
    expect(screen.getByTestId('station-health-page')).toBeInTheDocument();
    expect(screen.getByText(STATION_HEALTH_PAGE_TITLE)).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByTestId('station-health-row-KJFK')).toBeInTheDocument();
    });
    expect(screen.getByTestId('station-health-grade-count-B')).toHaveTextContent(
      'B: 1',
    );
    expect(
      screen.getByTestId('station-health-metric-availability'),
    ).toBeInTheDocument();
  });

  it('shows empty state when no stations are graded', async () => {
    fetchStationHealthList.mockResolvedValue({
      window: '6h',
      computed_at: '2026-11-13T12:00:00Z',
      stations: [],
      summary: { station_count: 0, grade_counts: { A: 0, B: 0, C: 0, D: 0, F: 0 } },
    });
    render(<StationHealthPage />);
    await waitFor(() => {
      expect(screen.getByTestId('station-health-empty')).toBeInTheDocument();
    });
  });

  it('shows load error when the API fails', async () => {
    fetchStationHealthList.mockRejectedValue(new Error('network'));
    render(<StationHealthPage />);
    await waitFor(() => {
      expect(screen.getByTestId('station-health-error')).toBeInTheDocument();
    });
  });

  it('reloads when window, product, and grade filters change', async () => {
    const user = userEvent.setup();
    fetchStationHealthList.mockResolvedValue({
      window: '6h',
      computed_at: '2026-11-13T12:00:00Z',
      stations: [],
      summary: { station_count: 0, grade_counts: { A: 0, B: 0, C: 0, D: 0, F: 0 } },
    });
    render(<StationHealthPage />);
    await waitFor(() => {
      expect(fetchStationHealthList).toHaveBeenCalled();
    });
    const callsBefore = fetchStationHealthList.mock.calls.length;
    await user.selectOptions(screen.getByTestId('station-health-window'), '1d');
    await user.selectOptions(screen.getByTestId('station-health-product'), 'metar');
    await user.selectOptions(screen.getByTestId('station-health-grade'), 'B');
    await waitFor(() => {
      expect(fetchStationHealthList.mock.calls.length).toBeGreaterThan(callsBefore);
    });
    const last = fetchStationHealthList.mock.calls.at(-1)?.[0] as {
      window?: string;
      product?: string;
      grade?: string;
    };
    expect(last.window).toBe('1d');
    expect(last.product).toBe('metar');
    expect(last.grade).toBe('B');
  });
});

describe('StationHealthPage modes', () => {
  it.each([
    {
      mode: 'success' as const,
      list: {
        window: '6h',
        computed_at: '2026-11-13T12:00:00Z',
        stations: [
          {
            icao: 'KJFK',
            name: 'John F Kennedy International',
            overall_grade: 'A',
            overall_score: 95,
            products: [],
          },
        ],
        summary: { station_count: 1, grade_counts: { A: 1, B: 0, C: 0, D: 0, F: 0 } },
      },
      testId: 'station-health-row-KJFK',
    },
    {
      mode: 'failure' as const,
      reject: true,
      testId: 'station-health-error',
    },
    {
      mode: 'validation' as const,
      list: {
        window: '6h',
        computed_at: '2026-11-13T12:00:00Z',
        stations: [],
        summary: { station_count: 0, grade_counts: { A: 0, B: 0, C: 0, D: 0, F: 0 } },
      },
      testId: 'station-health-empty',
    },
  ])('$mode mode renders $testId', async ({ mode, list, reject, testId }) => {
    void mode;
    if (reject) {
      fetchStationHealthList.mockRejectedValue(new Error('network'));
    } else {
      fetchStationHealthList.mockResolvedValue(list);
    }
    render(<StationHealthPage />);
    await waitFor(() => {
      expect(screen.getByTestId(testId)).toBeInTheDocument();
    });
  });
});

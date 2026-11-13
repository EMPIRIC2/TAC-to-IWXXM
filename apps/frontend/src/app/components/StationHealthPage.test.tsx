/**
 * TC-SH-005 — Station health shell page regressions.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
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
});

import { beforeEach, describe, expect, it, vi } from 'vitest';
import { act, render, screen, waitFor } from '@testing-library/react';

import { AirportDetailsCard } from './AirportDetailsCard';

const mockFetchAirportRegion = vi.hoisted(() =>
  vi.fn().mockResolvedValue({ airport_code: 'KJFK', icao_region: 'K1' }),
);

const realAirportsApi = vi.hoisted(() => ({
  findWhere: (_criteria: { icao?: string }) =>
    undefined as ReturnType<
      typeof import('../../utils/airportsData').airports.findWhere
    >,
  isValid: (_icao: string) => false as boolean,
}));

const mockFindWhere = vi.hoisted(() => vi.fn());
const mockIsValid = vi.hoisted(() => vi.fn());

vi.mock('../../utils/api', () => ({
  fetchAirportRegion: mockFetchAirportRegion,
}));

vi.mock('../../utils/airportsData', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../../utils/airportsData')>();
  realAirportsApi.findWhere = actual.airports.findWhere.bind(actual.airports);
  realAirportsApi.isValid = actual.airports.isValid.bind(actual.airports);
  return {
    ...actual,
    airports: {
      ...actual.airports,
      findWhere: mockFindWhere,
      isValid: mockIsValid,
    },
  };
});

describe('AirportDetailsCard', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockFetchAirportRegion.mockResolvedValue({
      airport_code: 'KJFK',
      icao_region: 'K1',
    });
    mockFindWhere.mockImplementation((criteria) => realAirportsApi.findWhere(criteria));
    mockIsValid.mockImplementation((icao) => realAirportsApi.isValid(icao));
  });

  it('returns null for invalid ICAO codes', () => {
    const { container } = render(<AirportDetailsCard icao="ZZZZ" />);
    expect(container).toBeEmptyDOMElement();
  });

  it('returns null for short ICAO codes', () => {
    const { container } = render(<AirportDetailsCard icao="KJ" />);
    expect(container).toBeEmptyDOMElement();
  });

  it('renders airport details and region info for valid ICAO', async () => {
    render(<AirportDetailsCard icao=" kjfk " />);

    expect(screen.getByLabelText('Airport details')).toBeInTheDocument();
    expect(
      screen.getByText('John F. Kennedy International Airport'),
    ).toBeInTheDocument();
    expect(screen.getByText('New York, United States')).toBeInTheDocument();
    expect(screen.getByText('IATA: JFK')).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText('ICAO region: K1')).toBeInTheDocument();
    });
    expect(mockFetchAirportRegion).toHaveBeenCalledWith('KJFK');
  });

  it('shows loading state before region fetch completes', () => {
    mockFetchAirportRegion.mockImplementation(() => new Promise(() => undefined));

    render(<AirportDetailsCard icao="KJFK" />);

    expect(screen.getByText('Loading ICAO region…')).toBeInTheDocument();
  });

  it('shows region fetch errors', async () => {
    mockFetchAirportRegion.mockRejectedValueOnce(new Error('Region unavailable'));

    render(<AirportDetailsCard icao="KJFK" />);

    await waitFor(() => {
      expect(screen.getByText('Region unavailable')).toBeInTheDocument();
    });
  });

  it('falls back to ICAO code when airport metadata is missing', async () => {
    mockFindWhere.mockReturnValue(undefined);

    render(<AirportDetailsCard icao="KATL" />);

    expect(screen.getByText('KATL')).toBeInTheDocument();
    await waitFor(() => {
      expect(mockFetchAirportRegion).toHaveBeenCalledWith('KATL');
    });
  });

  it('ignores region fetch results after unmount', async () => {
    vi.useFakeTimers();
    mockFetchAirportRegion.mockImplementation(
      () =>
        new Promise((resolve) => {
          setTimeout(() => resolve({ airport_code: 'KJFK', icao_region: 'K1' }), 100);
        }),
    );

    const { unmount } = render(<AirportDetailsCard icao="KJFK" />);
    unmount();

    await act(async () => {
      vi.advanceTimersByTime(100);
    });

    expect(screen.queryByText('ICAO region: K1')).not.toBeInTheDocument();
    vi.useRealTimers();
  });

  it('ignores region fetch errors after unmount', async () => {
    vi.useFakeTimers();
    mockFetchAirportRegion.mockImplementation(
      () =>
        new Promise((_, reject) => {
          setTimeout(() => reject(new Error('region down')), 100);
        }),
    );

    const { unmount } = render(<AirportDetailsCard icao="KJFK" />);
    unmount();

    await act(async () => {
      vi.advanceTimersByTime(100);
    });

    expect(screen.queryByText(/region down/i)).not.toBeInTheDocument();
    vi.useRealTimers();
  });

  it('renders city-only location when country is absent', async () => {
    mockFindWhere.mockReturnValue({
      icao: 'KATL',
      name: 'Test Airport',
      city: 'Test City',
      country: '',
    });

    render(<AirportDetailsCard icao="KATL" />);

    expect(screen.getByText('Test City')).toBeInTheDocument();
    expect(screen.queryByText(/Test City,/)).not.toBeInTheDocument();
  });

  it('omits IATA line when airport has no IATA code', async () => {
    mockFindWhere.mockReturnValue({
      icao: 'KATL',
      name: 'Test Airport',
      city: 'Test City',
      country: 'Test Country',
    });
    mockFetchAirportRegion.mockResolvedValueOnce({
      airport_code: 'KATL',
      icao_region: 'K1',
    });

    render(<AirportDetailsCard icao="KATL" />);

    expect(screen.queryByText(/^IATA:/)).not.toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByText('ICAO region: K1')).toBeInTheDocument();
    });
  });
});

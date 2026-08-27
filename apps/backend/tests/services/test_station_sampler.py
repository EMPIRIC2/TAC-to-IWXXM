"""Unit tests for station sampler utility."""

import csv

import pytest
from src.utilities.station_sampler import StationSampler


@pytest.fixture
def sample_airports_csv(tmp_path):
    """Create a sample airports CSV for testing."""
    csv_file = tmp_path / "test-airports.csv"

    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["id", "ident", "type", "name", "icao_code", "country_name", "scheduled_service"]
        )
        writer.writeheader()

        # Large airports with scheduled service
        writer.writerow(
            {
                "id": "1",
                "ident": "KJFK",
                "type": "large_airport",
                "name": "John F Kennedy Intl",
                "icao_code": "KJFK",
                "country_name": "United States",
                "scheduled_service": "1",
            }
        )
        writer.writerow(
            {
                "id": "2",
                "ident": "KLAX",
                "type": "large_airport",
                "name": "Los Angeles Intl",
                "icao_code": "KLAX",
                "country_name": "United States",
                "scheduled_service": "1",
            }
        )
        writer.writerow(
            {
                "id": "3",
                "ident": "KORD",
                "type": "large_airport",
                "name": "Chicago O'Hare",
                "icao_code": "KORD",
                "country_name": "United States",
                "scheduled_service": "1",
            }
        )

        # Medium airport
        writer.writerow(
            {
                "id": "4",
                "ident": "KBUR",
                "type": "medium_airport",
                "name": "Burbank Airport",
                "icao_code": "KBUR",
                "country_name": "United States",
                "scheduled_service": "1",
            }
        )

        # Small airport
        writer.writerow(
            {
                "id": "5",
                "ident": "KSMX",
                "type": "small_airport",
                "name": "Santa Maria",
                "icao_code": "KSMX",
                "country_name": "United States",
                "scheduled_service": "0",
            }
        )

    return csv_file


@pytest.mark.unit
class TestStationSampler:
    """Unit tests for StationSampler."""

    def test_initialization_with_csv(self, sample_airports_csv):
        """Test sampler initializes with provided CSV path."""
        sampler = StationSampler(csv_path=sample_airports_csv)
        assert sampler.csv_path == sample_airports_csv
        assert sampler._airports_cache is None

    def test_load_airports(self, sample_airports_csv):
        """Test loading and caching airports."""
        sampler = StationSampler(csv_path=sample_airports_csv)
        airports = sampler._load_airports()

        assert len(airports) == 5
        assert sampler._airports_cache is not None
        assert len(sampler._airports_cache) == 5
        assert all("icao" in a for a in airports)
        assert all(len(a["icao"]) == 4 for a in airports)

    def test_sample_random_stations(self, sample_airports_csv):
        """Test random station sampling."""
        sampler = StationSampler(csv_path=sample_airports_csv)

        stations = sampler.sample_random_stations(count=2, seed=42)

        assert len(stations) == 2
        assert all(isinstance(s, str) for s in stations)
        assert all(len(s) == 4 for s in stations)

    def test_sample_large_airports_only(self, sample_airports_csv):
        """Test sampling with large_airports_only filter."""
        sampler = StationSampler(csv_path=sample_airports_csv)

        stations = sampler.sample_random_stations(
            count=10, large_airports_only=True, scheduled_service_only=False, seed=42
        )

        assert len(stations) == 3
        assert set(stations) == {"KJFK", "KLAX", "KORD"}

    def test_sample_scheduled_service_only(self, sample_airports_csv):
        """Test sampling with scheduled_service_only filter."""
        sampler = StationSampler(csv_path=sample_airports_csv)

        stations = sampler.sample_random_stations(
            count=10, large_airports_only=False, scheduled_service_only=True, seed=42
        )

        assert len(stations) == 4
        assert "KSMX" not in stations

    def test_get_all_major_airports(self, sample_airports_csv):
        """Test getting all major airports."""
        sampler = StationSampler(csv_path=sample_airports_csv)

        airports = sampler.get_all_major_airports(large_only=True, scheduled_service_only=True)

        assert len(airports) == 3
        assert set(airports) == {"KJFK", "KLAX", "KORD"}

    def test_get_station_info(self, sample_airports_csv):
        """Test getting individual station info."""
        sampler = StationSampler(csv_path=sample_airports_csv)

        info = sampler.get_station_info("KJFK")

        assert info is not None
        assert info["icao"] == "KJFK"
        assert info["name"] == "John F Kennedy Intl"
        assert info["type"] == "large_airport"

    def test_get_station_info_not_found(self, sample_airports_csv):
        """Test station not found returns None."""
        sampler = StationSampler(csv_path=sample_airports_csv)

        info = sampler.get_station_info("ZZZZ")

        assert info is None

    def test_caching_works(self, sample_airports_csv):
        """Test that airport data is cached after first load."""
        sampler = StationSampler(csv_path=sample_airports_csv)

        airports1 = sampler._load_airports()
        cache1 = sampler._airports_cache

        airports2 = sampler._load_airports()
        cache2 = sampler._airports_cache

        assert cache1 is cache2
        assert airports1 is cache2


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "unit"])

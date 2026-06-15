"""Unit tests for station sampler utility."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.utilities.station_sampler import StationSampler


@pytest.fixture
def airports_csv(tmp_path: Path) -> Path:
    """Create a small airports CSV fixture file."""
    csv_path = tmp_path / "af-airports.csv"
    csv_path.write_text(
        "icao_code,name,country_name,type,scheduled_service\n"
        "KJFK,John F Kennedy Intl,United States,large_airport,1\n"
        "KBOS,Logan Intl,United States,large_airport,1\n"
        "KXYZ,Test Regional,United States,small_airport,0\n"
        "1234,Invalid Numeric,Nowhere,large_airport,1\n"
        "ABCD1,Invalid Length,Nowhere,large_airport,1\n"
        ",Missing ICAO,Nowhere,small_airport,0\n",
        encoding="utf-8",
    )
    return csv_path


def test_load_airports_filters_invalid_icao_and_caches(airports_csv: Path) -> None:
    sampler = StationSampler(csv_path=airports_csv)

    first = sampler._load_airports()
    second = sampler._load_airports()

    assert first is second
    assert [a["icao"] for a in first] == ["KJFK", "KBOS", "KXYZ"]


def test_sample_random_stations_with_filters_and_seed(airports_csv: Path) -> None:
    sampler = StationSampler(csv_path=airports_csv)

    sample = sampler.sample_random_stations(
        count=10,
        large_airports_only=True,
        scheduled_service_only=True,
        seed=7,
    )

    assert sorted(sample) == ["KBOS", "KJFK"]


def test_get_all_major_airports_and_station_info(airports_csv: Path) -> None:
    sampler = StationSampler(csv_path=airports_csv)

    majors = sampler.get_all_major_airports(large_only=True, scheduled_service_only=False)

    assert sorted(majors) == ["KBOS", "KJFK"]
    assert sampler.get_station_info("KJFK")["name"] == "John F Kennedy Intl"
    assert sampler.get_station_info("XXXX") is None


def test_find_airports_csv_raises_when_no_candidate_exists(monkeypatch: pytest.MonkeyPatch) -> None:
    class _MissingPath:
        def __init__(self, *_args, **_kwargs):
            self._parents = ()

        def resolve(self):
            return self

        @property
        def parents(self):
            return self._parents

        def __truediv__(self, _other):
            return self

        def exists(self):
            return False

    monkeypatch.setattr("src.utilities.station_sampler.pathlib.Path", _MissingPath)

    with pytest.raises(FileNotFoundError, match="Could not find af-airports.csv"):
        StationSampler._find_airports_csv()

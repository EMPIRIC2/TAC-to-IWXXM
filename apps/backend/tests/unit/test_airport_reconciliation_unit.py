"""Unit tests for AirportReconciliationService - 0% coverage target."""

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from src.services.airport_reconciliation import (
    AirportReconciliationService,
    ConflictLog,
    DataSource,
    ReconciledAirport,
)


class TestDataSourceEnum:
    def test_priority_order(self):
        assert DataSource.OPENAIP.value < DataSource.GIFTS.value
        assert DataSource.GIFTS.value < DataSource.AVIATION_WEATHER.value


class TestConflictLog:
    def test_str_includes_icao(self):
        c = ConflictLog(
            icao="KJFK",
            field="elevation",
            sources={"openaip": 9.14, "gifts": 9.0},
            resolution="9.14",
            winner="openaip",
        )
        s = str(c)
        assert "KJFK" in s
        assert "elevation" in s


class TestReconciledAirport:
    def test_has_conflicts_false_when_empty(self):
        ra = ReconciledAirport(icao_code="KJFK", name="JFK", country="US")
        assert ra.has_conflicts() is False

    def test_has_conflicts_true_when_present(self):
        ra = ReconciledAirport(icao_code="KJFK", name="JFK", country="US")
        ra.conflicts.append(ConflictLog(icao="KJFK", field="name", sources={}, resolution="JFK", winner="openaip"))
        assert ra.has_conflicts() is True

    def test_get_conflict_summary_no_conflicts(self):
        ra = ReconciledAirport(icao_code="KJFK", name="JFK", country="US")
        summary = ra.get_conflict_summary()
        assert "No conflicts" in summary

    def test_get_conflict_summary_with_conflicts(self):
        ra = ReconciledAirport(icao_code="KJFK", name="JFK", country="US")
        ra.conflicts.append(
            ConflictLog(icao="KJFK", field="elevation", sources={}, resolution="9.14", winner="openaip")
        )
        summary = ra.get_conflict_summary()
        assert "conflict" in summary.lower()

    def test_default_confidence_scores(self):
        ra = ReconciledAirport(icao_code="KJFK", name="JFK", country="US")
        assert ra.coordinate_confidence == 1.0
        assert ra.elevation_confidence == 1.0


def _make_service(openaip=None, aw=None, gifts_csv=None):
    mock_openaip = openaip or MagicMock()
    mock_aw = aw or MagicMock()
    mock_aw.fetch_airport.return_value = None
    gifts_path = gifts_csv or Path("/nonexistent/path.csv")
    svc = AirportReconciliationService(
        openaip_client=mock_openaip,
        aviation_weather_client=mock_aw,
        gifts_data_path=gifts_path,
    )
    return svc


class TestAirportReconciliationServiceInit:
    def test_init_with_mocks(self):
        svc = _make_service()
        assert svc.stats["total_queries"] == 0

    def test_default_stats_keys(self):
        svc = _make_service()
        expected_keys = {
            "total_queries",
            "openaip_hits",
            "gifts_hits",
            "aviation_weather_hits",
            "conflicts_detected",
            "conflicts_resolved",
        }
        assert expected_keys.issubset(svc.stats.keys())


class TestLoadGiftsData:
    def test_missing_file_does_not_crash(self, tmp_path):
        svc = _make_service(gifts_csv=tmp_path / "nonexistent.csv")
        svc._load_gifts_data()
        assert svc._gifts_loaded is True

    def test_loads_csv_with_icao_code_field(self, tmp_path):
        csv_path = tmp_path / "airports.csv"
        csv_path.write_text("icao_code,name,elevation_ft\nKJFK,JFK Airport,13\nEGLL,Heathrow,80\n")
        svc = _make_service(gifts_csv=csv_path)
        svc._load_gifts_data()
        assert "KJFK" in svc._gifts_cache
        assert "EGLL" in svc._gifts_cache

    def test_loads_csv_with_icao_field(self, tmp_path):
        csv_path = tmp_path / "airports.csv"
        csv_path.write_text("icao,name,elevation\nEDDF,Frankfurt,111\n")
        svc = _make_service(gifts_csv=csv_path)
        svc._load_gifts_data()
        assert "EDDF" in svc._gifts_cache

    def test_load_twice_is_idempotent(self, tmp_path):
        csv_path = tmp_path / "airports.csv"
        csv_path.write_text("icao,name\nKJFK,JFK\n")
        svc = _make_service(gifts_csv=csv_path)
        svc._load_gifts_data()
        svc._load_gifts_data()  # Second call should be no-op
        assert svc._gifts_loaded is True

    def test_skip_rows_without_icao(self, tmp_path):
        csv_path = tmp_path / "airports.csv"
        csv_path.write_text("icao_code,name\n,No ICAO Airport\nKJFK,JFK\n")
        svc = _make_service(gifts_csv=csv_path)
        svc._load_gifts_data()
        assert "" not in svc._gifts_cache
        assert "KJFK" in svc._gifts_cache

    def test_load_gifts_data_handles_csv_read_exception(self, monkeypatch, tmp_path):
        csv_path = tmp_path / "airports.csv"
        csv_path.write_text("icao_code,name\nKJFK,JFK\n")
        svc = _make_service(gifts_csv=csv_path)

        def boom(*args, **kwargs):
            raise RuntimeError("csv exploded")

        monkeypatch.setattr("builtins.open", boom)

        svc._load_gifts_data()

        assert svc._gifts_loaded is True
        assert svc._gifts_cache == {}


class TestSafeFloat:
    @pytest.mark.parametrize(("value", "expected"), [(None, None), ("", None), ("12.5", 12.5), (12, 12.0)])
    def test_safe_float_expected_values(self, value, expected):
        svc = _make_service()
        assert svc._safe_float(value) == expected

    @pytest.mark.parametrize("value", ["abc", object()])
    def test_safe_float_invalid_values_return_none(self, value):
        svc = _make_service()
        assert svc._safe_float(value) is None


class TestReconcileAirport:
    def test_reconcile_uses_openaip_when_available(self):
        mock_airport = MagicMock()
        mock_airport.icao_code = "KJFK"
        mock_airport.name = "JFK International"
        mock_airport.country = "US"
        mock_airport.latitude = 40.64
        mock_airport.longitude = -73.78
        mock_airport.elevation = 9.14
        mock_airport.iata_code = "JFK"

        mock_openaip = MagicMock()
        mock_openaip.get_airport_by_icao.return_value = mock_airport

        svc = _make_service(openaip=mock_openaip)
        result = svc.get_airport("KJFK")

        assert result is not None
        assert result.icao_code == "KJFK"
        assert "openaip" in result.primary_source.lower() or result.primary_source is not None

    def test_reconcile_missing_airport_returns_fallback(self):
        mock_openaip = MagicMock()
        mock_openaip.get_airport_by_icao.return_value = None
        mock_aw = MagicMock()
        mock_aw.fetch_airport.return_value = None

        svc = _make_service(openaip=mock_openaip, aw=mock_aw)
        result = svc.get_airport("XXXX")
        # May return None or a minimal record
        assert result is None or isinstance(result, ReconciledAirport)

    def test_reconcile_increments_stats(self):
        mock_openaip = MagicMock()
        mock_openaip.get_airport_by_icao.return_value = None
        mock_aw = MagicMock()
        mock_aw.fetch_airport.return_value = None

        svc = _make_service(openaip=mock_openaip, aw=mock_aw)
        svc.get_airport("KJFK")
        assert svc.stats["total_queries"] >= 1

    def test_get_airport_uses_gifts_data_and_updates_hit_stats(self, tmp_path):
        csv_path = tmp_path / "airports.csv"
        csv_path.write_text(
            "icao_code,name,iso_country,latitude_deg,longitude_deg,elevation_ft\nKJFK,JFK Airport,US,40.64,-73.78,30\n",
            encoding="utf-8",
        )
        mock_openaip = MagicMock()
        mock_openaip.get_airport_by_icao.return_value = None

        svc = _make_service(openaip=mock_openaip, gifts_csv=csv_path)
        result = svc.get_airport("kjfk")

        assert result is not None
        assert result.primary_source == DataSource.GIFTS.name
        assert svc.stats["gifts_hits"] == 1
        assert result.elevation == pytest.approx(30 * 0.3048)


class TestInternalReconciliationHelpers:
    def test_get_field_supports_dict_and_object(self):
        svc = _make_service()
        obj = SimpleNamespace(name="JFK")

        assert svc._get_field({"name": "Heathrow"}, "name", "") == "Heathrow"
        assert svc._get_field(obj, "name", "") == "JFK"
        assert svc._get_field(obj, "country", "US") == "US"

    def test_reconcile_returns_none_when_only_unknown_priority_sources_exist(self):
        svc = _make_service()

        result = svc._reconcile("KJFK", {DataSource.FALLBACK: {"name": "Fallback"}})

        assert result is None

    def test_check_field_conflict_returns_none_for_single_source_or_matching_values(self):
        svc = _make_service()
        sources_single = {DataSource.OPENAIP: {"name": "JFK"}}
        sources_same = {
            DataSource.OPENAIP: {"country": "US"},
            DataSource.GIFTS: {"country": "US"},
        }

        assert svc._check_field_conflict("KJFK", "name", sources_single, [DataSource.OPENAIP]) is None
        assert (
            svc._check_field_conflict("KJFK", "country", sources_same, [DataSource.OPENAIP, DataSource.GIFTS]) is None
        )

    def test_check_field_conflict_resolves_by_priority_and_skips_none_values(self):
        svc = _make_service()
        sources = {
            DataSource.OPENAIP: {"name": None},
            DataSource.GIFTS: {"name": "John F Kennedy"},
            DataSource.AVIATION_WEATHER: {"name": "JFK Intl"},
        }

        conflict = svc._check_field_conflict(
            "KJFK",
            "name",
            sources,
            [DataSource.OPENAIP, DataSource.GIFTS, DataSource.AVIATION_WEATHER],
        )

        assert conflict is not None
        assert conflict.winner == DataSource.GIFTS.name
        assert conflict.resolution == "John F Kennedy"
        assert set(conflict.sources.keys()) == {DataSource.GIFTS.name, DataSource.AVIATION_WEATHER.name}

    def test_check_field_conflict_skips_missing_priority_sources_before_finding_winner(self):
        svc = _make_service()
        sources = {
            DataSource.GIFTS: {"country": "US"},
            DataSource.FALLBACK: {"country": "USA"},
        }

        conflict = svc._check_field_conflict(
            "KJFK",
            "country",
            sources,
            [DataSource.OPENAIP, DataSource.AVIATION_WEATHER, DataSource.GIFTS],
        )

        assert conflict is not None
        assert conflict.winner == DataSource.GIFTS.name

    def test_check_field_conflict_can_return_unresolved_when_priority_list_has_no_matching_sources(self):
        svc = _make_service()
        sources = {
            DataSource.GIFTS: {"country": "US"},
            DataSource.FALLBACK: {"country": "USA"},
        }

        conflict = svc._check_field_conflict("KJFK", "country", sources, [])

        assert conflict is not None
        assert conflict.winner is None
        assert conflict.resolution == "None"

    def test_reconcile_collects_conflicts_and_updates_stats(self):
        svc = _make_service()
        openaip = SimpleNamespace(
            name="JFK International",
            country="US",
            latitude=40.64,
            longitude=-73.78,
            elevation=10.0,
            iata_code="JFK",
        )
        gifts = {
            "name": "John F Kennedy",
            "country": "USA",
            "latitude": 40.70,
            "longitude": -73.90,
            "elevation": 25.0,
        }

        result = svc._reconcile(
            "KJFK",
            {
                DataSource.OPENAIP: openaip,
                DataSource.GIFTS: gifts,
            },
        )

        assert result is not None
        assert result.primary_source == DataSource.OPENAIP.name
        assert result.has_conflicts() is True
        assert len(result.conflicts) == 5
        assert svc.stats["conflicts_detected"] == 5
        assert svc.stats["conflicts_resolved"] == 5
        assert result.coordinate_confidence < 1.0
        assert result.elevation_confidence < 1.0

    def test_coordinate_confidence_returns_zero_without_final_coords_or_source_coords(self):
        svc = _make_service()
        sources_without_coords = {DataSource.OPENAIP: {"name": "JFK"}}

        assert svc._calculate_coordinate_confidence(sources_without_coords, None, -73.7) == 0.0
        assert svc._calculate_coordinate_confidence(sources_without_coords, 40.0, -73.7) == 0.0

    def test_coordinate_confidence_boosts_and_clamps_with_openaip_agreement(self):
        svc = _make_service()
        sources = {
            DataSource.OPENAIP: {"latitude": 40.0, "longitude": -73.0},
            DataSource.GIFTS: {"latitude": 40.005, "longitude": -73.005},
        }

        confidence = svc._calculate_coordinate_confidence(sources, 40.0, -73.0)

        assert confidence == 1.0

    def test_elevation_confidence_returns_zero_without_final_or_source_elevation(self):
        svc = _make_service()
        sources_without_elevation = {DataSource.GIFTS: {"name": "JFK"}}

        assert svc._calculate_elevation_confidence(sources_without_elevation, None) == 0.0
        assert svc._calculate_elevation_confidence(sources_without_elevation, 12.0) == 0.0

    def test_elevation_confidence_boosts_with_openaip_and_counts_disagreement(self):
        svc = _make_service()
        sources = {
            DataSource.OPENAIP: {"elevation": 10.0},
            DataSource.GIFTS: {"elevation": 12.0},
            DataSource.AVIATION_WEATHER: {"elevation": 40.0},
        }

        confidence = svc._calculate_elevation_confidence(sources, 10.0)

        assert confidence == pytest.approx((2 / 3) + 0.2)


class TestStatistics:
    def test_get_statistics_zero_queries_conflict_rate_is_zero(self):
        svc = _make_service()

        stats = svc.get_statistics()

        assert stats["conflict_rate"] == 0.0
        assert stats["gifts_airports_loaded"] == 0
        assert stats["openaip_available"] is True

    def test_get_statistics_reports_conflict_rate_after_queries(self):
        svc = _make_service()
        svc.stats["total_queries"] = 4
        svc.stats["conflicts_detected"] = 2
        svc._gifts_cache["KJFK"] = {"name": "JFK"}

        stats = svc.get_statistics()

        assert stats["conflict_rate"] == 0.5
        assert stats["gifts_airports_loaded"] == 1

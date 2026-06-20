"""Unit tests for AirportRecordBuilder – 0% coverage target."""

import json
from unittest.mock import patch

from src.utilities.airport_record_builder import AirportRecordBuilder


def _make_builder(tmp_path, airports_data=None, datum_map=None):
    """Create a builder pointing to a temp data dir."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    if airports_data is not None:
        (data_dir / "airports.json").write_text(json.dumps(airports_data))

    if datum_map is not None:
        (data_dir / "vertical_datum_map.json").write_text(json.dumps(datum_map))
    else:
        (data_dir / "vertical_datum_map.json").write_text(
            json.dumps({"country_defaults": {}, "airport_overrides": {}, "datum_info": {}})
        )

    with patch.object(AirportRecordBuilder, "__init__") as mock_init:
        mock_init.return_value = None
        builder = AirportRecordBuilder()
        builder.data_dir = data_dir
        builder._vertical_datum_map = builder._load_json("vertical_datum_map.json")
        builder._airports_json = builder._load_json("airports.json")
    return builder


class TestAirportRecordBuilderLoadJson:
    def test_load_airports_list_converts_to_dict(self, tmp_path):
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        (data_dir / "airports.json").write_text(
            json.dumps([{"icao": "KJFK", "name": "JFK"}, {"icao": "EGLL", "name": "Heathrow"}])
        )
        with patch.object(AirportRecordBuilder, "__init__", return_value=None):
            builder = AirportRecordBuilder()
            builder.data_dir = data_dir
        result = builder._load_json("airports.json")
        assert "KJFK" in result
        assert result["KJFK"]["name"] == "JFK"

    def test_load_missing_file_returns_empty_dict(self, tmp_path):
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        with patch.object(AirportRecordBuilder, "__init__", return_value=None):
            builder = AirportRecordBuilder()
            builder.data_dir = data_dir
        result = builder._load_json("nonexistent.json")
        assert result == {}

    def test_load_bad_json_returns_empty_dict(self, tmp_path):
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        (data_dir / "bad.json").write_text("{{NOT JSON")
        with patch.object(AirportRecordBuilder, "__init__", return_value=None):
            builder = AirportRecordBuilder()
            builder.data_dir = data_dir
        result = builder._load_json("bad.json")
        assert result == {}

    def test_load_dict_json(self, tmp_path):
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        (data_dir / "dict.json").write_text(json.dumps({"key": "value"}))
        with patch.object(AirportRecordBuilder, "__init__", return_value=None):
            builder = AirportRecordBuilder()
            builder.data_dir = data_dir
        result = builder._load_json("dict.json")
        assert result == {"key": "value"}

    def test_load_non_dict_non_list_returns_empty(self, tmp_path):
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        (data_dir / "weird.json").write_text('"just a string"')
        with patch.object(AirportRecordBuilder, "__init__", return_value=None):
            builder = AirportRecordBuilder()
            builder.data_dir = data_dir
        result = builder._load_json("weird.json")
        assert result == {}


class TestAirportRecordBuilderBuildRecord:
    def test_build_record_uses_airports_json_fallback(self, tmp_path):
        airports = [
            {
                "icao": "KJFK",
                "name": "JFK Airport",
                "iata": "JFK",
                "designator": "KJFK",
                "lat": 40.6398,
                "lon": -73.7789,
            }
        ]
        builder = _make_builder(tmp_path, airports_data=airports)
        record = builder.build_record("KJFK")
        assert record["icao"] == "KJFK"

    def test_build_record_unknown_airport(self, tmp_path):
        builder = _make_builder(tmp_path, airports_data=[])
        record = builder.build_record("XXXX")
        assert record["icao"] == "XXXX"
        assert record["status"] == "unknown"

    def test_build_record_uses_openaip_data(self, tmp_path):
        builder = _make_builder(tmp_path, airports_data=[])
        openaip_data = {
            "name": "Test Airport",
            "iata": "TST",
            "geometry": {"type": "Point", "coordinates": [10.0, 52.0]},
        }
        record = builder.build_record("EDDE", openaip_data=openaip_data)
        assert record["icao"] == "EDDE"

    def test_build_record_icao_normalised_to_upper(self, tmp_path):
        airports = [{"icao": "KJFK", "name": "JFK"}]
        builder = _make_builder(tmp_path, airports_data=airports)
        record = builder.build_record("kjfk")
        assert record["icao"] == "KJFK"

    def test_build_record_override_in_datum_map(self, tmp_path):
        datum_map = {
            "country_defaults": {},
            "airport_overrides": {
                "EGLL": {
                    "name": "Heathrow Override",
                    "vertical_datum": "EGM_96",
                    "source": "manual",
                }
            },
            "datum_info": {},
        }
        builder = _make_builder(tmp_path, airports_data=[], datum_map=datum_map)
        record = builder.build_record("EGLL")
        assert record["_override"] is True

    def test_build_record_returns_early_on_complete_override(self, tmp_path):
        datum_map = {
            "country_defaults": {},
            "airport_overrides": {
                "ENFB": {
                    "name": "FORNEBU AIRPORT",
                    "iata": "FBU",
                    "designator": "FBU",
                    "coordinates": {"latitude": 59.89580, "longitude": 10.6172},
                    "source": "manual",
                }
            },
            "datum_info": {},
        }
        builder = _make_builder(tmp_path, airports_data=[], datum_map=datum_map)
        record = builder.build_record("ENFB")
        assert record["source"] == "manual"
        assert record["_sources_tried"] == ["vertical_datum_map"]

    def test_build_record_merges_openaip_then_airports(self, tmp_path):
        airports = [
            {
                "icao": "KDEN",
                "name": "Denver Intl",
                "iata": "DEN",
                "designator": "DEN",
                "coordinates": {"latitude": 39.8561, "longitude": -104.6737},
            }
        ]
        builder = _make_builder(tmp_path, airports_data=airports)
        openaip_data = {"name": "DEN from OpenAIP"}
        record = builder.build_record("KDEN", openaip_data=openaip_data)
        assert record["name"] == "DEN from OpenAIP"
        assert record["iata"] == "DEN"
        assert record["designator"] == "DEN"
        assert record["coordinates"]["latitude"] == 39.8561

    def test_build_record_uses_validator_when_all_other_sources_missing(self, tmp_path):
        builder = _make_builder(tmp_path, airports_data=[])

        class _Validator:
            def get_airport_info(self, icao):
                return {
                    "name": "Validator Airport",
                    "iata": "VAL",
                    "coordinates": {"latitude": 1.0, "longitude": 2.0},
                }

        record = builder.build_record("VALD", airport_validator=_Validator())
        assert record["source"] == "AirportValidator"
        assert record["name"] == "Validator Airport"

    def test_build_record_validator_exception_is_handled(self, tmp_path):
        builder = _make_builder(tmp_path, airports_data=[])

        class _BadValidator:
            def get_airport_info(self, icao):
                raise RuntimeError("boom")

        record = builder.build_record("FAIL", airport_validator=_BadValidator())
        assert record["source"] == "unknown"
        assert "AirportValidator" in record["_sources_tried"]


class TestAirportRecordBuilderExtractFields:
    def test_extract_fields_prefers_iataCode_and_altIdentifier(self, tmp_path):
        builder = _make_builder(tmp_path, airports_data=[])
        extracted = builder._extract_fields(
            {
                "name": "Alt Airport",
                "iataCode": "ALT",
                "altIdentifier": "AID",
                "latitude": 10,
                "longitude": 20,
                "elevation": 123,
                "status": "closed",
                "closure_year": 1977,
            }
        )
        assert extracted["iata"] == "ALT"
        assert extracted["designator"] == "AID"
        assert extracted["coordinates"] == {"latitude": 10, "longitude": 20}
        assert extracted["elevation_m"] == 123.0
        assert extracted["status"] == "closed"
        assert extracted["closure_year"] == 1977

    def test_extract_fields_designator_falls_back_to_iata(self, tmp_path):
        builder = _make_builder(tmp_path, airports_data=[])
        extracted = builder._extract_fields({"iata": "XYZ"})
        assert extracted["designator"] == "XYZ"

    def test_extract_fields_rejects_invalid_coordinates_dict(self, tmp_path):
        builder = _make_builder(tmp_path, airports_data=[])
        extracted = builder._extract_fields({"coordinates": {"latitude": 1.0}})
        assert "coordinates" not in extracted


class TestAirportRecordBuilderGiftsFormat:
    def test_get_gifts_format_complete_record(self, tmp_path):
        builder = _make_builder(tmp_path, airports_data=[])
        record = {
            "icao": "ENFB",
            "name": "FORNEBU AIRPORT",
            "iata": "FBU",
            "designator": "FBU",
            "coordinates": {"latitude": 59.89580, "longitude": 10.6172},
        }
        line = builder.get_gifts_format(record)
        assert line == "FORNEBU AIRPORT|FBU|FBU|59.8958,10.6172"

    def test_get_gifts_format_incomplete_record_returns_empty(self, tmp_path):
        builder = _make_builder(tmp_path, airports_data=[])
        line = builder.get_gifts_format({"icao": "XXXX", "name": "No Coords"})
        assert line == ""

    def test_get_gifts_format_missing_lat_lon_returns_empty(self, tmp_path):
        builder = _make_builder(tmp_path, airports_data=[])
        line = builder.get_gifts_format(
            {
                "icao": "XXXX",
                "name": "No Lat",
                "iata": "NOL",
                "designator": "NOL",
                "coordinates": {"latitude": None, "longitude": 10},
            }
        )
        assert line == ""

"""Unit tests for ElevationService – 0% coverage target."""

import json
from pathlib import Path
from unittest.mock import patch

from src.utilities import elevation_service as elevation_module
from src.utilities.elevation_service import ElevationService, get_elevation_service


def _make_service(tmp_path, datum_map=None):
    """Create an ElevationService pointing at a temporary datum file."""
    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True)
    if datum_map is None:
        datum_map = {
            "country_defaults": {"US": "NAVD88", "AU": "AHD"},
            "airport_overrides": {
                "EGLL": {"vertical_datum": "EGM_96"},
                "KJFK": {"vertical_datum": "NAVD88"},
            },
            "datum_info": {"NAVD88": {"name": "North American Vertical Datum 1988"}},
        }
    datum_file = data_dir / "vertical_datum_map.json"
    datum_file.write_text(json.dumps(datum_map))

    # Patch the path so the service loads our test file
    with patch.object(
        ElevationService,
        "_load_datum_mapping",
        lambda self: _load_from_path(self, datum_file),
    ):
        svc = ElevationService()
    return svc


def _load_from_path(service, path):
    """Helper that loads from a specific path."""
    import json

    with open(path) as f:
        service.datum_map = json.load(f)


class TestElevationServiceInit:
    def test_loads_datum_map(self, tmp_path):
        svc = _make_service(tmp_path)
        assert "country_defaults" in svc.datum_map

    def test_handles_missing_datum_file(self):
        """Should not raise when datum file is missing."""
        svc = ElevationService.__new__(ElevationService)
        with patch.object(Path, "open", side_effect=FileNotFoundError):
            svc.datum_map = {}
            svc._load_datum_mapping()
        # Gracefully degraded
        assert isinstance(svc.datum_map, dict)

    def test_handles_bad_json_datum_file(self, tmp_path):
        data_dir = tmp_path / "src" / "data"
        data_dir.mkdir(parents=True)
        (data_dir / "vertical_datum_map.json").write_text("{{BAD")
        svc = ElevationService.__new__(ElevationService)
        svc.datum_map = {}
        # Call _load_datum_mapping which searches relative to __file__
        # Just confirm no exception from degraded path
        svc._load_datum_mapping()
        assert isinstance(svc.datum_map, dict)


class TestElevationServiceGetVerticalDatum:
    def test_airport_override_takes_priority(self, tmp_path):
        svc = _make_service(tmp_path)
        result = svc.get_vertical_datum("EGLL")
        assert result == "EGM_96"

    def test_country_default_used_when_no_override(self, tmp_path):
        svc = _make_service(tmp_path)
        result = svc.get_vertical_datum("KLAX", country_code="US")
        assert "NAVD" in result or result == "NAVD88"

    def test_global_default_egm96_when_nothing_matches(self, tmp_path):
        svc = _make_service(tmp_path)
        result = svc.get_vertical_datum("ZZZZ", country_code=None)
        assert result == "EGM_96"

    def test_unknown_country_code_falls_back_to_default(self, tmp_path):
        svc = _make_service(tmp_path)
        result = svc.get_vertical_datum("ABCD", country_code="XZ")
        assert result == "EGM_96"

    def test_airport_override_ignores_country_code(self, tmp_path):
        svc = _make_service(tmp_path)
        # KJFK override → NAVD88, regardless of country
        result = svc.get_vertical_datum("KJFK", country_code="AU")
        assert result == "NAVD88"


class TestElevationServiceNormalizeDatum:
    def test_normalize_egm96_variants(self, tmp_path):
        svc = _make_service(tmp_path)
        # EGM_96 and EGM96 should both be accepted
        code = svc._normalize_datum_code("EGM96")
        assert code in {"EGM_96", "EGM96"}

    def test_normalize_supported_navd88(self, tmp_path):
        svc = _make_service(tmp_path)
        code = svc._normalize_datum_code("NAVD88")
        assert code == "NAVD88"

    def test_normalize_unsupported_gets_other_prefix(self, tmp_path):
        svc = _make_service(tmp_path)
        code = svc._normalize_datum_code("CGVD2013")
        assert "CGVD2013" in code


class TestElevationServiceRawData:
    def test_get_raw_data_uses_test_override_with_production_elevation(self, tmp_path):
        svc = _make_service(
            tmp_path,
            {
                "country_defaults": {"US": "NAVD88"},
                "airport_overrides": {
                    "KJFK": {"vertical_datum": "NAVD88", "elevation_m": 4},
                },
                "test_overrides": {
                    "KJFK": {"vertical_datum": "OTHER:WGS84", "production_datum": "NAVD88"},
                },
                "datum_info": {},
            },
        )

        elevation_m, datum = svc._get_raw_elevation_data("KJFK", use_test_overrides=True)
        assert elevation_m == 4
        assert datum == "OTHER:WGS84"

    def test_get_raw_data_test_override_falls_back_to_default_feet(self, tmp_path):
        svc = _make_service(
            tmp_path,
            {
                "country_defaults": {},
                "airport_overrides": {},
                "test_overrides": {
                    "ABCD": {"vertical_datum": "OTHER:CUSTOM", "production_datum": "EGM_96"},
                },
                "datum_info": {},
            },
        )

        elevation_m, datum = svc._get_raw_elevation_data(
            "ABCD",
            default_elevation_ft=100,
            use_test_overrides=True,
        )
        assert elevation_m == 30
        assert datum == "OTHER:CUSTOM"

    def test_get_raw_data_uses_airport_override_elevation(self, tmp_path):
        svc = _make_service(
            tmp_path,
            {
                "country_defaults": {},
                "airport_overrides": {
                    "EGLL": {"vertical_datum": "EGM_96", "elevation_m": 24},
                },
                "datum_info": {},
            },
        )

        elevation_m, datum = svc._get_raw_elevation_data("EGLL")
        assert elevation_m == 24
        assert datum == "EGM_96"

    def test_get_raw_data_falls_back_to_default_elevation(self, tmp_path):
        svc = _make_service(tmp_path)
        elevation_m, datum = svc._get_raw_elevation_data("KLAX", default_elevation_ft=20, country_code="US")
        assert elevation_m == 6
        assert datum == "NAVD88"


class TestElevationServiceVersionFormatting:
    def test_get_elevation_data_applies_version_formatting(self, tmp_path):
        svc = _make_service(tmp_path)

        with patch("src.config.version_formatting.format_elevation", return_value=7.5):
            elevation_m, datum = svc.get_elevation_data("KLAX", default_elevation_ft=20, country_code="US")

        assert elevation_m == 7.5
        assert datum == "NAVD88"

    def test_get_elevation_data_formatting_error_keeps_raw_value(self, tmp_path):
        svc = _make_service(tmp_path)

        with patch("src.config.version_formatting.format_elevation", side_effect=RuntimeError("boom")):
            elevation_m, datum = svc.get_elevation_data("KLAX", default_elevation_ft=20, country_code="US")

        assert elevation_m == 6
        assert datum == "NAVD88"


class TestElevationServiceMetadataHelpers:
    def test_get_coordinates_override_returns_tuple(self, tmp_path):
        svc = _make_service(
            tmp_path,
            {
                "country_defaults": {},
                "airport_overrides": {
                    "KSEA": {"latitude": 47.449, "longitude": -122.309},
                },
                "datum_info": {},
            },
        )
        assert svc.get_coordinates_override("KSEA") == (47.449, -122.309)

    def test_get_coordinates_override_returns_none_when_missing(self, tmp_path):
        svc = _make_service(tmp_path)
        assert svc.get_coordinates_override("XXXX") is None

    def test_get_test_datum_override_and_missing(self, tmp_path):
        svc = _make_service(
            tmp_path,
            {
                "country_defaults": {},
                "airport_overrides": {},
                "test_overrides": {"KDEN": {"vertical_datum": "NAVD88"}},
                "datum_info": {},
            },
        )
        assert svc.get_test_datum_override("KDEN") == {"vertical_datum": "NAVD88"}
        assert svc.get_test_datum_override("XXXX") is None

    def test_get_datum_info_handles_other_prefix(self, tmp_path):
        svc = _make_service(
            tmp_path,
            {
                "country_defaults": {},
                "airport_overrides": {},
                "datum_info": {"NAVD88": {"name": "North American Vertical Datum"}},
            },
        )
        info = svc.get_datum_info("OTHER:NAVD88")
        assert info["name"].startswith("North American")

    def test_add_airport_override_sets_fields(self, tmp_path):
        svc = _make_service(tmp_path)
        svc.add_airport_override("KDEN", 1655, "NAVD88", source="test", notes="seed")
        assert svc.datum_map["airport_overrides"]["KDEN"]["elevation_m"] == 1655
        assert svc.datum_map["airport_overrides"]["KDEN"]["source"] == "test"


class TestElevationServicePersistenceAndSingleton:
    def test_save_datum_mapping_handles_write_error(self, tmp_path):
        svc = _make_service(tmp_path)
        with patch("builtins.open", side_effect=OSError("no write")):
            svc.save_datum_mapping()  # should not raise

    def test_get_elevation_service_singleton(self):
        original = elevation_module._elevation_service
        try:
            elevation_module._elevation_service = None
            first = get_elevation_service()
            second = get_elevation_service()
            assert first is second
        finally:
            elevation_module._elevation_service = original


class TestElevationServiceLoadErrors:
    def test_load_datum_mapping_file_not_found(self, monkeypatch):
        svc = ElevationService.__new__(ElevationService)
        svc.datum_map = {}
        real_open = open

        def fake_open(path, *args, **kwargs):
            if str(path).endswith("vertical_datum_map.json"):
                raise FileNotFoundError(path)
            return real_open(path, *args, **kwargs)

        monkeypatch.setattr("builtins.open", fake_open)
        svc._load_datum_mapping()
        assert svc.datum_map == {"country_defaults": {}, "airport_overrides": {}, "datum_info": {}}

    def test_load_datum_mapping_json_decode_error(self, monkeypatch):
        from io import StringIO

        svc = ElevationService.__new__(ElevationService)
        svc.datum_map = {}
        real_open = open

        def fake_open(path, *args, **kwargs):
            if str(path).endswith("vertical_datum_map.json"):
                return StringIO("{bad json")
            return real_open(path, *args, **kwargs)

        monkeypatch.setattr("builtins.open", fake_open)
        svc._load_datum_mapping()
        assert svc.datum_map == {"country_defaults": {}, "airport_overrides": {}, "datum_info": {}}


class TestElevationServiceDatumNormalization:
    def test_normalize_datum_other_prefix_passthrough(self, tmp_path):
        svc = _make_service(tmp_path)
        assert svc._normalize_datum_code("OTHER:CUSTOM") == "OTHER:CUSTOM"

    def test_normalize_datum_uses_datum_info_iwxxm_code(self, tmp_path):
        svc = _make_service(
            tmp_path,
            {
                "country_defaults": {},
                "airport_overrides": {},
                "datum_info": {"CGVD2013": {"iwxxm_code": "OTHER:CGVD2013"}},
            },
        )
        assert svc._normalize_datum_code("CGVD2013") == "OTHER:CGVD2013"


class TestElevationServiceAdditionalBranches:
    def test_get_raw_data_returns_none_elevation_without_default(self, tmp_path):
        svc = _make_service(tmp_path)
        elevation_m, datum = svc._get_raw_elevation_data("ZZZZ", country_code="XZ")
        assert elevation_m is None
        assert datum == "EGM_96"

    def test_get_raw_data_override_without_elevation_uses_datum_only(self, tmp_path):
        svc = _make_service(
            tmp_path,
            {
                "country_defaults": {},
                "airport_overrides": {"EGLL": {"vertical_datum": "EGM_96"}},
                "datum_info": {},
            },
        )
        elevation_m, datum = svc._get_raw_elevation_data("EGLL")
        assert elevation_m is None
        assert datum == "EGM_96"

    def test_get_coordinates_override_partial_coords_returns_none(self, tmp_path):
        svc = _make_service(
            tmp_path,
            {
                "country_defaults": {},
                "airport_overrides": {"KSEA": {"latitude": 47.449}},
                "datum_info": {},
            },
        )
        assert svc.get_coordinates_override("KSEA") is None

    def test_save_datum_mapping_writes_file(self, tmp_path, monkeypatch):
        svc = _make_service(tmp_path)
        written = {}

        real_open = open

        def fake_open(path, mode="r", *args, **kwargs):
            if "w" in mode and str(path).endswith("vertical_datum_map.json"):
                written["path"] = path
                return real_open(tmp_path / "saved.json", mode, *args, **kwargs)
            return real_open(path, mode, *args, **kwargs)

        monkeypatch.setattr("builtins.open", fake_open)
        svc.save_datum_mapping()

        assert written["path"] is not None
        saved = json.loads((tmp_path / "saved.json").read_text(encoding="utf-8"))
        assert "country_defaults" in saved


class TestElevationServiceVersionFormatting:
    def test_get_elevation_data_applies_version_formatting(self, tmp_path, monkeypatch):
        svc = _make_service(
            tmp_path,
            {
                "country_defaults": {},
                "airport_overrides": {"KJFK": {"elevation_m": 4.0, "vertical_datum": "NAVD88"}},
                "datum_info": {},
            },
        )

        monkeypatch.setattr(
            "src.config.version_formatting.format_elevation",
            lambda value, _version: round(value, 1),
        )

        elevation_m, datum = svc.get_elevation_data("KJFK", version="2025-2")
        assert elevation_m == 4.0
        assert datum == "NAVD88"

    def test_get_raw_elevation_data_test_override_uses_default_feet(self, tmp_path):
        svc = _make_service(
            tmp_path,
            {
                "country_defaults": {},
                "airport_overrides": {"KSEA": {"vertical_datum": "NAVD88"}},
                "datum_info": {},
                "test_overrides": {
                    "KSEA": {
                        "vertical_datum": "EGM_96",
                        "production_datum": "NAVD88",
                    }
                },
            },
        )

        elevation_m, datum = svc._get_raw_elevation_data("KSEA", default_elevation_ft=100, use_test_overrides=True)
        assert datum == "EGM_96"
        assert elevation_m == 30

    def test_get_elevation_data_keeps_raw_value_when_formatting_fails(self, tmp_path, monkeypatch):
        svc = _make_service(
            tmp_path,
            {
                "country_defaults": {},
                "airport_overrides": {"KJFK": {"elevation_m": 4.0, "vertical_datum": "NAVD88"}},
                "datum_info": {},
            },
        )

        monkeypatch.setattr(
            "src.config.version_formatting.format_elevation",
            lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("format failed")),
        )

        elevation_m, datum = svc.get_elevation_data("KJFK", version="2025-2")
        assert elevation_m == 4.0
        assert datum == "NAVD88"

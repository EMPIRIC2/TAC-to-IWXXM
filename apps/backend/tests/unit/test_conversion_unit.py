"""High-impact unit tests for conversion utility branches."""

from __future__ import annotations

import sys
import types
from types import SimpleNamespace

import pytest

from src.utilities import conversion as conv


def test_extract_icao_from_tac_prefers_parser(monkeypatch):
    monkeypatch.setattr(conv, "extract_airport_code", lambda _tac: "KJFK")

    assert conv._extract_icao_from_tac("METAR KJFK 010000Z") == "KJFK"


def test_extract_icao_from_tac_regex_fallback(monkeypatch):
    monkeypatch.setattr(conv, "extract_airport_code", lambda _tac: None)

    assert conv._extract_icao_from_tac("random KDEN text") == "KDEN"
    assert conv._extract_icao_from_tac("no airport id") is None


def test_convert_metar_tac_wrapper_calls_with_metadata(monkeypatch):
    monkeypatch.setattr(
        conv,
        "convert_metar_tac_with_metadata",
        lambda tac_text, iwxxm_version=None, validate=False: (f"xml:{tac_text}:{iwxxm_version}:{validate}", None),
    )

    result = conv.convert_metar_tac("METAR KJFK", iwxxm_version="2025-2")

    assert result.startswith("xml:METAR KJFK:2025-2:False")


def test_load_aerodrome_db_returns_none_when_missing(monkeypatch):
    class _FakePath:
        def __init__(self, value):
            self.value = value
            self.parents = [self] * 6

        def resolve(self):
            return self

        def __truediv__(self, _other):
            return self

        def exists(self):
            return False

    monkeypatch.setattr(conv.pathlib, "Path", lambda _v: _FakePath(_v))

    assert conv._load_aerodrome_db() is None


def test_lookup_aerodrome_prefers_validator(monkeypatch):
    fake_airport = SimpleNamespace(
        name="John F Kennedy",
        iata="JFK",
        country="US",
        coordinates=SimpleNamespace(latitude=40.6413, longitude=-73.7781, elevation_ft=13),
    )
    fake_validator = SimpleNamespace(get_airport=lambda _icao: fake_airport)

    fake_elevation = SimpleNamespace(
        get_coordinates_override=lambda _icao: (40.64127777, -73.77813888),
        get_elevation_data=lambda **_kwargs: (4.0, "EGM_96"),
        datum_map={"airport_overrides": {"KJFK": {"name": "JFK AIRPORT", "iata": "JFK", "designator": "ALT"}}},
    )

    monkeypatch.setattr("src.schemas.airport.get_airport_validator", lambda: fake_validator)
    monkeypatch.setattr("src.utilities.elevation_service.get_elevation_service", lambda: fake_elevation)

    result = conv._lookup_aerodrome("KJFK")

    assert result is not None
    assert result["name"] == "JFK AIRPORT"
    assert result["iataID"] == "JFK"
    assert result["alternate"] == "ALT"
    assert result["vertical_datum"] == "EGM_96"


def test_lookup_aerodrome_falls_back_to_gifts_table(monkeypatch, tmp_path):
    db = tmp_path / "aerodromes.tbl"
    db.write_text("KDEN|DEN|ALTD|Denver Intl|39.8617|-104.6731|1655\n", encoding="utf-8")

    monkeypatch.setattr(conv, "_load_aerodrome_db", lambda: db)
    monkeypatch.setattr("src.schemas.airport.get_airport_validator", lambda: SimpleNamespace(get_airport=lambda _icao: None))

    result = conv._lookup_aerodrome("KDEN")

    assert result is not None
    assert result["name"] == "Denver Intl"
    assert result["position"] == "39.8617 -104.6731 1655"


def test_convert_with_metadata_adapter_init_fail(monkeypatch):
    def _raise_import(*_args, **_kwargs):
        raise ImportError("no adapter")

    monkeypatch.setattr("src.utilities.gifts_adapter.get_decoder", _raise_import)

    with pytest.raises(conv.ConversionError, match="Failed to initialize decoder/encoder"):
        conv.convert_metar_tac_with_metadata("METAR KJFK 010000Z")


def test_convert_with_metadata_invalid_reference_time(monkeypatch):
    monkeypatch.setattr("src.utilities.gifts_adapter.get_decoder", lambda version=None: SimpleNamespace(decode=lambda _tac: {"ident": {"str": "KJFK"}}))
    monkeypatch.setattr("src.utilities.gifts_adapter.get_encoder", lambda version=None: SimpleNamespace(encode=lambda _decoded, _tac: SimpleNamespace(tag="root")))
    monkeypatch.setattr(conv, "_lookup_aerodrome", lambda *_args, **_kwargs: None)

    with pytest.raises(conv.ConversionError, match="Invalid reference_time format"):
        conv.convert_metar_tac_with_metadata("METAR KJFK 010000Z", reference_time="not-a-date", validate=False)


def test_convert_with_metadata_encoder_none(monkeypatch):
    monkeypatch.setattr("src.utilities.gifts_adapter.get_decoder", lambda version=None: SimpleNamespace(decode=lambda _tac: {"ident": {"str": "KJFK"}}))
    monkeypatch.setattr("src.utilities.gifts_adapter.get_encoder", lambda version=None: SimpleNamespace(encode=lambda _decoded, _tac: None))
    monkeypatch.setattr(conv, "_lookup_aerodrome", lambda *_args, **_kwargs: None)

    with pytest.raises(conv.ConversionError, match="Encoder returned None"):
        conv.convert_metar_tac_with_metadata("METAR KJFK 010000Z", validate=False)


def test_convert_with_metadata_serialization_error(monkeypatch):
    monkeypatch.setattr("src.utilities.gifts_adapter.get_decoder", lambda version=None: SimpleNamespace(decode=lambda _tac: {"ident": {"str": "KJFK"}}))
    monkeypatch.setattr("src.utilities.gifts_adapter.get_encoder", lambda version=None: SimpleNamespace(encode=lambda _decoded, _tac: SimpleNamespace(tag="root")))
    monkeypatch.setattr(conv.ET, "tostring", lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("boom")))
    monkeypatch.setattr(conv, "_lookup_aerodrome", lambda *_args, **_kwargs: None)

    with pytest.raises(conv.ConversionError, match="Serialization error"):
        conv.convert_metar_tac_with_metadata("METAR KJFK 010000Z", validate=False)


def test_convert_with_metadata_validation_raise_on_error(monkeypatch):
    decoder = SimpleNamespace(decode=lambda _tac: {"ident": {"str": "KJFK"}})
    encoder = SimpleNamespace(encode=lambda _decoded, _tac: SimpleNamespace(tag="root"))
    monkeypatch.setattr("src.utilities.gifts_adapter.get_decoder", lambda version=None: decoder)
    monkeypatch.setattr("src.utilities.gifts_adapter.get_encoder", lambda version=None: encoder)
    monkeypatch.setattr(conv, "_lookup_aerodrome", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(conv.ET, "tostring", lambda *_args, **_kwargs: "<iwxxm:METAR/>")

    bad_issue = SimpleNamespace(level=SimpleNamespace(value="ERROR"), code="E1", message="failed")
    fake_result = SimpleNamespace(is_valid=False, layers_passed=[], layers_failed=["XML_SCHEMA"], all_issues=[bad_issue])
    fake_orchestrator = SimpleNamespace(validate_complete=lambda **_kwargs: fake_result)
    monkeypatch.setattr("src.services.validation_orchestrator.get_validation_orchestrator", lambda: fake_orchestrator)

    with pytest.raises(conv.ConversionError, match="Validation failed with 1 error"):
        conv.convert_metar_tac_with_metadata(
            "METAR KJFK 010000Z",
            validate=True,
            raise_on_validation_error=True,
        )


def test_convert_with_metadata_validation_continue_on_error(monkeypatch):
    decoder = SimpleNamespace(decode=lambda _tac: {"ident": {"str": "KJFK"}})
    encoder = SimpleNamespace(encode=lambda _decoded, _tac: SimpleNamespace(tag="root"))
    monkeypatch.setattr("src.utilities.gifts_adapter.get_decoder", lambda version=None: decoder)
    monkeypatch.setattr("src.utilities.gifts_adapter.get_encoder", lambda version=None: encoder)
    monkeypatch.setattr(conv, "_lookup_aerodrome", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(conv.ET, "tostring", lambda *_args, **_kwargs: "<iwxxm:METAR/>")

    bad_issue = SimpleNamespace(level=SimpleNamespace(value="ERROR"), code="E1", message="failed")
    fake_result = SimpleNamespace(is_valid=False, layers_passed=[], layers_failed=["XML_SCHEMA"], all_issues=[bad_issue])
    fake_orchestrator = SimpleNamespace(validate_complete=lambda **_kwargs: fake_result)
    monkeypatch.setattr("src.services.validation_orchestrator.get_validation_orchestrator", lambda: fake_orchestrator)

    xml, validation_result = conv.convert_metar_tac_with_metadata(
        "METAR KJFK 010000Z",
        validate=True,
        raise_on_validation_error=False,
    )

    assert xml.startswith("<?xml version=\"1.0\"?>")
    assert validation_result is not None
def test_load_aerodrome_db_finds_repo_candidate(monkeypatch, tmp_path):
    utilities_dir = tmp_path / "backend" / "src" / "utilities"
    utilities_dir.mkdir(parents=True)
    fake_file = utilities_dir / "conversion.py"
    fake_file.write_text("# test", encoding="utf-8")
    db_path = tmp_path / "GIFTs" / "gifts" / "database" / "aerodromes.tbl"
    db_path.parent.mkdir(parents=True)
    db_path.write_text("KDEN|DEN\n", encoding="utf-8")

    monkeypatch.setattr(conv, "__file__", str(fake_file))

    found = conv._load_aerodrome_db()

    assert found == db_path


def test_lookup_aerodrome_csv_exception_falls_back_to_gifts_table(monkeypatch, tmp_path):
    db = tmp_path / "aerodromes.tbl"
    db.write_text("# comment\nKDEN|DEN|||||\n", encoding="utf-8")

    monkeypatch.setattr(conv, "_load_aerodrome_db", lambda: db)

    def _raise_validator():
        raise RuntimeError("csv unavailable")

    monkeypatch.setattr("src.schemas.airport.get_airport_validator", _raise_validator)

    result = conv._lookup_aerodrome("KDEN")

    assert result == {
        "name": "",
        "iataID": "DEN",
        "alternate": "",
        "position": "",
    }


def test_lookup_aerodrome_returns_none_for_malformed_table(monkeypatch):
    class _BrokenDb:
        def read_text(self, encoding="utf-8"):
            raise ValueError("broken table")

    monkeypatch.setattr(conv, "_load_aerodrome_db", lambda: _BrokenDb())
    monkeypatch.setattr(
        "src.schemas.airport.get_airport_validator",
        lambda: SimpleNamespace(get_airport=lambda _icao: None),
    )

    assert conv._lookup_aerodrome("KDEN") is None


def test_lookup_aerodrome_without_coordinates_uses_defaults(monkeypatch):
    fake_airport = SimpleNamespace(name="Test Field", iata=None, coordinates=None)
    fake_validator = SimpleNamespace(get_airport=lambda _icao: fake_airport)
    fake_elevation = SimpleNamespace(
        datum_map={"airport_overrides": {}},
        get_coordinates_override=lambda _icao: None,
        get_elevation_data=lambda **_kwargs: (None, "EGM_96"),
    )

    monkeypatch.setattr("src.schemas.airport.get_airport_validator", lambda: fake_validator)
    monkeypatch.setattr("src.utilities.elevation_service.get_elevation_service", lambda: fake_elevation)

    result = conv._lookup_aerodrome("TEST")

    assert result == {
        "name": "TEST FIELD",
        "iataID": "",
        "alternate": "",
        "position": "",
        "vertical_datum": "EGM_96",
    }


def test_lookup_aerodrome_uses_database_coordinates_when_no_override(monkeypatch):
    fake_airport = SimpleNamespace(
        name="Test Field",
        iata="TST",
        country="US",
        coordinates=SimpleNamespace(latitude=12.3, longitude=45.6, elevation_ft=100),
    )
    fake_validator = SimpleNamespace(get_airport=lambda _icao: fake_airport)
    fake_elevation = SimpleNamespace(
        datum_map={"airport_overrides": {}},
        get_coordinates_override=lambda _icao: None,
        get_elevation_data=lambda **_kwargs: (None, "LOCAL_DATUM"),
    )

    monkeypatch.setattr("src.schemas.airport.get_airport_validator", lambda: fake_validator)
    monkeypatch.setattr("src.utilities.elevation_service.get_elevation_service", lambda: fake_elevation)

    result = conv._lookup_aerodrome("TEST")

    assert result == {
        "name": "TEST FIELD",
        "iataID": "TST",
        "alternate": "",
        "position": "12.30000000 45.60000000",
        "vertical_datum": "LOCAL_DATUM",
    }




def test_convert_with_metadata_success_injects_metadata_and_runs_default_validation(monkeypatch):
    captured = {}

    def _decode(_tac):
        import time

        captured["gmtime_year"] = time.gmtime().tm_year
        captured["timestamp_year"] = time.gmtime(time.time()).tm_year
        return {"ident": {"str": "KJFK", "index": 7}}

    def _encode(decoded, tac_text):
        captured["decoded_ident"] = decoded["ident"].copy()
        captured["tac_text"] = tac_text
        return SimpleNamespace(tag="root")

    fake_result = SimpleNamespace(is_valid=True, layers_passed=["XML_SCHEMA"], layers_failed=[], all_issues=[])

    def _validate_complete(**kwargs):
        captured["validation_kwargs"] = kwargs
        return fake_result

    fake_orchestrator = SimpleNamespace(validate_complete=_validate_complete)

    fake_xml_config = SimpleNamespace(verticalDatum=None)
    fake_common = types.ModuleType("gifts.common")
    fake_common.xmlConfig = fake_xml_config
    fake_gifts = types.ModuleType("gifts")
    fake_gifts.common = fake_common

    monkeypatch.setattr("src.utilities.gifts_adapter.get_decoder", lambda version=None: SimpleNamespace(decode=_decode))
    monkeypatch.setattr("src.utilities.gifts_adapter.get_encoder", lambda version=None: SimpleNamespace(encode=_encode))
    monkeypatch.setattr(
        conv,
        "_lookup_aerodrome",
        lambda *_args, **_kwargs: {
            "name": "JFK AIRPORT",
            "alternate": "ALT",
            "iataID": "JFK",
            "position": "40.0 -73.0 4.0",
            "vertical_datum": "EGM_08",
        },
    )
    monkeypatch.setattr(
        "src.services.validation_orchestrator.get_validation_orchestrator",
        lambda: fake_orchestrator,
    )
    monkeypatch.setattr(conv.ET, "tostring", lambda *_args, **_kwargs: "<iwxxm:METAR/>")

    with pytest.MonkeyPatch.context() as path_patch, pytest.MonkeyPatch.context() as sys_patch:
        path_patch.setattr(conv, "__file__", "/tmp/backend/src/utilities/conversion.py")
        sys_patch.setitem(sys.modules, "gifts", fake_gifts)
        sys_patch.setitem(sys.modules, "gifts.common", fake_common)

        xml, validation_result = conv.convert_metar_tac_with_metadata(
            "METAR KJFK 010000Z",
            iwxxm_version="2025-2",
            reference_time="2024-05-01T12:00:00Z",
            validate=True,
        )

    assert xml == "<?xml version=\"1.0\"?>\n<iwxxm:METAR/>"
    assert validation_result is fake_result
    assert captured["gmtime_year"] == 2024
    assert captured["timestamp_year"] == 2024
    assert list(captured["decoded_ident"].keys()) == ["str", "name", "alternate", "iataID", "position", "index"]
    assert captured["decoded_ident"]["name"] == "JFK AIRPORT"
    assert captured["validation_kwargs"]["layers"] == [
        "XML_WELLFORMED",
        "XML_SCHEMA",
        "SCHEMATRON",
        "WMO_CODELISTS",
    ]
    assert fake_xml_config.verticalDatum == "EGM_08"


def test_convert_with_metadata_logs_vertical_datum_warning_and_uses_custom_layers(monkeypatch, caplog):
    decoder = SimpleNamespace(decode=lambda _tac: {"ident": {"str": "KJFK", "index": 1}})
    encoder = SimpleNamespace(encode=lambda _decoded, _tac: SimpleNamespace(tag="root"))
    captured = {}

    def _validate_complete(**kwargs):
        captured.update(kwargs)
        return SimpleNamespace(is_valid=True, layers_passed=kwargs["layers"], layers_failed=[], all_issues=[])

    monkeypatch.setattr("src.utilities.gifts_adapter.get_decoder", lambda version=None: decoder)
    monkeypatch.setattr("src.utilities.gifts_adapter.get_encoder", lambda version=None: encoder)
    monkeypatch.setattr(
        conv,
        "_lookup_aerodrome",
        lambda *_args, **_kwargs: {
            "name": "JFK AIRPORT",
            "alternate": "",
            "iataID": "",
            "position": "40.0 -73.0",
            "vertical_datum": "EGM_08",
        },
    )
    monkeypatch.setattr(conv.ET, "tostring", lambda *_args, **_kwargs: "<iwxxm:METAR/>")
    monkeypatch.setattr(
        "src.services.validation_orchestrator.get_validation_orchestrator",
        lambda: SimpleNamespace(validate_complete=_validate_complete),
    )

    import builtins

    original_import = builtins.__import__

    def _import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "gifts.common":
            raise ModuleNotFoundError("missing gifts.common")
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", _import)

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(conv, "__file__", "/tmp/backend/src/utilities/conversion.py")

        xml, validation_result = conv.convert_metar_tac_with_metadata(
            "METAR KJFK 010000Z",
            validate=True,
            validation_layers=["XML_SCHEMA"],
        )

    assert xml.startswith("<?xml version=\"1.0\"?>")
    assert validation_result is not None
    assert captured["layers"] == ["XML_SCHEMA"]
    assert "Failed to set vertical datum" in caplog.text



def test_convert_with_metadata_without_dict_ident_skips_lookup(monkeypatch):
    decoder = SimpleNamespace(decode=lambda _tac: {"ident": "KJFK"})
    encoder = SimpleNamespace(encode=lambda _decoded, _tac: SimpleNamespace(tag="root"))
    lookup_calls = []

    monkeypatch.setattr("src.utilities.gifts_adapter.get_decoder", lambda version=None: decoder)
    monkeypatch.setattr("src.utilities.gifts_adapter.get_encoder", lambda version=None: encoder)
    monkeypatch.setattr(conv, "_lookup_aerodrome", lambda *_args, **_kwargs: lookup_calls.append(True))
    monkeypatch.setattr(conv.ET, "tostring", lambda *_args, **_kwargs: "<iwxxm:METAR/>")

    xml, validation_result = conv.convert_metar_tac_with_metadata("METAR KJFK 010000Z", validate=False)

    assert xml.startswith('<?xml version="1.0"?>')
    assert validation_result is None
    assert lookup_calls == []


def test_convert_with_metadata_validation_exception_returns_none(monkeypatch):
    decoder = SimpleNamespace(decode=lambda _tac: {"ident": {"str": "KJFK"}})
    encoder = SimpleNamespace(encode=lambda _decoded, _tac: SimpleNamespace(tag="root"))
    failing_orchestrator = SimpleNamespace(validate_complete=lambda **_kwargs: (_ for _ in ()).throw(RuntimeError("boom")))

    monkeypatch.setattr("src.utilities.gifts_adapter.get_decoder", lambda version=None: decoder)
    monkeypatch.setattr("src.utilities.gifts_adapter.get_encoder", lambda version=None: encoder)
    monkeypatch.setattr(conv, "_lookup_aerodrome", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(conv.ET, "tostring", lambda *_args, **_kwargs: "<iwxxm:METAR/>")
    monkeypatch.setattr(
        "src.services.validation_orchestrator.get_validation_orchestrator",
        lambda: failing_orchestrator,
    )

    xml, validation_result = conv.convert_metar_tac_with_metadata(
        "METAR KJFK 010000Z",
        validate=True,
        raise_on_validation_error=False,
    )

    assert xml.startswith('<?xml version="1.0"?>')
    assert validation_result is None


# ---------------------------------------------------------------------------
# Additional branch coverage tests
# ---------------------------------------------------------------------------


    """Shallow __file__ path exhausts parents, triggering IndexError break (covers 146-147)."""
    monkeypatch.setattr(conv, "__file__", "/conversion.py")

    # /app/GIFTs/... almost certainly doesn't exist in this environment
    result = conv._load_aerodrome_db()

    assert result is None


def test_lookup_aerodrome_override_data_missing_all_keys(monkeypatch):
    """Override entry present but has no name/iata/designator keys (covers 228->230, 230->232, 232->234)."""
    fake_airport = SimpleNamespace(
        name="TestAirport",
        iata="TST",
        country="US",
        coordinates=SimpleNamespace(latitude=1.0, longitude=2.0, elevation_ft=10),
    )
    fake_validator = SimpleNamespace(get_airport=lambda _icao: fake_airport)
    fake_elevation = SimpleNamespace(
        datum_map={"airport_overrides": {"KTEST": {}}},  # no name/iata/designator
        get_coordinates_override=lambda _icao: None,
        get_elevation_data=lambda **_kwargs: (None, "EGM_96"),
    )

    monkeypatch.setattr("src.schemas.airport.get_airport_validator", lambda: fake_validator)
    monkeypatch.setattr("src.utilities.elevation_service.get_elevation_service", lambda: fake_elevation)

    result = conv._lookup_aerodrome("KTEST")

    assert result is not None
    # Falls back to original airport data since override has no matching keys
    assert result["name"] == "TESTAIRPORT"
    assert result["iataID"] == "TST"
    assert result["alternate"] == ""


def test_lookup_aerodrome_returns_none_when_db_is_none(monkeypatch):
    """_load_aerodrome_db returns None -> function returns None (covers line 250)."""
    monkeypatch.setattr(conv, "_load_aerodrome_db", lambda: None)
    monkeypatch.setattr(
        "src.schemas.airport.get_airport_validator",
        lambda: SimpleNamespace(get_airport=lambda _icao: None),
    )

    assert conv._lookup_aerodrome("XXXX") is None


def test_lookup_aerodrome_icao_not_found_in_gifts_table(monkeypatch, tmp_path):
    """ICAO absent from table - loop exhausts then returns None (covers 258->252, 275)."""
    db = tmp_path / "aerodromes.tbl"
    db.write_text("KDEN|DEN|ALTD|Denver Intl|39.8617|-104.6731|1655\n", encoding="utf-8")

    monkeypatch.setattr(conv, "_load_aerodrome_db", lambda: db)
    monkeypatch.setattr(
        "src.schemas.airport.get_airport_validator",
        lambda: SimpleNamespace(get_airport=lambda _icao: None),
    )

    assert conv._lookup_aerodrome("XXXX") is None


def test_convert_with_metadata_empty_meta_fields_covers_skip_branches(monkeypatch):
    """Decoded ident without 'str' + meta with all empty fields covers:
    406->412 (str absent), 412->414 (name empty), 418->422 (position empty), 429->446 (no vert_datum).
    """
    decoded_state = {"ident": {"index": 7}}  # no 'str' key

    # meta without vertical_datum and with empty string fields
    meta_template = {"name": "", "alternate": "", "iataID": "TST", "position": ""}

    monkeypatch.setattr(
        "src.utilities.gifts_adapter.get_decoder",
        lambda version=None: SimpleNamespace(decode=lambda _tac: decoded_state),
    )
    monkeypatch.setattr(
        "src.utilities.gifts_adapter.get_encoder",
        lambda version=None: SimpleNamespace(encode=lambda _decoded, _tac: SimpleNamespace(tag="root")),
    )
    monkeypatch.setattr(conv, "_lookup_aerodrome", lambda *_a, **_kw: dict(meta_template))
    monkeypatch.setattr(conv.ET, "tostring", lambda *_a, **_kw: "<iwxxm:METAR/>")

    xml, _ = conv.convert_metar_tac_with_metadata("METAR KJFK 010000Z", validate=False)

    assert xml.startswith("<?xml version=\"1.0\"?>")
    # Only iataID (non-empty) and original 'index' should survive in rebuilt ident
    assert decoded_state["ident"].get("iataID") == "TST"
    assert "name" not in decoded_state["ident"]
    assert "position" not in decoded_state["ident"]
    assert "str" not in decoded_state["ident"]


def test_convert_with_metadata_gifts_root_exists_inserts_to_sys_path(monkeypatch, tmp_path):
    """gifts_root directory exists and not in sys.path -> inserts to path (covers line 438)."""
    # Build path so Path(__file__).parent^4 / GIFTs == tmp_path/a/GIFTs
    sub = tmp_path / "a" / "b" / "c" / "d"
    sub.mkdir(parents=True)
    gifts_root = tmp_path / "a" / "GIFTs"
    gifts_root.mkdir()
    gifts_root_str = str(gifts_root)

    # Expose a fake gifts.common so the import succeeds after path insert
    fake_xml_config = SimpleNamespace(verticalDatum=None)
    fake_common = types.ModuleType("gifts.common")
    fake_common.xmlConfig = fake_xml_config

    # Keep sys.path clean so the insert condition fires
    clean_path = [p for p in sys.path if p != gifts_root_str]
    monkeypatch.setattr(sys, "path", clean_path)
    monkeypatch.setitem(sys.modules, "gifts.common", fake_common)

    meta = {"name": "JFK", "alternate": "", "iataID": "", "position": "", "vertical_datum": "EGM_08"}
    decoded = {"ident": {"str": "KJFK"}}

    monkeypatch.setattr(conv, "__file__", str(sub / "conversion.py"))
    monkeypatch.setattr(
        "src.utilities.gifts_adapter.get_decoder",
        lambda version=None: SimpleNamespace(decode=lambda _tac: decoded),
    )
    monkeypatch.setattr(
        "src.utilities.gifts_adapter.get_encoder",
        lambda version=None: SimpleNamespace(encode=lambda _d, _t: SimpleNamespace(tag="root")),
    )
    monkeypatch.setattr(conv, "_lookup_aerodrome", lambda *_a, **_kw: dict(meta))
    monkeypatch.setattr(conv.ET, "tostring", lambda *_a, **_kw: "<iwxxm:METAR/>")

    xml, _ = conv.convert_metar_tac_with_metadata("METAR KJFK 010000Z", validate=False)

    assert xml.startswith("<?xml version=\"1.0\"?>")
    # Vertical datum should have been set on the fake config object
    assert fake_xml_config.verticalDatum == "EGM_08"
    # gifts_root was inserted into sys.path
    assert gifts_root_str in sys.path

"""Unit tests for tac2iwxxm-backed conversion (T4.7 cutover)."""

from __future__ import annotations

import pytest
from src.utilities.conversion import (
    ConversionError,
    _detect_product,
    _extract_icao_from_tac,
    convert_metar_tac,
    convert_metar_tac_with_metadata,
)


def test_extract_icao_from_tac() -> None:
    assert _extract_icao_from_tac("METAR KJFK 231751Z NIL=") == "KJFK"


def test_detect_product_speci() -> None:
    assert _detect_product("SPECI KJFK 232045Z 18012KT 5SM 15/07 A3005=") == "SPECI"


def test_detect_product_default_metar() -> None:
    assert _detect_product("KJFK 231751Z NIL=") == "METAR"


def test_detect_product_lwis_maps_to_metar() -> None:
    assert _detect_product("LWIS CYLA 292000Z AUTO 31006KT M00/M02 A2926=") == "METAR"


def test_detect_product_sawr_maps_to_metar() -> None:
    assert _detect_product("SAWR CYXX 231800Z AUTO 24010KT 5SM FEW030 M05/M10 A2998=") == "METAR"


def test_convert_metar_tac_with_metadata_ok() -> None:
    xml, validation = convert_metar_tac_with_metadata(
        "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005=",
        validate=False,
    )
    assert "<?xml" in xml
    assert "iwxxm:METAR" in xml or "METAR" in xml
    assert validation is None


def test_convert_metar_tac_deprecated() -> None:
    with pytest.warns(DeprecationWarning, match=r"."):
        xml = convert_metar_tac("METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005=")
    assert "<?xml" in xml


def test_convert_parse_error_raises() -> None:
    with pytest.raises(ConversionError, match="Conversion failed"):
        convert_metar_tac_with_metadata("NOT A REPORT", validate=False)


def test_convert_iwxxm_us_profile() -> None:
    xml, _ = convert_metar_tac_with_metadata(
        "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005 RMK AO2 SLP149=",
        validate=False,
        profile="iwxxm_us",
    )
    assert "iwxxm-us" in xml or "www.weather.gov/iwxxm-us" in xml


def test_convert_tac2iwxxm_import_error(monkeypatch: pytest.MonkeyPatch) -> None:
    import builtins

    real_import = builtins.__import__

    def _boom(name, *args, **kwargs):
        if name == "tac2iwxxm" or name.startswith("tac2iwxxm."):
            raise ImportError("no tac2iwxxm")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _boom)
    with pytest.raises(ConversionError, match="tac2iwxxm unavailable"):
        convert_metar_tac_with_metadata(
            "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005=",
            validate=False,
        )


def test_extract_icao_regex_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    import src.utilities.conversion as conv

    monkeypatch.setattr(conv, "extract_airport_code", lambda _tac: None)
    assert _extract_icao_from_tac("METAR KJFK 231751Z NIL=") == "KJFK"
    assert _extract_icao_from_tac("????") is None


def test_convert_lenient_false_skips_normalization(monkeypatch: pytest.MonkeyPatch) -> None:
    import src.utilities.conversion as conv

    calls: list[str] = []

    def _track(tac: str) -> tuple[str, list[dict[str, object]]]:
        calls.append(tac)
        return tac, []

    monkeypatch.setattr(conv, "normalize_recent_weather_for_tac", _track)
    convert_metar_tac_with_metadata(
        "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005=",
        validate=False,
        lenient=False,
    )
    assert calls == []


def test_convert_lenient_logs_normalization(monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture) -> None:
    import logging

    import src.utilities.conversion as conv

    monkeypatch.setattr(
        conv,
        "normalize_recent_weather_for_tac",
        lambda tac: (
            tac,
            [{"original": "RASN", "index": 3, "replacement": "RA", "rule": "truncate"}],
        ),
    )
    with caplog.at_level(logging.INFO):
        convert_metar_tac_with_metadata(
            "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005=",
            validate=False,
            lenient=True,
        )
    assert any("recent-weather pre-normalization" in r.message for r in caplog.records)


def test_convert_prepends_xml_declaration(monkeypatch: pytest.MonkeyPatch) -> None:
    from types import SimpleNamespace

    import tac2iwxxm

    def _fake_convert(*_a, **_k):
        return SimpleNamespace(ok=True, xml="<iwxxm:METAR/>", issues=[])

    monkeypatch.setattr(tac2iwxxm, "convert", _fake_convert)
    xml, _ = convert_metar_tac_with_metadata(
        "METAR KJFK 231751Z NIL=",
        validate=False,
    )
    assert xml.lstrip().startswith("<?xml")
    assert "<iwxxm:METAR/>" in xml


def test_convert_validation_pass_and_fail_paths(monkeypatch: pytest.MonkeyPatch) -> None:
    from src.schemas.validation import ValidationIssue, ValidationLayer, ValidationLevel
    from src.services import validation_orchestrator as orch_mod
    from src.services.validation_orchestrator import ComprehensiveValidationResult

    class _Orch:
        def __init__(self, result: ComprehensiveValidationResult) -> None:
            self._result = result

        def validate_complete(self, **_kwargs: object) -> ComprehensiveValidationResult:
            return self._result

    ok = ComprehensiveValidationResult(
        is_valid=True,
        layers_run=[ValidationLayer.XML_WELLFORMED],
        layers_passed=[ValidationLayer.XML_WELLFORMED],
        layers_failed=[],
        all_issues=[],
    )
    monkeypatch.setattr(orch_mod, "get_validation_orchestrator", lambda: _Orch(ok))
    xml, result = convert_metar_tac_with_metadata(
        "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005=",
        validate=True,
        validation_layers=["XML_WELLFORMED"],
    )
    assert "<?xml" in xml
    assert result is not None
    assert result.is_valid is True

    fail = ComprehensiveValidationResult(
        is_valid=False,
        layers_run=[ValidationLayer.XML_SCHEMA],
        layers_passed=[],
        layers_failed=[ValidationLayer.XML_SCHEMA],
        all_issues=[
            ValidationIssue(
                layer=ValidationLayer.XML_SCHEMA,
                level=ValidationLevel.ERROR,
                message="bad schema",
                code="XSD",
            )
        ],
    )
    monkeypatch.setattr(orch_mod, "get_validation_orchestrator", lambda: _Orch(fail))
    with pytest.raises(ConversionError, match="Validation failed"):
        convert_metar_tac_with_metadata(
            "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005=",
            validate=True,
            raise_on_validation_error=True,
            validation_layers=[ValidationLayer.XML_SCHEMA],
        )


def test_convert_validation_exception_swallowed_or_raised(monkeypatch: pytest.MonkeyPatch) -> None:
    from src.services import validation_orchestrator as orch_mod

    class _Boom:
        def validate_complete(self, **_kwargs: object) -> None:
            raise RuntimeError("orchestrator down")

    monkeypatch.setattr(orch_mod, "get_validation_orchestrator", lambda: _Boom())
    xml, result = convert_metar_tac_with_metadata(
        "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005=",
        validate=True,
        raise_on_validation_error=False,
    )
    assert "<?xml" in xml
    assert result is None

    with pytest.raises(ConversionError, match="Validation error"):
        convert_metar_tac_with_metadata(
            "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005=",
            validate=True,
            raise_on_validation_error=True,
        )


def test_soft_preview_prepends_xml_declaration(monkeypatch: pytest.MonkeyPatch) -> None:
    """Soft-preview path prepends <?xml when tac2iwxxm returns a bare root element."""
    from types import SimpleNamespace

    import tac2iwxxm

    fake_result = SimpleNamespace(
        ok=False,
        xml="<iwxxm:METAR xmlns:iwxxm='http://icao.int/iwxxm/2023-1'/>",
        issues=[
            SimpleNamespace(code="PARSE_ERROR", message="bad", start=0, end=5),
        ],
    )
    monkeypatch.setattr(tac2iwxxm, "convert", lambda *a, **k: fake_result)

    soft: dict = {}
    xml, _ = convert_metar_tac_with_metadata(
        "INVALID TEXT",
        validate=False,
        preview=True,
        soft_preview_out=soft,
    )
    assert soft.get("ok") is False
    assert soft.get("failed_spans")
    assert xml.lstrip().startswith("<?xml")

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


def test_convert_metar_tac_with_metadata_ok() -> None:
    xml, validation = convert_metar_tac_with_metadata(
        "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005=",
        validate=False,
    )
    assert "<?xml" in xml
    assert "iwxxm:METAR" in xml or "METAR" in xml
    assert validation is None


def test_convert_metar_tac_deprecated() -> None:
    with pytest.warns(DeprecationWarning):
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

    def _boom(name, *args, **kwargs):  # noqa: ANN001
        if name == "tac2iwxxm" or name.startswith("tac2iwxxm."):
            raise ImportError("no tac2iwxxm")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _boom)
    with pytest.raises(ConversionError, match="tac2iwxxm unavailable"):
        convert_metar_tac_with_metadata(
            "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005=",
            validate=False,
        )

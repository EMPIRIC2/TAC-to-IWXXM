"""Unit coverage for convert / METAR-SPECI parse edge paths (T4.2)."""

from __future__ import annotations

import pytest

from tac2iwxxm import ConvertError, convert
from tac2iwxxm.products.metar_speci import parse_metar_speci
from tac2iwxxm.profiles.annex3 import emit_metar_speci_annex3


def test_convert_error_is_value_error() -> None:
    err = ConvertError("boom")
    assert isinstance(err, ValueError)
    assert str(err) == "boom"


def test_convert_unsupported_product() -> None:
    result = convert("METAR KJFK 231751Z NIL=", product="TAF")
    assert result.ok is False
    assert result.issues[0].code == "UNSUPPORTED_PRODUCT"


def test_convert_unsupported_profile() -> None:
    result = convert(
        "METAR KJFK 231751Z NIL=",
        product="METAR",
        profile="iwxxm_us",
    )
    assert result.ok is False
    assert result.issues[0].code == "UNSUPPORTED_PROFILE"


def test_convert_parse_error_returns_ok_false() -> None:
    result = convert("NOT A REPORT", product="METAR")
    assert result.ok is False
    assert result.issues[0].code == "PARSE_ERROR"


def test_parse_product_mismatch() -> None:
    with pytest.raises(ValueError, match="product mismatch"):
        parse_metar_speci("METAR KJFK 231751Z NIL=", product="SPECI")


def test_parse_missing_wind() -> None:
    with pytest.raises(ValueError, match="missing wind"):
        parse_metar_speci("METAR KJFK 231751Z 10SM 15/07 A3005=", product="METAR")


def test_parse_missing_visibility() -> None:
    with pytest.raises(ValueError, match="missing visibility"):
        parse_metar_speci("METAR KJFK 231751Z 18012KT 15/07 A3005=", product="METAR")


def test_parse_missing_temp() -> None:
    with pytest.raises(ValueError, match="missing temperature"):
        parse_metar_speci("METAR KJFK 231751Z 18012KT 10SM A3005=", product="METAR")


def test_parse_missing_altimeter() -> None:
    with pytest.raises(ValueError, match="missing altimeter"):
        parse_metar_speci("METAR KJFK 231751Z 18012KT 10SM 15/07=", product="METAR")


def test_parse_vrb_and_mps_and_negative_temps() -> None:
    ir = parse_metar_speci(
        "METAR KJFK 231751Z VRB03MPS 5SM FEW010 M02/M05 A2992=",
        product="METAR",
    )
    assert ir["wind_variable"] is True
    assert ir["wind_dir_deg"] is None
    assert ir["wind_speed_mps"] == 3
    assert ir["temp_c"] == -2
    assert ir["dewpoint_c"] == -5
    assert ir["visibility_above"] is False


def test_parse_without_trailing_equals() -> None:
    ir = parse_metar_speci(
        "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005",
        product="METAR",
    )
    assert ir["station"] == "KJFK"


def test_emit_unsupported_version() -> None:
    with pytest.raises(ValueError, match="unsupported iwxxm_version"):
        emit_metar_speci_annex3(
            {"station": "KJFK", "day": 23, "hour": 17, "minute": 51, "nil": True},
            product="METAR",
            iwxxm_version="1999-1",
        )


def test_emit_without_cloud_layer() -> None:
    ir = {
        "station": "KJFK",
        "day": 23,
        "hour": 17,
        "minute": 51,
        "nil": False,
        "temp_c": 15,
        "dewpoint_c": 7,
        "qnh_hpa": 1017.6,
        "wind_dir_deg": 180,
        "wind_speed_kt": 12,
        "visibility_m": 10000,
        "visibility_above": True,
    }
    xml = emit_metar_speci_annex3(ir, product="METAR", iwxxm_version="2025-2")
    assert "iwxxm:cloud" not in xml
    assert "prevailingVisibilityOperator>ABOVE" in xml


def test_scan_metar_tokens_raises_without_extension(monkeypatch: pytest.MonkeyPatch) -> None:
    from tac2iwxxm.native import scan_metar_tokens

    monkeypatch.setattr("tac2iwxxm.native.rust_module", lambda: None)
    with pytest.raises(NotImplementedError, match="scan_metar_tokens"):
        scan_metar_tokens("METAR KJFK 231751Z NIL=")


def test_scan_metar_tokens_when_rust_available() -> None:
    from tac2iwxxm import rust_available
    from tac2iwxxm.native import scan_metar_tokens

    if not rust_available():
        pytest.skip("PyO3 extension not built in this environment")
    tokens = scan_metar_tokens("METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005=")
    assert tokens[0] == "METAR"
    assert "KJFK" in tokens


def test_convert_vrb_omits_mean_wind_direction() -> None:
    """Bugbot PR #705: VRB must not emit meanWindDirection=None."""
    result = convert(
        "METAR KJFK 231751Z VRB03KT 5SM FEW010 15/07 A2992=",
        product="METAR",
    )
    assert result.ok and result.xml
    assert 'variableWindDirection="true"' in result.xml
    assert "meanWindDirection" not in result.xml
    assert ">None<" not in result.xml


def test_convert_mps_gust_converted_to_knots() -> None:
    """Bugbot PR #705: MPS gust must convert to knots like mean speed."""
    result = convert(
        "METAR KJFK 231751Z 24004G12MPS 5SM FEW010 15/07 A2992=",
        product="METAR",
    )
    assert result.ok and result.ir is not None
    assert result.ir["wind_speed_mps"] == 4
    assert result.ir["wind_gust_mps"] == 12
    # 12 m/s ≈ 23 kt
    assert result.ir["wind_gust_kt"] == int(round(12 * 1.94384))
    assert f'windGustSpeed uom="[kn_i]">{result.ir["wind_gust_kt"]}' in (result.xml or "")

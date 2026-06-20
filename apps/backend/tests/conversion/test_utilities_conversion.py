"""Unit tests for conversion utilities."""

import pathlib
import sys

# Ensure src layout path precedence
ROOT = pathlib.Path(__file__).resolve().parents[2]
BACKEND_SRC = ROOT / "backend" / "src"
if str(BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(BACKEND_SRC))
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from src.utilities.conversion import (
    ConversionError,
    convert_metar_tac,
    convert_metar_tac_with_metadata,
)

VALID_METAR = "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005"
VALID_SPECI = "SPECI KJFK 232045Z 20015G25KT 8SM -SN BKN020 OVC040 12/06 A3001"
VALID_COR_METAR = "METAR COR FAOR 101200Z 12012KT 9999 FEW020 22/14 Q1018"
INVALID_METAR = "INVALID TEXT"


def test_convert_valid_metar():
    """Test conversion of valid METAR."""
    result = convert_metar_tac(VALID_METAR)
    assert isinstance(result, str)
    assert len(result) > 0
    assert "<iwxxm:METAR" in result


def test_convert_valid_speci():
    """Test conversion of valid SPECI."""
    result = convert_metar_tac(VALID_SPECI)
    assert isinstance(result, str)
    assert len(result) > 0
    assert "<iwxxm:METAR" in result or "<iwxxm:SPECI" in result or "iwxxm" in result


def test_convert_invalid_metar_produces_output():
    """Test that invalid METAR still produces some XML output."""
    # METAR decoder is lenient and may still produce output even with invalid input
    try:
        result = convert_metar_tac(INVALID_METAR)
        assert isinstance(result, str)
    except ConversionError:
        # It's also okay if it raises an error
        pass


def test_conversion_error_is_exception():
    """Test that ConversionError is an Exception subclass."""
    assert issubclass(ConversionError, Exception)


def test_conversion_output_is_valid_xml():
    """Test that output is valid XML string."""
    result = convert_metar_tac(VALID_METAR)
    assert "<iwxxm:" in result or "iwxxm" in result
    assert result.count("<") == result.count(">")  # Basic XML balance check


def test_conversion_whitespace_handling():
    """Test handling of whitespace in input."""
    metar_with_spaces = "  METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005  "
    result = convert_metar_tac(metar_with_spaces)
    assert "<iwxxm:METAR" in result


def test_multiple_conversions():
    """Test multiple sequential conversions."""
    for _ in range(3):
        result = convert_metar_tac(VALID_METAR)
        assert "<iwxxm:METAR" in result


def test_different_stations():
    """Test conversions from different stations."""
    stations = [
        "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005",
        "METAR KLAX 231753Z 25008KT 10SM FEW020 18/12 A2992",
        "METAR KORD 231756Z 16008KT 10SM SCT035 14/05 A3012",
    ]
    for station in stations:
        result = convert_metar_tac(station)
        assert "<iwxxm:METAR" in result


def test_conversion_returns_string():
    """Test that conversion always returns a string."""
    result = convert_metar_tac(VALID_METAR)
    assert isinstance(result, str)
    assert len(result) > 0


def test_different_valid_metars():
    """Test conversion of various valid METAR formats."""
    metars = [
        "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005",
        "METAR KJFK 231751Z 18012KT 10SM OVC040 15/07 A3005",
        "METAR KJFK 231751Z 18012KT 10SM SCT040 15/07 A3005",
    ]
    for metar in metars:
        result = convert_metar_tac(metar)
        assert len(result) > 0


def test_convert_cor_metar_with_metadata():
    """Test corrected METAR converts to IWXXM with correction status."""
    result, validation_result = convert_metar_tac_with_metadata(
        VALID_COR_METAR,
        iwxxm_version="2025-2",
    )

    assert isinstance(result, str)
    assert len(result) > 0
    assert 'reportStatus="CORRECTION"' in result
    assert "translationFailedTAC" not in result
    assert validation_result is not None
    assert validation_result.is_valid is True


# ---------------------------------------------------------------------------
# Recent weather normalization (issue #668): RESH -> RESHUP
# ---------------------------------------------------------------------------

METAR_WITH_RESH = "METAR TTPP 121000Z 00000KT 9999 VCSH FEW010CB 26/25 Q1013 RESH NOSIG"
METAR_WITH_RESHRA = "METAR TTPP 121000Z 00000KT 9999 VCSH FEW010CB 26/25 Q1013 RESHRA NOSIG"


def test_resh_conversion_succeeds_lenient_mode():
    """METAR with bare RESH token must not raise ConversionError in lenient mode (default).

    Also verifies that the encoder does not produce a TAC-failure element,
    confirming that RESHUP (the normalised form) was decoded and encoded
    successfully.
    """
    result, _ = convert_metar_tac_with_metadata(
        METAR_WITH_RESH,
        validate=False,
        lenient=True,
    )
    assert isinstance(result, str)
    assert len(result) > 0
    assert "translationFailedTAC" not in result


def test_resh_normalizer_rewrites_before_conversion():
    """normalize_recent_weather_tokens rewrites RESH->RESHUP before GIFTs decoding.

    This test verifies the normalizer step independently of the full pipeline so
    results are stable even when GIFTs module state is polluted by earlier tests.
    """
    from src.utilities.metar_normalizer import normalize_recent_weather_tokens

    normalised, warnings = normalize_recent_weather_tokens(METAR_WITH_RESH)
    assert "RESHUP" in normalised
    assert " RESH " not in normalised
    assert len(warnings) == 1
    assert warnings[0]["original"] == "RESH"
    assert warnings[0]["replacement"] == "RESHUP"


def test_reshra_conversion_still_works_baseline():
    """RESHRA (already valid) must still convert successfully with lenient mode on (regression guard)."""
    result, _ = convert_metar_tac_with_metadata(
        METAR_WITH_RESHRA,
        validate=False,
        lenient=True,
    )
    assert isinstance(result, str)
    assert len(result) > 0
    assert "translationFailedTAC" not in result


def test_lenient_false_resh_strict_behaviour():
    """When lenient=False, RESH is NOT rewritten and the decoder may record a parse failure."""
    # We do not assert that this raises ConversionError because GIFTs degrades gracefully
    # (it encodes a translationFailedTAC element rather than raising), but we DO assert that
    # the normalised XML from lenient=True does NOT appear when lenient is off.
    result_strict, _ = convert_metar_tac_with_metadata(
        METAR_WITH_RESH,
        validate=False,
        lenient=False,
    )
    result_lenient, _ = convert_metar_tac_with_metadata(
        METAR_WITH_RESH,
        validate=False,
        lenient=True,
    )
    # Strict mode should not silently mirror lenient output.
    assert result_strict != result_lenient
    # In strict mode, GIFTs should preserve TAC parse failure markers for bare RESH.
    assert "translationFailedTAC" in result_strict
    # Lenient result should not contain a TAC failure marker
    assert "translationFailedTAC" not in result_lenient

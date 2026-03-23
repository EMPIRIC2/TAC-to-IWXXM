"""Unit tests for metar_normalizer.normalize_recent_weather_tokens."""
from __future__ import annotations

import pytest

from src.utilities.metar_normalizer import normalize_recent_weather_tokens

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _normalized(tac: str) -> str:
    """Return only the normalized text, ignoring warnings."""
    result, _ = normalize_recent_weather_tokens(tac)
    return result


def _warnings(tac: str) -> list:
    """Return only the warnings list."""
    _, warnings = normalize_recent_weather_tokens(tac)
    return warnings


# ---------------------------------------------------------------------------
# Core rewrite rules
# ---------------------------------------------------------------------------

def test_resh_rewritten_to_reshup():
    result = _normalized("METAR TTPP 121000Z 00000KT 9999 FEW010 26/25 Q1013 RESH NOSIG")
    assert "RESHUP" in result
    assert " RESH " not in result  # original token gone (space-bounded check)


def test_refz_rewritten_to_refzup():
    result = _normalized("METAR KJFK 121000Z 00000KT 9999 FEW010 10/05 A2990 REFZ NOSIG")
    assert "REFZUP" in result
    assert " REFZ " not in result


# ---------------------------------------------------------------------------
# No accidental rewrites
# ---------------------------------------------------------------------------

def test_reshra_unchanged():
    tac = "METAR KJFK 121000Z 18012KT 9999 FEW020 15/07 A3005 RESHRA NOSIG"
    assert _normalized(tac) == tac
    assert _warnings(tac) == []


def test_reshup_already_valid_unchanged():
    tac = "METAR KJFK 121000Z 18012KT 9999 FEW020 15/07 A3005 RESHUP NOSIG"
    assert _normalized(tac) == tac
    assert _warnings(tac) == []


def test_vcsh_unchanged():
    """VCSH is vicinity showers (not a recent-weather group)."""
    tac = "METAR TTPP 121000Z 00000KT 9999 VCSH FEW010CB 26/25 Q1013 NOSIG"
    assert _normalized(tac) == tac
    assert _warnings(tac) == []


def test_shra_unchanged():
    """SHRA is present weather (no RE prefix)."""
    tac = "METAR KJFK 121000Z 18012KT 9999 SHRA FEW020 15/07 A3005"
    assert _normalized(tac) == tac
    assert _warnings(tac) == []


def test_retssn_unchanged():
    """RETSSN has a phenomenon (SN), should not be touched."""
    tac = "METAR KJFK 121000Z 18012KT 9999 FEW020 15/07 A3005 RETSSN NOSIG"
    assert _normalized(tac) == tac
    assert _warnings(tac) == []


# ---------------------------------------------------------------------------
# Trailing '=' handling
# ---------------------------------------------------------------------------

def test_resh_trailing_equals_rewritten():
    tac = "METAR TTPP 121000Z 00000KT 9999 FEW010CB 26/25 Q1013 RESH="
    result = _normalized(tac)
    assert result.endswith("RESHUP=")
    assert " RESH=" not in result


def test_refz_trailing_equals_rewritten():
    tac = "METAR KJFK 121000Z 00000KT 9999 FEW010 10/05 A2990 REFZ="
    result = _normalized(tac)
    assert result.endswith("REFZUP=")


# ---------------------------------------------------------------------------
# Multiple rewrites
# ---------------------------------------------------------------------------

def test_multiple_rewrites_in_one_metar():
    """Both RESH and REFZ in the same report should both be rewritten."""
    tac = "METAR KJFK 121000Z 00000KT 9999 FEW010 10/05 A2990 RESH REFZ NOSIG"
    result, warns = normalize_recent_weather_tokens(tac)
    assert "RESHUP" in result
    assert "REFZUP" in result
    assert len(warns) == 2


# ---------------------------------------------------------------------------
# Clean METAR passes through unchanged
# ---------------------------------------------------------------------------

def test_clean_metar_unchanged_empty_warnings():
    tac = "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005"
    result, warns = normalize_recent_weather_tokens(tac)
    assert result == tac
    assert warns == []


# ---------------------------------------------------------------------------
# Warning dict structure
# ---------------------------------------------------------------------------

def test_warning_dict_keys():
    tac = "METAR TTPP 121000Z 00000KT 9999 FEW010CB 26/25 Q1013 RESH NOSIG"
    _, warns = normalize_recent_weather_tokens(tac)
    assert len(warns) == 1
    w = warns[0]
    assert set(w.keys()) == {"index", "original", "replacement", "rule"}
    assert w["original"] == "RESH"
    assert w["replacement"] == "RESHUP"
    assert w["rule"] == "recent_weather_truncated_showers"


def test_refz_warning_rule_name():
    tac = "METAR KJFK 121000Z 00000KT 9999 FEW010 10/05 A2990 REFZ NOSIG"
    _, warns = normalize_recent_weather_tokens(tac)
    assert len(warns) == 1
    assert warns[0]["rule"] == "recent_weather_truncated_freezing"


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_empty_string():
    result, warns = normalize_recent_weather_tokens("")
    assert result == ""
    assert warns == []


def test_whitespace_only_string():
    result, warns = normalize_recent_weather_tokens("   ")
    assert result == "   "
    assert warns == []


def test_leading_trailing_whitespace_preserved():
    tac = "  METAR TTPP 121000Z 00000KT 9999 FEW010 26/25 Q1013 RESH NOSIG  "
    result, _ = normalize_recent_weather_tokens(tac)
    assert result.startswith("  ")
    assert result.endswith("  ")
    assert "RESHUP" in result

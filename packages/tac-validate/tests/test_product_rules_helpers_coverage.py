"""Coverage gaps for product_rules helpers (F15 CI cov-fail-under=95)."""

from __future__ import annotations

from tac_validate.product_rules import (
    _body_span,
    _is_valid_weather_token,
    _weather_candidate_tokens,
)


def test_body_span_whitespace_only() -> None:
    start, end, body = _body_span("   \n")
    assert body == ""
    assert start == 0
    assert end == 4


def test_weather_token_edge_cases() -> None:
    assert _is_valid_weather_token("UP") is True
    assert _is_valid_weather_token("//") is True
    assert _is_valid_weather_token("++RA") is False
    assert _is_valid_weather_token("+-RA") is False
    assert _is_valid_weather_token("+") is False
    assert _is_valid_weather_token("+VCSH") is False
    assert _is_valid_weather_token("RA+") is False
    assert _is_valid_weather_token("XYZ") is False
    assert _is_valid_weather_token("TSRA") is True
    assert _is_valid_weather_token("SHRA") is True
    assert _is_valid_weather_token("-") is False


def test_weather_candidates_skip_without_wind() -> None:
    assert _weather_candidate_tokens(["METAR", "KJFK", "101200Z"]) == []

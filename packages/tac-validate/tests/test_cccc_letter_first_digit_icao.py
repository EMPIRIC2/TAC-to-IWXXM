"""Unit matrix for letter-first CCCC with digits (#1476).

Covers helper match / extract / lint validation success and failure modes.
Mutation surface is read-only lint (no create/update/delete state).
[Corpus: product §F15] [Corpus: tests] [Corpus: domain]
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from tac_validate.api import extract_station_icao, lint
from tac_validate.product_rules_pkg._common import (
    _ICAO,
    _METAR_SPECI_SKIP,
    _TAF_SKIP,
    _first_icao,
    _first_icao_index,
)

_R1_YAML = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "tac_validate"
    / "data"
    / "detectors"
    / "metar-speci-r1-identity-order.yaml"
)


# --- V+ / S: pattern + helpers accept digit and letter CCCC ---


@pytest.mark.parametrize(
    "token",
    ["K10U", "K05U", "K1F0", "KJFK", "EGLL"],
    ids=["k10u", "k05u", "k1f0", "kjfk", "egll"],
)
def test_icao_token_fullmatch_accepts_letter_first(token: str) -> None:
    assert _ICAO.fullmatch(token) is not None


@pytest.mark.parametrize(
    ("tokens", "skip", "expected"),
    [
        (["METAR", "K10U", "302035Z"], _METAR_SPECI_SKIP, "K10U"),
        (["SPECI", "COR", "K05U", "302045Z"], _METAR_SPECI_SKIP, "K05U"),
        (["TAF", "AMD", "K1F0", "302030Z"], _TAF_SKIP, "K1F0"),
        (["METAR", "AUTO", "KJFK", "302035Z"], _METAR_SPECI_SKIP, "KJFK"),
    ],
    ids=["metar-digit", "speci-cor-digit", "taf-amd-digit", "metar-auto-letter"],
)
def test_first_icao_skips_keywords(
    tokens: list[str],
    skip: frozenset[str],
    expected: str,
) -> None:
    assert _first_icao(tokens, skip) == expected
    assert _first_icao_index(tokens, skip) == tokens.index(expected)


@pytest.mark.parametrize(
    ("tac", "product", "expected"),
    [
        ("METAR K10U 302035Z AUTO 23005KT 10SM FEW023=", "METAR", "K10U"),
        ("SPECI COR K10U 302045Z AUTO 23005KT 10SM FEW023=", "SPECI", "K10U"),
        ("TAF AMD K10U 302030Z 3021/3103 23005KT P6SM FEW023=", "TAF", "K10U"),
        ("METAR KJFK 302035Z 23005KT 10SM FEW023=", "METAR", "KJFK"),
    ],
    ids=["metar-k10u", "speci-cor-k10u", "taf-amd-k10u", "metar-kjfk"],
)
def test_extract_station_icao_digit_and_letter(
    tac: str,
    product: str,
    expected: str,
) -> None:
    assert extract_station_icao(tac, product) == expected


def test_r1_detector_yaml_pattern_is_letter_first_with_digits() -> None:
    payload = yaml.safe_load(_R1_YAML.read_text(encoding="utf-8"))
    rule = next(r for r in payload["rules"] if r["id"] == "missing_cccc")
    assert rule["pattern"] == r"\b(?!AUTO\b)[A-Z][A-Z0-9]{3}\b"
    assert rule["on_fail"]["code"] == "MISSING_CCCC"


# --- V- / F: reject digit-first, absent, empty, garbage ---


@pytest.mark.parametrize(
    "token",
    ["10UK", "1ABC", "1234", "ABC"],
    ids=["digit-first", "digit-lead", "all-digit", "too-short"],
)
def test_icao_token_fullmatch_rejects_invalid(token: str) -> None:
    assert _ICAO.fullmatch(token) is None


def test_auto_matches_shape_but_is_skipped_as_keyword() -> None:
    """AUTO is letter+3 alnum; skip sets keep it from counting as CCCC."""
    assert _ICAO.fullmatch("AUTO") is not None
    assert _first_icao(["METAR", "AUTO", "302035Z"], _METAR_SPECI_SKIP) is None


@pytest.mark.parametrize(
    ("tokens", "skip"),
    [
        (["METAR", "10UK", "302035Z"], _METAR_SPECI_SKIP),
        (["METAR", "302035Z", "AUTO"], _METAR_SPECI_SKIP),
        (["TAF", "151800Z", "1600/1618"], _TAF_SKIP),
        ([], _METAR_SPECI_SKIP),
    ],
    ids=["digit-first", "time-only", "taf-no-station", "empty"],
)
def test_first_icao_returns_none_when_absent(
    tokens: list[str],
    skip: frozenset[str],
) -> None:
    assert _first_icao(tokens, skip) is None
    assert _first_icao_index(tokens, skip) is None


@pytest.mark.parametrize(
    ("tac", "product"),
    [
        ("METAR 10UK 302035Z AUTO 23005KT 10SM FEW023=", "METAR"),
        ("METAR 302035Z AUTO 23005KT 10SM FEW023=", "METAR"),
        ("SPECI 302045Z AUTO 23005KT 10SM FEW023=", "SPECI"),
        ("TAF 151800Z 1600/1618 13005MPS 9000 BKN020=", "TAF"),
        ("", "METAR"),
        ("GARBAGE", "METAR"),
    ],
    ids=[
        "digit-first",
        "metar-missing",
        "speci-missing",
        "taf-missing",
        "empty",
        "garbage",
    ],
)
def test_extract_station_icao_rejects_invalid_or_absent(tac: str, product: str) -> None:
    assert extract_station_icao(tac, product) is None


@pytest.mark.parametrize(
    ("tac", "product"),
    [
        ("METAR 10UK 302035Z AUTO 23005KT 10SM FEW023=", "METAR"),
        ("METAR 302035Z AUTO 23005KT 10SM FEW023=", "METAR"),
        ("SPECI 302045Z AUTO 23005KT 10SM FEW023=", "SPECI"),
        ("TAF 151800Z 1600/1618 13005MPS 9000 BKN020=", "TAF"),
    ],
    ids=["digit-first", "metar-missing", "speci-missing", "taf-missing"],
)
def test_lint_emits_missing_cccc_on_validation_failure(tac: str, product: str) -> None:
    codes = {issue.code for issue in lint(tac, product=product).issues}
    assert "MISSING_CCCC" in codes


@pytest.mark.parametrize(
    ("tac", "product", "expected_code"),
    [
        ("", "METAR", "EMPTY_TAC"),
        ("GARBAGE", "METAR", "MISSING_PRODUCT_KEYWORD"),
    ],
    ids=["empty", "garbage"],
)
def test_lint_rejects_empty_or_garbage_before_cccc(
    tac: str,
    product: str,
    expected_code: str,
) -> None:
    codes = {issue.code for issue in lint(tac, product=product).issues}
    assert expected_code in codes
    assert extract_station_icao(tac, product) is None

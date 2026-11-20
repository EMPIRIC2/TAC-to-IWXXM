"""BUG-2026-10-30 — MISSING_CCCC must not fire on digit ICAO (K10U).

US METAR/SPECI/TAF station designators may include digits (e.g. K10U, K05U,
K1F0). R1 CCCC detection used ``[A-Z]{4}`` only, so lint emitted
``MISSING_CCCC`` even when the station token was present. Production
pattern/helpers were widened in #1481; this module locks success and
failure modes for #1476.

Live-map full-world probe 2026-10-30: 8 places, all pass=true.
Ticket: #1476. [Corpus: product §F15] [Corpus: tests]
"""

from __future__ import annotations

import pytest
from tac_validate import lint
from tac_validate.api import extract_station_icao

# Staging live-map places (Bar B samples).
_K10U = "METAR K10U 302035Z AUTO 23005KT 10SM FEW023 OVC100 12/05 A2989 RMK AO2"
_K05U = "METAR K05U 302055Z AUTO 17012KT 10SM CLR 13/06 A2989 RMK AO2"
_K1F0 = "METAR K1F0 302055Z AUTO 00000KT 10SM SCT017 SCT110 22/18 A3009 RMK AO2"
_SPECI_K10U = "SPECI K10U 302045Z AUTO 23005KT 10SM FEW023 12/05 A2989="
_SPECI_COR_K10U = "SPECI COR K10U 302050Z AUTO 23005KT 10SM FEW023 12/05 A2989="
_TAF_K10U = "TAF K10U 302030Z 3021/3103 23005KT P6SM FEW023="
_TAF_AMD_K10U = "TAF AMD K10U 302030Z 3021/3103 23005KT P6SM FEW023="
_LETTER_ONLY = "METAR KJFK 302035Z 23005KT 10SM FEW023 12/05 A2989="
_METAR_COR_LETTER = "METAR COR KJFK 302035Z 23005KT 10SM FEW023 12/05 A2989="
_MISSING = "METAR 302035Z AUTO 23005KT 10SM FEW023 OVC100 12/05 A2989="
_DIGIT_FIRST = "METAR 10UK 302035Z AUTO 23005KT 10SM FEW023 12/05 A2989="
_SPECI_MISSING = "SPECI 302045Z AUTO 23005KT 10SM FEW023 12/05 A2989="
_SPECI_DIGIT_FIRST = "SPECI 10UK 302045Z AUTO 23005KT 10SM FEW023 12/05 A2989="
# Avoid P6SM here — letter+digit visibility can look like a CCCC token.
_TAF_MISSING = "TAF 151800Z 1600/1618 13005MPS 9000 BKN020="
_TAF_DIGIT_FIRST = "TAF 10UK 302030Z 3021/3103 23005KT 9000 FEW023="


def _codes(tac: str, *, product: str) -> set[str]:
    return {issue.code for issue in lint(tac, product=product).issues}


@pytest.mark.parametrize(
    ("tac", "product", "station"),
    [
        (_K10U, "METAR", "K10U"),
        (_K05U, "METAR", "K05U"),
        (_K1F0, "METAR", "K1F0"),
        (_SPECI_K10U, "SPECI", "K10U"),
        (_SPECI_COR_K10U, "SPECI", "K10U"),
        (_TAF_K10U, "TAF", "K10U"),
        (_TAF_AMD_K10U, "TAF", "K10U"),
        (_LETTER_ONLY, "METAR", "KJFK"),
        (_METAR_COR_LETTER, "METAR", "KJFK"),
    ],
    ids=[
        "k10u",
        "k05u",
        "k1f0",
        "speci-k10u",
        "speci-cor-k10u",
        "taf-k10u",
        "taf-amd-k10u",
        "letter-only-kjfk",
        "metar-cor-kjfk",
    ],
)
def test_digit_or_letter_cccc_not_missing(
    tac: str,
    product: str,
    station: str,
) -> None:
    assert extract_station_icao(tac, product) == station
    assert "MISSING_CCCC" not in _codes(tac, product=product)


@pytest.mark.parametrize(
    ("tac", "product"),
    [
        (_MISSING, "METAR"),
        (_DIGIT_FIRST, "METAR"),
        (_SPECI_MISSING, "SPECI"),
        (_SPECI_DIGIT_FIRST, "SPECI"),
        (_TAF_MISSING, "TAF"),
        (_TAF_DIGIT_FIRST, "TAF"),
    ],
    ids=[
        "metar-missing",
        "metar-digit-first",
        "speci-missing",
        "speci-digit-first",
        "taf-missing",
        "taf-digit-first",
    ],
)
def test_invalid_or_absent_cccc_still_errors(tac: str, product: str) -> None:
    assert extract_station_icao(tac, product) is None
    assert "MISSING_CCCC" in _codes(tac, product=product)


@pytest.mark.parametrize(
    ("tac", "expected_code"),
    [
        ("", "EMPTY_TAC"),
        ("GARBAGE", "MISSING_PRODUCT_KEYWORD"),
    ],
    ids=["empty", "garbage"],
)
def test_pre_cccc_validation_failures_still_reject(
    tac: str, expected_code: str
) -> None:
    assert extract_station_icao(tac, "METAR") is None
    assert expected_code in _codes(tac, product="METAR")

"""#1563: translation fail still emits IWXXM carrying original TAC.

Hard-fail SIGMET/AIRMET structural defects and product-shaped unknown-VOR
paths must quarantine with ``@translationFailedTAC`` (no invented TS, no
illegal geometry). Non-product TAC still hard-fails without XML.

[Corpus: product §F6] [Corpus: domain] [Corpus: tests] D-029
"""

from __future__ import annotations

import re

import pytest

from tac2iwxxm import ConvertResult, convert

_TS_HREF = "AirWxPhenomena/TS"

_EMPTY_SIGMET = "YUDD SIGMET 2 VALID 101200/101600 YUSO-="
_FIR_ONLY_SIGMET = "YUDD SIGMET 2 VALID 101200/101600 YUSO-\nYUDD SHANLON FIR="
_EMPTY_AIRMET = "YUDD AIRMET 1 VALID 151520/151800 YUSO-="
_INCOMPLETE_CNL = "YUDD SIGMET 3 VALID 101345/101600 YUSO-\nYUDD SHANLON FIR/UIR CNL SIGMET 2="
_INVERTED_VALID = (
    "YUDD SIGMET 2 VALID 101600/101200 YUSO-\n"
    "YUDD SHANLON FIR/UIR OBSC TS FCST S OF N54 AND E OF W012 TOP FL390 MOV E 20KT WKN="
)
_ZERO_VALID = (
    "YUDD SIGMET 2 VALID 101200/101200 YUSO-\n"
    "YUDD SHANLON FIR/UIR OBSC TS FCST S OF N54 AND E OF W012 TOP FL390 MOV E 20KT WKN="
)
_LAT95 = (
    "YUDD SIGMET 2 VALID 101200/101600 YUSO-\n"
    "YUDD SHANLON FIR/UIR SEV ICE FCST WI N9500 E01000 - N9600 E01200 - "
    "N9500 E01400 - N9500 E01000 FL100/200 STNR NC="
)
_AIRMET_NO_PHENOMENON = (
    "YUDD AIRMET 1 VALID 151400/152100 YUSO-\nYUDD SHANLON FIR=\nOTLK VALID 1800-2000Z...AREA BOUNDED BY BAE-BVT"
)
_NOT_PRODUCT = "THIS IS NOT A WEATHER PRODUCT AT ALL"


def _attr(xml: str, name: str) -> str | None:
    match = re.search(rf'\b{re.escape(name)}="([^"]*)"', xml)
    return match.group(1) if match else None


def _phenomenon_hrefs(xml: str) -> list[str]:
    return re.findall(r'phenomenon[^>]*xlink:href="([^"]+)"', xml or "")


def _pos_values(xml: str) -> list[float]:
    lists = re.findall(r"<gml:posList[^>]*>([^<]*)</gml:posList>", xml or "")
    values: list[float] = []
    for block in lists:
        values.extend(float(tok) for tok in block.split() if tok)
    return values


def _assert_quarantine_carries_tac(result: ConvertResult, *, tac_substr: str) -> None:
    assert result.ok is True
    xml = result.xml or ""
    assert "translationFailedTAC" in xml
    carried = _attr(xml, "translationFailedTAC") or ""
    assert tac_substr in carried.replace("\n", " ")
    assert any(i.code == "TRANSLATION_FAILED" for i in result.issues)
    assert not any(_TS_HREF in href for href in _phenomenon_hrefs(xml))
    assert "<iwxxm:analysis" not in xml
    assert "<iwxxm:observation>" not in xml


@pytest.mark.parametrize(
    ("tac", "product", "substr"),
    [
        (_EMPTY_SIGMET, "SIGMET", "YUDD SIGMET 2"),
        (_FIR_ONLY_SIGMET, "SIGMET", "YUDD SIGMET 2"),
        (_EMPTY_AIRMET, "AIRMET", "YUDD AIRMET 1"),
        (_INCOMPLETE_CNL, "SIGMET", "CNL SIGMET 2"),
        (_INVERTED_VALID, "SIGMET", "VALID 101600/101200"),
        (_ZERO_VALID, "SIGMET", "VALID 101200/101200"),
        (_LAT95, "SIGMET", "N9500"),
        (_AIRMET_NO_PHENOMENON, "AIRMET", "YUDD AIRMET 1"),
    ],
)
def test_tc_1563_structural_fail_emits_quarantine_with_tac(tac: str, product: str, substr: str) -> None:
    """Success path: hard structural fails still yield translation-failed XML."""
    result = convert(tac, product=product, profile="annex3", iwxxm_version="2025-2")
    _assert_quarantine_carries_tac(result, tac_substr=substr)
    assert 95.0 not in _pos_values(result.xml or "")
    assert 190.0 not in _pos_values(result.xml or "")
    if "VALID 101600/101200" in tac or "VALID 101200/101200" in tac:
        assert "<gml:beginPosition>" not in (result.xml or "")


def test_tc_1563_non_product_still_hard_fails_without_xml() -> None:
    """Failure path: non-product TAC stays ok=false with no quarantine XML."""
    result = convert(_NOT_PRODUCT, product="SIGMET", profile="annex3", iwxxm_version="2025-2")
    assert result.ok is False
    assert result.xml is None or "translationFailedTAC" not in (result.xml or "")
    assert any(i.code == "PARSE_ERROR" for i in result.issues)


def test_tc_1563_preview_keeps_ok_false_stub() -> None:
    """Validation/preview: preview mode still returns ok=false stub (not quarantine soft-ok)."""
    result = convert(
        _EMPTY_SIGMET,
        product="SIGMET",
        profile="annex3",
        iwxxm_version="2025-2",
        preview=True,
    )
    assert result.ok is False
    assert result.xml is not None
    assert "translationFailedTAC" not in result.xml


def test_tc_1563_happy_path_sigmet_still_converts() -> None:
    """Validation success: well-formed SIGMET still converts without quarantine."""
    tac = (
        "YUDD SIGMET 2 VALID 101200/101600 YUSO-\n"
        "YUDD SHANLON FIR/UIR OBSC TS FCST S OF N54 AND E OF W012 TOP FL390 MOV E 20KT WKN="
    )
    result = convert(tac, product="SIGMET", profile="annex3", iwxxm_version="2025-2")
    assert result.ok is True
    assert result.xml is not None
    assert "translationFailedTAC" not in result.xml
    assert not any(i.code == "TRANSLATION_FAILED" for i in result.issues)


def test_tc_1563_invalid_keyword_still_quarantines() -> None:
    """Mutation-adjacent: INVALID keyword path still emits quarantine (create shell)."""
    tac = "YUDD SIGMET 1 VALID 101600/101200 YUSO INVALID"
    result = convert(tac, product="SIGMET", profile="annex3", iwxxm_version="2025-2")
    _assert_quarantine_carries_tac(result, tac_substr="INVALID")
    assert "nilReason" in (result.xml or "")

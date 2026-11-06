"""QNH decode rows name the pressure and what QNH means."""

from __future__ import annotations

from tac_decoding import decode_tac
from tac_decoding.match import match_tac
from tac_decoding.packs import load_packs

_MEANING = "the altimeter setting reduced to mean sea level"


def _qnh_explanation(tac: str, product: str) -> str:
    result = decode_tac(tac, product=product)
    matches = [segment.explanation for segment in result.segments if segment.code == "Q1008"]
    assert len(matches) == 1
    return matches[0]


def test_metar_qnh_explains_the_setting_and_keeps_hectopascals() -> None:
    text = _qnh_explanation("METAR YUDO 151115Z Q1008=", "METAR")
    assert text == f"QNH 1008 hPa, {_MEANING}"


def test_speci_qnh_uses_the_same_sentence() -> None:
    text = _qnh_explanation("SPECI YUDO 151115Z Q1008=", "SPECI")
    assert text == f"QNH 1008 hPa, {_MEANING}"


def test_taf_qnh_uses_the_same_sentence() -> None:
    text = _qnh_explanation("TAF YUDO 151100Z 1512/1612 Q1008=", "TAF")
    assert text == f"QNH 1008 hPa, {_MEANING}"


def test_metar_and_speci_packs_explain_qnh() -> None:
    packs = {pack.id: pack for pack in load_packs()}
    for name in ("metar", "speci"):
        result = match_tac("Q1008", packs[name])
        span = next(item for item in result.spans if item.rule_id == "qnh")
        assert span.explanation == f"QNH Q1008, {_MEANING}"

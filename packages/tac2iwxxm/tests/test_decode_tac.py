"""Unit coverage for ``tac2iwxxm.decode.decode_tac`` (F7 / #702)."""

from __future__ import annotations

from pathlib import Path

import pytest

from tac2iwxxm.decode import DecodeResult, decode_tac

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "product_matrix"

PRODUCT_FILES = {
    "AIRMET": "airmet_basic.tac",
    "METAR": "metar_basic.tac",
    "SIGMET": "sigmet_basic.tac",
    "SPECI": "speci_basic.tac",
    "TAF": "taf_basic.tac",
    "VAA": "vaa_basic.tac",
    "TCA": "tca_basic.tac",
}


@pytest.mark.parametrize("product,filename", list(PRODUCT_FILES.items()))
def test_decode_tac_product_matrix_well_formed(product: str, filename: str) -> None:
    tac = (FIXTURES / filename).read_text(encoding="utf-8").strip()
    result = decode_tac(tac, product=product)
    assert isinstance(result, DecodeResult)
    assert result.product == product
    assert isinstance(result.segments, list)
    assert isinstance(result.residuals, list)
    for seg in result.segments:
        assert 0 <= seg.start <= seg.end <= len(tac)
        assert seg.code
        assert seg.explanation


def test_decode_metar_golden_has_core_explanations() -> None:
    tac = (FIXTURES / "metar_basic.tac").read_text(encoding="utf-8").strip()
    result = decode_tac(tac, product="METAR")
    explanations = " ".join(s.explanation for s in result.segments).lower()
    assert "report type" in explanations
    assert "station" in explanations
    assert "wind" in explanations
    assert result.segments


def test_decode_speci_and_metar_tokens() -> None:
    speci = "SPECI KJFK 232045Z 20015G25KT 8SM -SN BKN020 OVC040 12/06 A3001="
    result = decode_tac(speci, product="SPECI")
    codes = [s.code for s in result.segments]
    assert "SPECI" in codes
    assert "KJFK" in codes
    assert any("special" in s.explanation.lower() for s in result.segments)


def test_decode_taf_change_groups() -> None:
    tac = "TAF KJFK 151800Z 1600/1618 13005KT 9999 BKN020 TEMPO 1606/1612 4000 -RA BKN010="
    result = decode_tac(tac, product="TAF")
    assert any("validity" in s.explanation.lower() for s in result.segments)
    assert any("tempo" in s.code.lower() or "change" in s.explanation.lower() for s in result.segments)


def test_decode_sigmet_airmet_hazards() -> None:
    sigmet = "YUDD SIGMET 2 VALID 101200/101600 YUSO- YUDD OBSC TS FCST ="
    result = decode_tac(sigmet, product="SIGMET")
    assert any("phenomenon" in s.explanation.lower() or "hazard" in s.explanation.lower() for s in result.segments)


def test_decode_vaa_tca_residuals_allowed() -> None:
    vaa = (FIXTURES / "vaa_basic.tac").read_text(encoding="utf-8").strip()
    result = decode_tac(vaa, product="VAA")
    assert result.segments or result.residuals
    tca = (FIXTURES / "tca_basic.tac").read_text(encoding="utf-8").strip()
    result_tca = decode_tac(tca, product="TCA")
    assert result_tca.segments or result_tca.residuals


def test_decode_unknown_product_entire_body_residual() -> None:
    tac = "NOT A REAL PRODUCT BODY"
    result = decode_tac(tac, product="NOTREAL")
    assert result.product == "NOTREAL"
    assert result.segments == []
    assert len(result.residuals) == 1
    assert result.residuals[0].text == tac


def test_decode_empty_unknown_product() -> None:
    result = decode_tac("", product="ZZZZ")
    assert result.segments == []
    assert result.residuals == []


def test_decode_metar_optional_tokens() -> None:
    tac = "METAR KJFK 231751Z COR NIL CAVOK RMK AO2 SLP123 PK WND 28045/15 ="
    result = decode_tac(tac, product="metar")
    joined = " ".join(s.explanation.lower() for s in result.segments)
    assert "correction" in joined
    assert "nil" in joined
    assert "cavok" in joined or "ceiling" in joined
    assert "remarks" in joined
    assert "automated" in joined
    assert "sea-level" in joined or "peak" in joined


def test_decode_qnh_and_weather() -> None:
    tac = "METAR LFPG 231751Z 18012KT 2000 RA BKN012 15/07 Q1013="
    result = decode_tac(tac, product="METAR")
    joined = " ".join(s.explanation.lower() for s in result.segments)
    assert "qnh" in joined or "visibility" in joined
    assert "weather" in joined or "cloud" in joined


def test_decode_coalesces_adjacent_residuals() -> None:
    tac = "METAR KJFK 231751Z UNK1 UNK2 18012KT="
    result = decode_tac(tac, product="METAR")
    residual_texts = [r.text for r in result.residuals]
    assert any("UNK1" in t and "UNK2" in t for t in residual_texts)

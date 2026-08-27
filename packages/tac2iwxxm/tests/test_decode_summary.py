"""TC-F9-002 §1-3 - deterministic plain-language ``summary`` (S013 / EV-009, F9).

``DecodeResult.summary`` is a single flowing paragraph built from decoded values.
Residuals append a trailing "Not decoded: …" clause. Sparse products (SIGMET/AIRMET/
VAA/TCA) use "partial decode" wording. ADR-025.
"""

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

METAR_GOLDEN = "METAR KJFK 121251Z 18004KT 10SM FEW250 24/18 A3011="


# --- TC-F9-002 §1 - summary present for all seven products ---


@pytest.mark.parametrize(("product", "filename"), list(PRODUCT_FILES.items()))
def test_summary_present_for_all_products(product: str, filename: str) -> None:
    tac = (FIXTURES / filename).read_text(encoding="utf-8").strip()
    result = decode_tac(tac, product=product)
    assert isinstance(result, DecodeResult)
    assert isinstance(result.summary, str)
    assert result.summary.strip()


# --- TC-F9-002 §2 - flowing paragraph from decoded values ---


def test_metar_summary_is_one_flowing_paragraph() -> None:
    result = decode_tac(METAR_GOLDEN, product="METAR")
    assert "\n" not in result.summary.strip()
    assert result.summary.count(".") >= 1
    lower = result.summary.lower()
    assert "kjfk" in lower
    assert "180°" in result.summary or "from 180" in lower
    assert "4 kt" in result.summary
    assert "24 °c" in lower or "24 °C" in result.summary
    assert "30.11" in result.summary


def test_summary_deterministic_across_calls() -> None:
    a = decode_tac(METAR_GOLDEN, product="METAR").summary
    b = decode_tac(METAR_GOLDEN, product="METAR").summary
    assert a == b


# --- TC-F9-002 §3 - residual clause + sparse-product wording ---


def test_summary_residual_clause() -> None:
    tac = "METAR KJFK 121251Z 18004KT UNK1 UNK2 24/18 A3011="
    result = decode_tac(tac, product="METAR")
    assert "Not decoded:" in result.summary
    assert "UNK1" in result.summary
    assert "UNK2" in result.summary


def test_summary_no_residual_clause_when_clean() -> None:
    result = decode_tac(METAR_GOLDEN, product="METAR")
    assert "Not decoded:" not in result.summary


@pytest.mark.parametrize("product", ["SIGMET", "AIRMET", "VAA", "TCA"])
def test_sparse_products_partial_decode_wording(product: str) -> None:
    tac = (FIXTURES / PRODUCT_FILES[product]).read_text(encoding="utf-8").strip()
    result = decode_tac(tac, product=product)
    assert "partial decode" in result.summary.lower()


def test_taf_summary_mentions_validity() -> None:
    tac = "TAF KJFK 151800Z 1600/1618 13005KT 9999 BKN020="
    result = decode_tac(tac, product="TAF")
    lower = result.summary.lower()
    assert "taf" in lower or "forecast" in lower
    assert "kjfk" in lower
    assert "day 16" in lower

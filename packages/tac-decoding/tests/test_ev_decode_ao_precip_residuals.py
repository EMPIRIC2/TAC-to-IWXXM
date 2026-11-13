"""Decode AO sensor + precip addenda residuals (US). [Corpus: product §F9]

Issue #1538 — A01/A02/P000/PP000 clear with or without ``RMK``. No MISSING_* severity soften.
"""

from __future__ import annotations

import pytest
from tac_decoding.decode import decode_tac
from tac_decoding.match import match_tac
from tac_decoding.packs import load_packs

_BODY = "031455Z AUTO 26003KT 9SM CLR 00/00 A3008"


def _codes(tac: str, product: str) -> dict[str, str]:
    result = decode_tac(tac, product=product)
    return {segment.code: segment.explanation for segment in result.segments}


def _residual_text(tac: str, product: str) -> str:
    return " ".join(item.text for item in decode_tac(tac, product=product).residuals)


def _pack_codes(fragment: str, pack_id: str) -> dict[str, str]:
    packs = {pack.id: pack for pack in load_packs()}
    result = match_tac(fragment, packs[pack_id])
    return {span.code: span.explanation for span in result.spans}


@pytest.mark.parametrize(
    ("token", "needle"),
    [
        ("A01", "automated"),
        ("A02", "automated"),
        ("AO1", "automated"),
        ("AO2", "automated"),
        ("P000", "precipitation"),
        ("P0000", "precipitation"),
        ("PP000", "precipitation"),
    ],
)
@pytest.mark.parametrize("product", ["METAR", "SPECI"])
@pytest.mark.parametrize("with_rmk", [True, False])
def test_ao_and_precip_addenda_explained(
    token: str,
    needle: str,
    product: str,
    with_rmk: bool,
) -> None:
    """US sensor / precip addenda decode as fragments; not residuals."""
    mid = f"RMK {token}" if with_rmk else token
    tac = f"{product} KSVE {_BODY} {mid}"
    codes = _codes(tac, product)
    assert token in codes
    assert needle in codes[token].lower()
    assert token not in _residual_text(tac, product).split()


@pytest.mark.parametrize(
    ("fragment", "tokens"),
    [
        ("A01 P000", ("A01", "P000")),
        ("A02 PP000", ("A02", "PP000")),
        ("AO1 P0000", ("AO1", "P0000")),
    ],
)
def test_ao_plus_precip_combo_not_residual(fragment: str, tokens: tuple[str, ...]) -> None:
    """Live-map style ``A01 P000`` pairs clear together."""
    for with_rmk in (True, False):
        mid = f"RMK {fragment}" if with_rmk else fragment
        tac = f"METAR KSVE {_BODY} {mid}"
        residual = _residual_text(tac, "METAR")
        codes = _codes(tac, "METAR")
        for tok in tokens:
            assert tok in codes
            assert tok not in residual.split()


@pytest.mark.parametrize("pack_id", ["metar", "speci"])
@pytest.mark.parametrize(
    "token",
    ["A01", "A02", "AO1", "AO2", "P000", "PP000"],
)
def test_pack_rules_cover_ao_and_precip(pack_id: str, token: str) -> None:
    """Pack residual policy names AO / precip addenda (not generic Token)."""
    codes = _pack_codes(token, pack_id)
    assert token in codes
    explanation = codes[token].lower()
    assert "token " not in explanation
    assert "automated" in explanation or "precip" in explanation

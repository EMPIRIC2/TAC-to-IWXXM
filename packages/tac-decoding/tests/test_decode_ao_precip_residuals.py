"""Decode AO sensor + precip addenda residuals (US). [Corpus: product §F9]

Issue #1538 — A01/A02/P000/PP000 clear with or without ``RMK``. No MISSING_*
severity soften. Combinatorial matrix: success, residual/malformed failure,
pack validation accept/reject.
"""

from __future__ import annotations

import pytest
from tac_decoding.decode import decode_tac
from tac_decoding.decode_tokens import _us_precip_addenda
from tac_decoding.match import match_tac
from tac_decoding.packs import load_packs

_BODY = "031455Z AUTO 26003KT 9SM CLR 00/00 A3008"


def _codes(tac: str, product: str) -> dict[str, str]:
    result = decode_tac(tac, product=product)
    return {segment.code: segment.explanation for segment in result.segments}


def _residual_tokens(tac: str, product: str) -> set[str]:
    return {item.text for item in decode_tac(tac, product=product).residuals}


def _pack_spans(fragment: str, pack_id: str) -> dict[str, str]:
    packs = {pack.id: pack for pack in load_packs()}
    result = match_tac(fragment, packs[pack_id])
    return {span.code: span.explanation for span in result.spans}


def _pack_rule_ids(fragment: str, pack_id: str) -> dict[str, str]:
    packs = {pack.id: pack for pack in load_packs()}
    result = match_tac(fragment, packs[pack_id])
    return {span.code: span.rule_id for span in result.spans}


# ---------------------------------------------------------------------------
# S — Success paths (happy path decode)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("token", "needle"),
    [
        ("A01", "automated"),
        ("A02", "automated"),
        ("AO1", "automated"),
        ("AO2", "automated"),
        ("AO2A", "augmented"),
        ("P000", "precipitation"),
        ("P0000", "precipitation"),
        ("P0001", "precipitation"),
        ("PP000", "precipitation"),
        ("PP012", "precipitation"),
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
    assert token not in _residual_tokens(tac, product)


@pytest.mark.parametrize(
    ("fragment", "tokens"),
    [
        ("A01 P000", ("A01", "P000")),
        ("A02 PP000", ("A02", "PP000")),
        ("AO1 P0000", ("AO1", "P0000")),
        ("AO2 P0001", ("AO2", "P0001")),
        ("AO2A PP012", ("AO2A", "PP012")),
    ],
)
@pytest.mark.parametrize("product", ["METAR", "SPECI"])
@pytest.mark.parametrize("with_rmk", [True, False])
def test_ao_plus_precip_combo_not_residual(
    fragment: str,
    tokens: tuple[str, ...],
    product: str,
    with_rmk: bool,
) -> None:
    """AO + precip pairs clear together with or without RMK."""
    mid = f"RMK {fragment}" if with_rmk else fragment
    tac = f"{product} KSVE {_BODY} {mid}"
    residual = _residual_tokens(tac, product)
    codes = _codes(tac, product)
    for tok in tokens:
        assert tok in codes
        assert tok not in residual


# ---------------------------------------------------------------------------
# F — Failure / residual / malformed addenda
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "bad_token",
    [
        "A03",
        "AO3",
        "AO0",
        "A00",
        "P00",
        "P0",
        "P00000",
        "PP00",
        "PP0",
        "PP0000",
        "PA00",
        "PPP000",
    ],
)
@pytest.mark.parametrize("product", ["METAR", "SPECI"])
@pytest.mark.parametrize("with_rmk", [True, False])
def test_malformed_addenda_remain_residual(
    bad_token: str,
    product: str,
    with_rmk: bool,
) -> None:
    """Malformed AO/precip-shaped tokens stay unexplained residuals."""
    mid = f"RMK {bad_token}" if with_rmk else bad_token
    tac = f"{product} KSVE {_BODY} {mid}"
    codes = _codes(tac, product)
    residuals = _residual_tokens(tac, product)
    assert bad_token not in codes or "automated" not in codes.get(bad_token, "").lower()
    # Must appear as residual text (not decoded as precip/AO).
    assert bad_token in residuals
    assert _us_precip_addenda(bad_token) is None


@pytest.mark.parametrize(
    ("good", "bad"),
    [
        ("A01", "A03"),
        ("P000", "P00"),
        ("PP000", "PP00"),
    ],
)
def test_mixed_good_and_malformed_partial_clear(good: str, bad: str) -> None:
    """Valid addendum clears; sibling malformed token stays residual."""
    tac = f"METAR KSVE {_BODY} RMK {good} {bad}"
    codes = _codes(tac, "METAR")
    residuals = _residual_tokens(tac, "METAR")
    assert good in codes
    assert good not in residuals
    assert bad in residuals
    assert bad not in codes or codes[bad] != codes[good]


# ---------------------------------------------------------------------------
# V+ / V- — Pack validation accept and reject
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("pack_id", ["metar", "speci"])
@pytest.mark.parametrize(
    ("token", "rule_substr"),
    [
        ("A01", "ao"),
        ("A02", "ao"),
        ("AO1", "ao"),
        ("AO2", "ao"),
        ("AO2A", "ao"),
        ("P000", "precip"),
        ("P0000", "precip"),
        ("PP000", "precip"),
        ("PP012", "precip"),
    ],
)
def test_pack_rules_accept_ao_and_precip(
    pack_id: str,
    token: str,
    rule_substr: str,
) -> None:
    """Pack residual policy names AO / precip addenda (validation accept)."""
    codes = _pack_spans(token, pack_id)
    rules = _pack_rule_ids(token, pack_id)
    assert token in codes
    explanation = codes[token].lower()
    assert "token " not in explanation
    assert "automated" in explanation or "precip" in explanation
    assert rule_substr in rules[token].lower()


@pytest.mark.parametrize("pack_id", ["metar", "speci"])
@pytest.mark.parametrize(
    "bad_token",
    ["A03", "AO3", "P00", "P00000", "PP00", "PP0000", "PA00"],
)
def test_pack_rules_reject_malformed_addenda(pack_id: str, bad_token: str) -> None:
    """Malformed addenda do not match ao_sensor / precip_* rules (validation fail)."""
    rules = _pack_rule_ids(bad_token, pack_id)
    codes = _pack_spans(bad_token, pack_id)
    assert bad_token in rules
    rule_id = rules[bad_token]
    assert rule_id not in {"ao_sensor", "ao2a", "precip_hourly", "precip_pp_mm"}
    # Falls through to station or generic token — not precip/AO explain.
    explanation = codes[bad_token].lower()
    assert "precipitation" not in explanation
    assert "automated station sensor" not in explanation


# ---------------------------------------------------------------------------
# Helper unit: _us_precip_addenda create-like classify (non-mutating decode)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("token", "expect_substr"),
    [
        ("P0000", "trace"),
        ("P0001", "0.01"),
        ("P012", "0.12"),
        ("P000", "trace"),
        ("PP000", "0.0 mm"),
        ("PP015", "1.5 mm"),
    ],
)
def test_us_precip_addenda_phrases(token: str, expect_substr: str) -> None:
    """Helper accepts well-formed precip shapes with expected phrasing."""
    phrase = _us_precip_addenda(token)
    assert phrase is not None
    assert expect_substr in phrase


@pytest.mark.parametrize("token", ["P0", "P00", "P00000", "PP0", "PP00", "PP0000", "X000"])
def test_us_precip_addenda_rejects_malformed(token: str) -> None:
    """Helper returns None for shapes outside P### / P#### / PP###."""
    assert _us_precip_addenda(token) is None


# ---------------------------------------------------------------------------
# Combinatorial: product x RMK x AO x precip (success cell)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("product", ["METAR", "SPECI"])
@pytest.mark.parametrize("with_rmk", [True, False])
@pytest.mark.parametrize("ao", ["A01", "AO2"])
@pytest.mark.parametrize("precip", ["P000", "PP000"])
def test_product_rmk_ao_precip_matrix(
    product: str,
    with_rmk: bool,
    ao: str,
    precip: str,
) -> None:
    """Full product x RMK x AO x precip success permutation."""
    mid = f"RMK {ao} {precip}" if with_rmk else f"{ao} {precip}"
    tac = f"{product} KSVE {_BODY} {mid}"
    codes = _codes(tac, product)
    residuals = _residual_tokens(tac, product)
    assert ao in codes
    assert precip in codes
    assert ao not in residuals
    assert precip not in residuals

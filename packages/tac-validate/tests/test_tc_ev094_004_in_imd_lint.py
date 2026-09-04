"""TC-EV094-004 — IN_IMD TAF TX/TN lint overlay (M5 / #1098).

[Corpus: product §F36] [Corpus: tests §TC-EV094-004] [Corpus: decisions §D-EV094-in-taf]
"""

from __future__ import annotations

import pytest
from tac_validate import lint

# AWC-style VIDP TAF without TX/TN (national omission practice).
_TAF_NO_TX_TN = "TAF VIDP 311400Z 3115/3124 27006KT 5000 HZ BR FEW035 SCT100 BECMG 3121/3123 25010G20KT 3000 BR="

_TAF_WITH_TX_TN = "TAF VIDP 311400Z 3115/3124 27006KT 5000 HZ FEW035 SCT100 TX32/3115Z TN24/3123Z="


def _codes(tac: str, *, product: str = "TAF", profile: str) -> set[str]:
    return {i.code for i in lint(tac, product=product, profile=profile).issues}


def test_tc_ev094_004_in_imd_emits_omit_info_when_tx_tn_absent() -> None:
    """profile=in_imd on TAF without TX/TN emits IN_TAF_TX_TN_OMITTED."""
    codes = _codes(_TAF_NO_TX_TN, profile="in_imd")
    assert "IN_TAF_TX_TN_OMITTED" in codes


def test_tc_ev094_004_in_imd_alias_uppercase() -> None:
    """IN_IMD alias normalizes to in_imd and emits the same awareness code."""
    codes = _codes(_TAF_NO_TX_TN, profile="IN_IMD")
    assert "IN_TAF_TX_TN_OMITTED" in codes


def test_tc_ev094_004_annex3_unchanged_for_same_tac() -> None:
    """annex3 path does not emit the IN overlay code for the same TAC."""
    codes = _codes(_TAF_NO_TX_TN, profile="annex3")
    assert "IN_TAF_TX_TN_OMITTED" not in codes


def test_tc_ev094_004_in_imd_no_omit_when_tx_tn_present() -> None:
    """When TX/TN are present under in_imd, omit-awareness code is absent."""
    codes = _codes(_TAF_WITH_TX_TN, profile="in_imd")
    assert "IN_TAF_TX_TN_OMITTED" not in codes
    assert "TX_TN_PRESENT" in codes


def test_tc_ev094_004_in_imd_rejects_non_taf() -> None:
    """in_imd is TAF-only — other products raise ValueError."""
    with pytest.raises(ValueError, match="in_imd is not applicable"):
        lint("METAR VIDP 311500Z 24004KT 5000 HZ FEW035 32/23 Q1003=", product="METAR", profile="in_imd")

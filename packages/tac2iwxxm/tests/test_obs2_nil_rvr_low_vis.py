"""Observation-2: nil RVR when prevailing visibility is below 1500 m.

[Corpus: product §F6] [Corpus: product §F2]
"""

from __future__ import annotations

from tac2iwxxm.profiles import annex3 as a3


def test_rvr_block_nils_when_visibility_below_1500_without_rvr() -> None:
    block = a3._rvr_block({"visibility_m": 1207})
    assert 'iwxxm:rvr xsi:nil="true"' in block
    assert a3.NIL_MISSING in block


def test_rvr_block_omits_when_visibility_at_or_above_1500_without_rvr() -> None:
    assert a3._rvr_block({"visibility_m": 1500}) == ""
    assert a3._rvr_block({"visibility_m": 3200}) == ""


def test_convert_low_sm_vis_without_rvr_includes_nil_rvr() -> None:
    from tac2iwxxm import convert

    result = convert(
        "METAR CYBR 021400Z 04010KT 3/4SM BR OVC002 10/10 A2979=",
        product="METAR",
        profile="annex3",
        iwxxm_version="2025-2",
    )
    assert result.ok
    assert result.xml is not None
    assert 'iwxxm:rvr xsi:nil="true"' in result.xml

"""BUG-2026-07-30 - SPECI A3-2 F9 decode must not residual min-vis/cloud/trends/NSW.

Annex 3 SPECI A3-2 converts cleanly to IWXXM, but ``decode_tac`` left
``1200NE``, ``BKN005CB``, ``TEMPO``/``TL1200``, ``BECMG``/``AT1200``, and ``NSW``
as residuals in the operator CODE / PLAIN LANGUAGE panel.
"""

from __future__ import annotations

from pathlib import Path

from tac2iwxxm.decode import decode_tac

ROOT = Path(__file__).resolve().parents[2]
SPECI_A3_2 = (
    (
        ROOT
        / "packages"
        / "tac2iwxxm"
        / "tests"
        / "fixtures"
        / "annex3_golden"
        / "speci_a3_2.tac"
    )
    .read_text(encoding="utf-8")
    .strip()
)

# Tokens that must be explained individually (not coalesced into residuals).
_MUST_EXPLAIN = (
    "1200NE",
    "BKN005CB",
    "TEMPO",
    "TL1200",
    "BECMG",
    "AT1200",
    "NSW",
)


def test_speci_a3_2_decode_explains_min_vis_cloud_trends_nsw() -> None:
    """WMO SPECI A3-2 decode must cover groups convert already emits to IWXXM."""
    result = decode_tac(SPECI_A3_2, product="SPECI")
    by_code = {seg.code: seg.explanation for seg in result.segments}
    residual_text = " ".join(r.text for r in result.residuals)

    for token in _MUST_EXPLAIN:
        assert token in by_code, (
            f"expected segment for {token!r}; residuals={residual_text!r}; "
            f"codes={sorted(by_code)}"
        )
        assert by_code[token].strip(), f"empty explanation for {token!r}"

    assert "1200" in by_code["1200NE"]
    assert "NE" in by_code["1200NE"] or "northeast" in by_code["1200NE"].lower()
    assert "500" in by_code["BKN005CB"] or "5,00" in by_code["BKN005CB"]
    assert "cumulonimbus" in by_code["BKN005CB"].lower() or "CB" in by_code["BKN005CB"]
    assert "temporary" in by_code["TEMPO"].lower() or "TEMPO" in by_code["TEMPO"]
    assert "12:00" in by_code["TL1200"] or "1200" in by_code["TL1200"]
    assert "becoming" in by_code["BECMG"].lower() or "BECMG" in by_code["BECMG"]
    assert "12:00" in by_code["AT1200"] or "1200" in by_code["AT1200"]
    assert "weather" in by_code["NSW"].lower() or "NSW" in by_code["NSW"]

    for token in _MUST_EXPLAIN:
        assert token not in residual_text, (
            f"{token!r} still in residuals: {residual_text!r}"
        )

    assert "Not decoded:" not in result.summary or not any(
        t in result.summary for t in ("1200NE", "BKN005CB", "TEMPO", "BECMG", "NSW")
    )

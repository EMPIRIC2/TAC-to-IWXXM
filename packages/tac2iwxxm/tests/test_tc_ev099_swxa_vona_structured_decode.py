"""TC-EV099 — structured SWXA/VONA decode (#1119 / EV-099).

Major LABEL: fields become segments; whole-TAC residuals are forbidden.
Meaningful explicit leftovers may remain via exact allowlist (not allow_any).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from tac2iwxxm.decode import decode_tac

_FIXTURES = Path(__file__).resolve().parent / "fixtures"
if str(_FIXTURES) not in sys.path:
    sys.path.insert(0, str(_FIXTURES))

from wmo_decode_residual_allowlist import allows_any_residual  # noqa: E402

ANNEX3 = Path(__file__).resolve().parent / "fixtures" / "annex3_golden"

_PEERS: tuple[tuple[str, str], ...] = (
    ("VONA", "vona_a7_1"),
    ("SWXA", "swxa_a7_3"),
    ("SWXA", "swxa_a7_4"),
    ("SWXA", "swxa_a7_5"),
)


@pytest.mark.parametrize(("product", "stem"), _PEERS)
def test_tc_ev099_001_major_field_labels_are_segments(product: str, stem: str) -> None:
    tac = (ANNEX3 / f"{stem}.tac").read_text(encoding="utf-8")
    result = decode_tac(tac, product=product)
    blob = " | ".join(f"{s.code}::{s.explanation}" for s in result.segments).lower()
    assert result.segments, f"{stem}: expected structured segments"
    if product == "VONA":
        for needle in (
            "dtg",
            "volcano",
            "psn",
            "notice nr",
            "current colour code",
            "svo",
            "va cld hgt",
            "nxt notice",
        ):
            assert needle in blob, f"{stem}: missing structured field {needle!r}"
    else:
        for needle in (
            "dtg",
            "swxc",
            "swx effect",
            "advisory nr",
            "obs swx",
            "fcst swx +6 hr",
            "nxt advisory",
        ):
            assert needle in blob, f"{stem}: missing structured field {needle!r}"


@pytest.mark.parametrize(("product", "stem"), _PEERS)
def test_tc_ev099_002_no_whole_tac_residual(product: str, stem: str) -> None:
    tac = (ANNEX3 / f"{stem}.tac").read_text(encoding="utf-8")
    result = decode_tac(tac, product=product)
    whole = [r for r in result.residuals if r.start == 0 and r.end == len(tac)]
    assert not whole, f"{stem}: whole-TAC residual still present: {whole!r}"
    assert not allows_any_residual(stem), f"{stem}: allow_any must be removed"


@pytest.mark.parametrize(("product", "stem"), _PEERS)
def test_tc_ev099_003_meaningful_residuals_only(product: str, stem: str) -> None:
    """Leftovers (if any) must be small vs body — not the bulk of the TAC."""
    tac = (ANNEX3 / f"{stem}.tac").read_text(encoding="utf-8")
    result = decode_tac(tac, product=product)
    residual_chars = sum(len(r.text) for r in result.residuals if r.text.strip())
    assert residual_chars < len(tac) // 2, (
        f"{stem}: residual chars {residual_chars} still dominate body len {len(tac)}; residuals={result.residuals!r}"
    )


def test_tc_ev099_004_convert_vona_peer_xml_bit_identical() -> None:
    """Decode-only change must not alter annex3 convert for VONA peer.

    SWXA golden soft-equality is covered by F28 packs; stage tip already has
    non-decode drift on some SWXA goldens — do not couple EV-099 to that.
    """
    from tac2iwxxm.convert import convert

    from metar_shared.xml_canonical import canonicalize_xml

    tac = (ANNEX3 / "vona_a7_1.tac").read_text(encoding="utf-8")
    golden = (ANNEX3 / "vona_a7_1.golden.xml").read_text(encoding="utf-8")
    result = convert(tac, product="VONA")
    assert canonicalize_xml(result.xml) == canonicalize_xml(golden)


def test_tc_ev099_004b_swxa_convert_still_emits_root() -> None:
    from tac2iwxxm.convert import convert

    tac = (ANNEX3 / "swxa_a7_3.tac").read_text(encoding="utf-8")
    result = convert(tac, product="SWXA")
    assert "SpaceWeatherAdvisory" in result.xml

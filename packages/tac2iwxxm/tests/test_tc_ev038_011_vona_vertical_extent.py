"""TC-EV038-011 - VONA VolcanicAshCloudVerticalExtent (G-VONA-1 / #849).

When TAC supplies ``HGT SOURCE`` / ``MOV`` on a non-A7-1 path, ash
``phenomenonProperty`` must carry ``VolcanicAshCloudVerticalExtent`` per XSD
(not ``iwxxm/nil/inapplicable``). Official ``vona-A7-1`` peer keeps inapplicable
(ADR-032 golden). No invented packing - MOV tokens map to XSD enum only.

Corpus: product F32; tests TC-EV038-011; decisions AC11.
"""

from __future__ import annotations

from pathlib import Path

import pytest

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "vona"
ACCEPT_TAC = FIXTURES / "vona_vertical_extent_accept.tac"
A7_TAC = Path(__file__).resolve().parent / "fixtures" / "annex3_golden" / "vona_a7_1.tac"
IWXXM_VERSION = "2025-2"
PROFILE = "annex3"


def test_tc_ev038_011_parse_carries_height_source_and_movement() -> None:
    from tac2iwxxm.products.vona import parse_vona

    ir = parse_vona(ACCEPT_TAC.read_text(encoding="utf-8"), product="VONA")
    assert ir["height_source"] == "GRD OBSERVER"
    assert ir["movement"] == "SW"
    assert ir["ash_cloud_height_m"] == 6000.0
    # Non-peer fingerprint (notice / volcano / SVO / DTG differ from A7-1).
    assert ir["notice_number"] == "2024/1"
    assert ir["volcano_name"] == "ETNA"


def test_tc_ev038_011_encode_vertical_extent_when_tac_supplies_hgt_mov() -> None:
    """Accept path: encode VolcanicAshCloudVerticalExtent from HGT SOURCE / MOV."""
    from tac2iwxxm import convert

    result = convert(
        ACCEPT_TAC.read_text(encoding="utf-8"),
        product="VONA",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"convert failed: {result.issues!r}"
    xml = result.xml
    assert "VolcanicAshCloudVerticalExtent" in xml
    assert "<iwxxm:heightSource>GRD OBSERVER</iwxxm:heightSource>" in xml
    assert "<iwxxm:movement>SW</iwxxm:movement>" in xml
    # Must not use A7-1 inapplicable nil on this deepen path.
    assert 'phenomenonProperty nilReason="http://codes.wmo.int/iwxxm/nil/inapplicable"' not in xml


def test_tc_ev038_011_a7_1_peer_keeps_inapplicable_ash_property() -> None:
    """Official A7-1 golden path unchanged (G-VONA-1 peer match)."""
    from tac2iwxxm import convert

    result = convert(
        A7_TAC.read_text(encoding="utf-8"),
        product="VONA",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True
    assert "VolcanicAshCloudVerticalExtent" not in result.xml
    assert "iwxxm/nil/inapplicable" in result.xml


def test_tc_ev038_011_negative_unknown_mov_token() -> None:
    """Negative: MOV outside XSD enum → quarantine (product-shaped TAC)."""
    from tac2iwxxm import convert

    tac = ACCEPT_TAC.read_text(encoding="utf-8").replace("MOV:\t\t\tSW", "MOV:\t\t\tXYZ")
    result = convert(tac, product="VONA", profile=PROFILE, iwxxm_version=IWXXM_VERSION)
    assert result.ok is True  # translationFailedTAC quarantine shell
    assert "translationFailedTAC" in result.xml
    assert "VolcanicAshCloudVerticalExtent" not in result.xml
    joined = " ".join(f"{i.code}:{i.message}" for i in (result.issues or []))
    assert "TRANSLATION_FAILED" in joined
    assert "MOV" in joined.upper() or "movement" in joined.lower()


@pytest.mark.parametrize(
    ("token", "expected"),
    [
        ("N", "N"),
        ("NE", "NE"),
        ("VERTICAL", "VERTICAL"),
        ("UNKNOWN", "UNKNOWN"),
        ("OBSCURED", "OBSCURED"),
    ],
)
def test_tc_ev038_011_mov_enum_tokens(token: str, expected: str) -> None:
    from tac2iwxxm import convert

    tac = ACCEPT_TAC.read_text(encoding="utf-8").replace("MOV:\t\t\tSW", f"MOV:\t\t\t{token}")
    result = convert(tac, product="VONA", profile=PROFILE, iwxxm_version=IWXXM_VERSION)
    assert result.ok is True, f"token {token!r}: {result.issues!r}"
    assert f"<iwxxm:movement>{expected}</iwxxm:movement>" in result.xml


def test_tc_ev038_011_vertical_extent_m_xsd_sch() -> None:
    """T4.3 / TC-EV038-011 - accept encode is M-xsd/M-sch clean."""
    from iwxxm_validate import validate

    from tac2iwxxm import convert

    result = convert(
        ACCEPT_TAC.read_text(encoding="utf-8"),
        product="VONA",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True
    assert "VolcanicAshCloudVerticalExtent" in result.xml
    report = validate(
        result.xml,
        iwxxm_version=IWXXM_VERSION,
        profile=PROFILE,
        levels=("xsd", "schematron"),
    )
    blocking = [i for i in report.issues if i.severity == "error" and i.code not in {"SCHEMATRON_SKIPPED"}]
    assert not blocking, f"M-xsd/M-sch blocking: {[(i.code, i.message) for i in blocking]}"

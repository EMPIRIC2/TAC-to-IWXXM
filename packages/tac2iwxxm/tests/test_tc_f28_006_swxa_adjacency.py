"""TC-F28-006 — SWXA adjacency + AHL FN→LN (S036 / EV-029 T11.4 / F28).

SWXA never mis-roots as SIGMET/VAA/TCA; AHL ``FN`` maps to IWXXM ``LN``;
``split_bulletin(product=SWXA)`` accepts FN + SWX ADVISORY bodies.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest
from tac_validate import lint

from tac2iwxxm import convert, iwxxm_filename, map_t1t2, parse_ahl, split_bulletin

FIXTURES = Path(__file__).resolve().parent / "fixtures"
ANNEX3 = FIXTURES / "annex3_golden"
AHL = FIXTURES / "ahl"
SWXA = FIXTURES / "swxa"
TAC_VALIDATE = Path(__file__).resolve().parents[2] / "tac-validate" / "tests" / "fixtures" / "accept"

_PROFILE = "annex3"
_VERSION = "2025-2"


def _has_root(xml: str, local: str) -> bool:
    return f"<iwxxm:{local} " in xml


def test_tc_f28_006_fn_maps_to_ln() -> None:
    assert map_t1t2("FN") == "LN"
    parts = parse_ahl((AHL / "fn_swxa.txt").read_text(encoding="utf-8").strip())
    assert parts.tt == "FN"
    assert parts.iwxxm_tt == "LN"
    name = iwxxm_filename(parts, issued_at=datetime(2026, 8, 2, 1, 0, 0, tzinfo=UTC))
    assert name.startswith("A_LN")
    assert "FNUS" not in name or name.startswith("A_LN")  # TAC FN must not be A_ segment
    assert "LNUS01" in name or "LN" in name[:6]


def test_tc_f28_006_split_bulletin_swxa() -> None:
    text = (SWXA / "swxa_ahl_normal.txt").read_text(encoding="utf-8")
    split = split_bulletin(text, product="SWXA")
    assert split.meta.tt == "FN"
    assert split.meta.report_count == 1
    assert split.reports[0].startswith("SWX ADVISORY")
    result = convert(
        split.reports[0],
        product="SWXA",
        profile=_PROFILE,
        iwxxm_version=_VERSION,
    )
    assert result.ok is True
    assert _has_root(result.xml, "SpaceWeatherAdvisory")


def test_tc_f28_006_swxa_keeps_space_weather_root() -> None:
    tac = (ANNEX3 / "swxa_a7_3.tac").read_text(encoding="utf-8")
    assert lint(tac, product="SWXA").ok is True
    result = convert(tac, product="SWXA", profile=_PROFILE, iwxxm_version=_VERSION)
    assert result.ok is True
    assert result.product == "SWXA"
    assert _has_root(result.xml, "SpaceWeatherAdvisory")
    assert not _has_root(result.xml, "SIGMET")
    assert not _has_root(result.xml, "VolcanicAshAdvisory")
    assert not _has_root(result.xml, "TropicalCycloneAdvisory")
    assert not _has_root(result.xml, "VolcanicAshSIGMET")


@pytest.mark.parametrize(
    ("wrong_product", "fixture"),
    (
        ("SIGMET", "swxa_a7_3.tac"),
        ("VAA", "swxa_a7_3.tac"),
        ("TCA", "swxa_a7_3.tac"),
    ),
)
def test_tc_f28_006_swxa_rejected_as_neighbor(wrong_product: str, fixture: str) -> None:
    tac = (ANNEX3 / fixture).read_text(encoding="utf-8")
    assert lint(tac, product=wrong_product).ok is False
    bad = convert(tac, product=wrong_product, profile=_PROFILE, iwxxm_version=_VERSION)
    assert bad.ok is False


def test_tc_f28_006_neighbors_rejected_as_swxa() -> None:
    for fname, product in (
        ("sigmet_basic.tac", "SIGMET"),
        ("vaa_basic.tac", "VAA"),
        ("tca_basic.tac", "TCA"),
    ):
        path = TAC_VALIDATE / fname if (TAC_VALIDATE / fname).is_file() else ANNEX3 / fname
        tac = path.read_text(encoding="utf-8")
        assert lint(tac, product="SWXA").ok is False, fname
        bad = convert(tac, product="SWXA", profile=_PROFILE, iwxxm_version=_VERSION)
        assert bad.ok is False, fname

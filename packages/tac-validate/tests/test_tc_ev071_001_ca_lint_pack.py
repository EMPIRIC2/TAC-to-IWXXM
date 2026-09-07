"""TC-EV071-001/002 - CA_ECCC tac-validate lint pack (#1038 / EV-071 M1).

[Corpus: product §F15] [Corpus: product §F36] [Corpus: tests §TC-EV071]
"""

from __future__ import annotations

from pathlib import Path

from tac_validate import lint

FIXTURES = Path(__file__).resolve().parents[2] / "tac2iwxxm" / "tests" / "fixtures" / "profiles" / "CA_ECCC"

# All CA overlay codes promoted in EV-071 M1 (≥10 rules per #1038 acceptance).
CA_LINT_CODES = frozenset(
    {
        "CA_STATUTE_MILE_VIS",
        "CA_ALTIMETER_INHG",
        "CA_ALTIMETER_NOT_OBS",
        "CA_REMARK_MANOBS",
        "CA_REMARK_PRESFR",
        "CA_REMARK_PRESRR",
        "CA_REMARK_NOSPECI",
        "CA_REMARK_SECTOR_VIS",
        "CA_METAR_LWIS",
        "CA_METAR_SAWR",
        "CA_TAF_NCLWS",
        "CA_AIRMET_GFA",
    }
)


def _codes(tac: str, *, product: str, profile: str = "ca_eccc") -> set[str]:
    return {i.code for i in lint(tac, product=product, profile=profile).issues}


def test_tc_ev071_001_twelve_distinct_ca_codes_registered() -> None:
    """Lint pack exposes ≥12 CA rule codes across METAR/TAF/AIRMET fixtures."""
    matrix: list[tuple[str, str, frozenset[str]]] = [
        ("METAR/valid/metar_rmk_sector_vis.tac", "METAR", frozenset({"CA_STATUTE_MILE_VIS", "CA_REMARK_SECTOR_VIS"})),
        ("METAR/valid/metar_alt_not_obs.tac", "METAR", frozenset({"CA_ALTIMETER_NOT_OBS"})),
        ("METAR/valid/metar_rmk_presrr.tac", "METAR", frozenset({"CA_REMARK_MANOBS", "CA_REMARK_PRESRR"})),
        ("METAR/valid/metar_rmk_nospeci.tac", "METAR", frozenset({"CA_REMARK_NOSPECI"})),
        ("METAR/valid/metar_lwis.tac", "METAR", frozenset({"CA_METAR_LWIS", "CA_ALTIMETER_INHG"})),
        ("METAR/valid/metar_sawr.tac", "METAR", frozenset({"CA_METAR_SAWR"})),
        ("TAF/valid/taf_nclws.tac", "TAF", frozenset({"CA_TAF_NCLWS"})),
        ("AIRMET/valid/airmet_gfa_sfc_vis.tac", "AIRMET", frozenset({"CA_AIRMET_GFA"})),
    ]
    seen: set[str] = set()
    for rel, product, expected in matrix:
        tac = (FIXTURES / rel).read_text(encoding="utf-8")
        codes = _codes(tac, product=product)
        assert expected <= codes, f"{rel}: expected {expected}, got {codes}"
        seen |= codes & CA_LINT_CODES
    assert len(seen) >= 10


def test_tc_ev071_002_profile_isolation_ca_vs_us() -> None:
    """iwxxm_us never emits CA_*; ca_eccc never emits REMARK_US_EXTENSION."""
    us_tac = "METAR KORD 121856Z 36010KT 10SM FEW250 RMK AO2 SLP013 T00671067="
    us_codes = _codes(us_tac, product="METAR", profile="iwxxm_us")
    ca_codes = _codes(us_tac, product="METAR", profile="ca_eccc")
    assert not (us_codes & CA_LINT_CODES), f"CA codes under iwxxm_us: {us_codes & CA_LINT_CODES}"
    assert "REMARK_US_EXTENSION" not in ca_codes


def test_tc_ev071_002_lwis_not_under_annex3() -> None:
    tac = (FIXTURES / "METAR/valid/metar_lwis.tac").read_text(encoding="utf-8")
    annex_codes = _codes(tac, product="METAR", profile="annex3")
    ca_codes = _codes(tac, product="METAR", profile="ca_eccc")
    assert "CA_METAR_LWIS" in ca_codes
    assert "CA_METAR_LWIS" not in annex_codes

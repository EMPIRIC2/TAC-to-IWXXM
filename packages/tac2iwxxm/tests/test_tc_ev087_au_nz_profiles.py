"""TC-EV087-001..006 — AU_BOM + NZ_CAA_MET P1 kickoff (EV-087 / #917+#918).

[Corpus: product §F36] [Corpus: domain-profiles] [Corpus: tests §TC-EV087]
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from tac2iwxxm.products.taf import parse_taf
from tac2iwxxm.profile_registry import (
    EMIT_AU_BOM,
    EMIT_NZ_CAA_MET,
    known_semantic_profile_ids,
    resolve_semantic_profile,
)

from tac2iwxxm import convert

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "profiles"
AU = FIXTURES / "AU_BOM"
NZ = FIXTURES / "NZ_CAA_MET"
METAR_BASIC = (Path(__file__).resolve().parent / "fixtures" / "annex3_golden" / "metar_basic.tac").read_text(
    encoding="utf-8"
)


def test_tc_ev087_001_registry_resolves_au_and_nz() -> None:
    """Canonical wire ids resolve to emit keys au_bom / nz_caa_met."""
    au = resolve_semantic_profile("AU_BOM")
    nz = resolve_semantic_profile("NZ_CAA_MET")
    assert au is not None
    assert nz is not None
    assert au.emit_key == EMIT_AU_BOM
    assert nz.emit_key == EMIT_NZ_CAA_MET
    assert au.canonical == "au_bom"
    assert nz.canonical == "nz_caa_met"
    known = known_semantic_profile_ids()
    assert "au_bom" in known
    assert "nz_caa_met" in known
    assert resolve_semantic_profile("au_bom") is not None
    assert resolve_semantic_profile("nz_caa_met") is not None


def test_tc_ev087_002_au_inter_parsed_distinct_from_tempo() -> None:
    """Under AU_BOM, INTER is a distinct IR change-group (not TEMPO-only)."""
    tac = (AU / "TAF" / "valid" / "taf_inter.tac").read_text(encoding="utf-8")
    ir = parse_taf(tac)
    changes = ir.get("change_forecasts") or []
    inter = [c for c in changes if c.get("tac_change_indicator") == "INTER"]
    assert len(inter) == 1
    assert inter[0]["change_indicator"] == "TEMPORARY_FLUCTUATIONS"
    assert "INTER" in (ir.get("national_remark_tokens") or [])
    # FM is also present and must remain labeled FROM (not collapsed into INTER).
    assert any(c.get("change_indicator") == "FROM" for c in changes)


def test_tc_ev087_003_au_inter_emit_policy_no_invented_enum() -> None:
    """Converted IWXXM uses TEMPORARY_FLUCTUATIONS; INTER preserved in diagnostics."""
    tac = (AU / "TAF" / "valid" / "taf_inter.tac").read_text(encoding="utf-8")
    result = convert(tac, product="TAF", profile="AU_BOM")
    assert result.ok, result.issues
    assert result.xml is not None
    assert 'changeIndicator="TEMPORARY_FLUCTUATIONS"' in result.xml
    assert 'changeIndicator="INTER"' not in result.xml
    assert result.ir is not None
    inter = [c for c in (result.ir.get("change_forecasts") or []) if c.get("tac_change_indicator") == "INTER"]
    assert inter
    codes = {i.code for i in result.issues}
    assert "NATIONAL_TAC_PROVENANCE" in codes
    msg = next(i.message for i in result.issues if i.code == "NATIONAL_TAC_PROVENANCE")
    assert "INTER" in msg


def test_tc_ev087_004_au_taf3_rmk_flag() -> None:
    """TAF3 / TAF3 VALID TL detected under product=TAF."""
    tac = (AU / "TAF" / "valid" / "taf_taf3.tac").read_text(encoding="utf-8")
    ir = parse_taf(tac)
    assert ir.get("au_taf3") is True
    assert "TAF3" in str(ir.get("au_taf3_token") or "")
    result = convert(tac, product="TAF", profile="AU_BOM")
    assert result.ok, result.issues
    assert result.product == "TAF"
    assert result.ir is not None
    assert result.ir.get("au_taf3") is True


def test_tc_ev087_005_nz_domestic_vs_international() -> None:
    """Domestic extras parsed; international path remains Annex 3-shaped."""
    dom_tac = (NZ / "TAF" / "valid" / "taf_domestic.tac").read_text(encoding="utf-8")
    intl_tac = (NZ / "TAF" / "valid" / "taf_international.tac").read_text(encoding="utf-8")
    dom = parse_taf(dom_tac)
    intl = parse_taf(intl_tac)
    assert dom.get("nz_taf_dialect") == "domestic"
    assert dom.get("visibility_km") == 30
    assert dom.get("nz_2000ft_wind", {}).get("wind_speed_kt") == 20
    assert dom.get("nz_qnh_mnm_hpa") == 1015
    assert dom.get("nz_qnh_max_hpa") == 1024
    assert intl.get("nz_taf_dialect") == "international"
    assert intl.get("nz_2000ft_wind") is None
    result = convert(dom_tac, product="TAF", profile="NZ_CAA_MET")
    assert result.ok, result.issues
    codes = {i.code for i in result.issues}
    assert "NATIONAL_TAC_PROVENANCE" in codes


def test_tc_ev087_006_unknown_semantic_still_fail_closed() -> None:
    """Garbage semantic id still rejected; ICAO path still works."""
    bad = convert(METAR_BASIC, product="METAR", profile="NOT_A_PROFILE")
    assert not bad.ok
    assert bad.issues[0].code == "UNSUPPORTED_PROFILE"
    ok = convert(METAR_BASIC, product="METAR", profile="ICAO_2025")
    assert ok.ok
    # AU/NZ registration must not break CA resolve.
    assert resolve_semantic_profile("CA_ECCC") is not None


@pytest.mark.parametrize(
    ("root", "profile"),
    [
        (AU, "AU_BOM"),
        (NZ, "NZ_CAA_MET"),
    ],
)
def test_tc_ev087_manifest_layout(root: Path, profile: str) -> None:
    """Fixture manifests exist with expected profile id."""
    manifest_path = root / "manifest.json"
    assert manifest_path.is_file()
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert data.get("profile") == profile
    assert data.get("cases")
    for case in data["cases"]:
        tac_path = root / case["tac"]
        assert tac_path.is_file(), tac_path

"""TC-EV089 — thin/compat national packs (#920 / EV-089).

[Corpus: product §F36] [Corpus: domain-profiles] [Corpus: tests §TC-EV089]
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from tac2iwxxm.profile_registry import (
    EMIT_BR_DECEA,
    EMIT_HK_HKO,
    EMIT_IN_IMD,
    EMIT_JP_JMA,
    EMIT_KR_KMA,
    EMIT_UK_METOFFICE,
    known_semantic_profile_ids,
    resolve_semantic_profile,
)

from tac2iwxxm import convert

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "profiles"
METAR_BASIC = (Path(__file__).resolve().parent / "fixtures" / "annex3_golden" / "metar_basic.tac").read_text(
    encoding="utf-8"
)

PROFILE_IDS = (
    "UK_METOFFICE",
    "BR_DECEA",
    "KR_KMA",
    "JP_JMA",
    "IN_IMD",
    "HK_HKO",
)
EMIT_BY_ID = {
    "UK_METOFFICE": EMIT_UK_METOFFICE,
    "BR_DECEA": EMIT_BR_DECEA,
    "KR_KMA": EMIT_KR_KMA,
    "JP_JMA": EMIT_JP_JMA,
    "IN_IMD": EMIT_IN_IMD,
    "HK_HKO": EMIT_HK_HKO,
}


def test_tc_ev089_001_registry_resolves_six_packs() -> None:
    """Canonical wire ids resolve to thin/compat emit keys."""
    known = known_semantic_profile_ids()
    for pid in PROFILE_IDS:
        resolved = resolve_semantic_profile(pid)
        assert resolved is not None, pid
        assert resolved.emit_key == EMIT_BY_ID[pid]
        assert resolved.canonical == EMIT_BY_ID[pid]
        assert EMIT_BY_ID[pid] in known


@pytest.mark.parametrize("profile_id", PROFILE_IDS)
def test_tc_ev089_002_manifest_layout(profile_id: str) -> None:
    """Each profile has a manifest with on-disk TAC paths."""
    root = FIXTURES / profile_id
    data = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    assert data.get("profile") == profile_id
    assert data.get("cases")
    for case in data["cases"]:
        tac_path = root / case["tac"]
        assert tac_path.is_file(), tac_path


@pytest.mark.parametrize("profile_id", PROFILE_IDS)
def test_tc_ev089_005_006_convert_active_cases(profile_id: str) -> None:
    """Active (non parse_only) manifest cases convert under the profile id."""
    root = FIXTURES / profile_id
    data = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    for case in data["cases"]:
        if case.get("status") == "parse_only":
            continue
        tac = (root / case["tac"]).read_text(encoding="utf-8")
        result = convert(tac, product=case["product"], profile=profile_id)
        assert result.ok, (profile_id, case["id"], result.issues)


def test_tc_ev089_003_br_gamet_not_convertible() -> None:
    """GAMET fixtures exist but convert rejects GAMET product (parse-only)."""
    root = FIXTURES / "BR_DECEA"
    data = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    gamet = next(c for c in data["cases"] if c["product"] == "GAMET")
    assert gamet["status"] == "parse_only"
    assert (root / gamet["tac"]).is_file()
    tac = (root / gamet["tac"]).read_text(encoding="utf-8")
    bad_product = convert(tac, product="GAMET", profile="BR_DECEA")
    assert not bad_product.ok
    assert any(i.code == "UNSUPPORTED_PRODUCT" for i in bad_product.issues)
    # Convert allowlist for BR must not list GAMET (D-EV089-gamet).
    assert "GAMET" not in {c["product"] for c in data["cases"] if c.get("status") == "active"}


def test_tc_ev089_jp_airmet_unsupported() -> None:
    """JP_JMA v1 excludes AIRMET (D-EV089-jp-va)."""
    tac = (FIXTURES / "BR_DECEA" / "AIRMET" / "valid" / "airmet_basic.tac").read_text(encoding="utf-8")
    bad = convert(tac, product="AIRMET", profile="JP_JMA")
    assert not bad.ok
    assert any(i.code == "UNSUPPORTED_PROFILE" for i in bad.issues)


def test_tc_ev089_007_unknown_semantic_still_fail_closed() -> None:
    """Garbage semantic id still rejected; ICAO + prior nationals still resolve."""
    bad = convert(METAR_BASIC, product="METAR", profile="NOT_A_PROFILE")
    assert not bad.ok
    assert bad.issues[0].code == "UNSUPPORTED_PROFILE"
    assert convert(METAR_BASIC, product="METAR", profile="ICAO_2025").ok
    assert resolve_semantic_profile("AU_BOM") is not None
    assert resolve_semantic_profile("CA_ECCC") is not None


def test_tc_ev089_uk_sigmet_unsupported() -> None:
    """UK thin pack is METAR/SPECI/TAF only."""
    tac = (FIXTURES / "BR_DECEA" / "SIGMET" / "valid" / "sigmet_basic.tac").read_text(encoding="utf-8")
    bad = convert(tac, product="SIGMET", profile="UK_METOFFICE")
    assert not bad.ok
    assert any(i.code == "UNSUPPORTED_PROFILE" for i in bad.issues)

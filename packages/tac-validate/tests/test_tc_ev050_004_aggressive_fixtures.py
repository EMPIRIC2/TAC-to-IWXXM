"""TC-EV050-004 / AC4 - aggressive RE* / AIRMET_ / SpaceWx / TCU fixtures (S059)."""

from __future__ import annotations

import json
import re
from pathlib import Path

from tac_validate import lint, membership

FIXTURES = Path(__file__).resolve().parent / "fixtures"
MANIFEST = json.loads((FIXTURES / "manifest.json").read_text(encoding="utf-8"))


def _ev050_cases(bucket: str) -> list[dict[str, object]]:
    return [c for c in MANIFEST[bucket] if c.get("theme") == "EV050" or "ev050" in str(c.get("id", ""))]


def test_ev050_accept_recent_and_airmet_underscore_in_manifest() -> None:
    ids = {str(c["id"]) for c in MANIFEST["accept"]}
    assert "accept_metar_ev050_recent_rera" in ids
    assert "accept_airmet_ev050_phenomenon_underscore" in ids
    assert (FIXTURES / "accept/speci_r4_bkn_tcu.tac").is_file()


def test_ev050_negative_membership_cases_in_manifest() -> None:
    ids = {str(c["id"]) for c in MANIFEST["negative"]}
    assert "metar_unknown_recent_weather" in ids
    assert "airmet_unknown_phenomenon_underscore" in ids
    assert "swxa_unknown_effect" in ids


def test_accept_rera_and_underscore_airmet_lint_ok() -> None:
    for case_id in (
        "accept_metar_ev050_recent_rera",
        "accept_metar_ev050_recent_resn",
        "accept_airmet_ev050_phenomenon_underscore",
        "accept_airmet_ev050_mod_ice_underscore",
    ):
        case = next(c for c in MANIFEST["accept"] if c["id"] == case_id)
        tac = (FIXTURES / str(case["tac"])).read_text(encoding="utf-8")
        report = lint(tac, product=str(case["product"]))
        assert report.ok, (case_id, [(i.code, i.message) for i in report.issues if i.severity == "error"])


def test_tcu_cloud_type_membership_via_speci_accept() -> None:
    tac = (FIXTURES / "accept/speci_r4_bkn_tcu.tac").read_text(encoding="utf-8")
    assert "TCU" in tac
    assert membership.is_member("cloud_type", "TCU")
    report = lint(tac, product="SPECI")
    assert "UNKNOWN_WMO_MEMBERSHIP" not in {i.code for i in report.issues}
    assert report.ok or not any(i.severity == "error" for i in report.issues)


def test_spacewx_composed_notations_from_accept_fixtures() -> None:
    """EFFECT + OBS severity → SpaceWxPhenomena register form (fixture baseline gap)."""
    membership.load_membership_sets.cache_clear()
    pairs = [
        ("accept/swxa_sx1_hf_com.tac", "HF_COM_SEV"),
        ("accept/swxa_sx1_gnss.tac", "GNSS_MOD"),
        ("accept/swxa_sx1_radiation.tac", "RADIATION_MOD"),
    ]
    for rel, notation in pairs:
        text = (FIXTURES / rel).read_text(encoding="utf-8")
        assert re.search(r"(?m)^\s*SWX\s+EFFECT\s*:", text)
        assert membership.is_member("spacewx_phenomena", notation)
        report = lint(text, product="SWXA")
        assert "UNKNOWN_WMO_MEMBERSHIP" not in {i.code for i in report.issues}


def test_negative_ev050_membership_codes() -> None:
    for case_id in (
        "metar_unknown_recent_weather",
        "airmet_unknown_phenomenon_underscore",
        "swxa_unknown_effect",
    ):
        case = next(c for c in MANIFEST["negative"] if c["id"] == case_id)
        tac = (FIXTURES / str(case["tac"])).read_text(encoding="utf-8")
        report = lint(tac, product=str(case["product"]))
        codes = {i.code for i in report.issues if i.severity == "error"}
        assert "UNKNOWN_WMO_MEMBERSHIP" in codes, (case_id, codes)

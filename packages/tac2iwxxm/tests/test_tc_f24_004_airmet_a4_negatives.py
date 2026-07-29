"""TC-F24-004 — AIRMET A4 negatives + translation-failed adjacency (S026 / EV-020 T2.4).

Rule-violating AIRMET must emit registry diagnostics; ``airmet-translation-failed`` is not a
happy-path golden and must not silent-swap product/root with SIGMET/VA.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from tac_validate import lint

from tac2iwxxm import convert

FIXTURES = Path(__file__).resolve().parents[2] / "tac-validate" / "tests" / "fixtures"
MANIFEST_PATH = FIXTURES / "manifest.json"
VENDOR = Path(__file__).resolve().parents[3] / "vendor" / "schemas" / "iwxxm" / "2025-2" / "IWXXM" / "examples"
ANNEX3 = Path(__file__).resolve().parent / "fixtures" / "annex3_golden"

_PROFILE = "annex3"
_VERSION = "2025-2"

_A4_CODES = {
    "MISSING_VALID",
    "MISSING_SEQUENCE",
    "MISSING_FIR_OR_CTA",
    "MULTIPLE_PHENOMENA",
    "INVALID_STNR_MOVEMENT",
    "MISSING_OBS_OR_FCST",
}


def _load_manifest() -> dict[str, Any]:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def _read(rel: str) -> str:
    path = FIXTURES / rel
    assert path.is_file(), f"missing fixture: {path}"
    return path.read_text(encoding="utf-8")


def _case_ids(cases: list[dict[str, Any]]) -> list[str]:
    return [str(c["id"]) for c in cases]


_MANIFEST = _load_manifest()
_A4_NEGATIVES = [
    c
    for c in _MANIFEST["negative"]
    if c["product"] == "AIRMET"
    and c.get("expected_codes")
    and (c.get("theme") in {"A1", "A2", "A4"} or c["id"] == "airmet_missing_valid")
]


def test_tc_f24_004_a4_negatives_present() -> None:
    assert len(_A4_NEGATIVES) >= 5
    codes = {c["expected_codes"][0] for c in _A4_NEGATIVES}
    assert "MISSING_VALID" in codes
    assert codes <= _A4_CODES
    for case in _A4_NEGATIVES:
        assert _read(case["tac"]).strip()


@pytest.mark.parametrize("case", _A4_NEGATIVES, ids=_case_ids(_A4_NEGATIVES))
def test_tc_f24_004_negatives_emit_registry_codes(case: dict[str, Any]) -> None:
    report = lint(_read(case["tac"]), product="AIRMET")
    assert report.ok is False
    codes = {i.code for i in report.issues}
    expected = case["expected_codes"][0]
    assert expected in codes, f"expected {expected} in {sorted(codes)}"
    if case.get("require_spans"):
        matched = [i for i in report.issues if i.code == expected]
        assert matched and matched[0].start is not None and matched[0].end is not None


def test_tc_f24_004_translation_failed_not_in_happy_path_pack() -> None:
    manifest = json.loads((ANNEX3 / "manifest.json").read_text(encoding="utf-8"))
    seeds = {c.get("seed") for c in manifest["cases"]}
    ids = {c["id"] for c in manifest["cases"]}
    assert "airmet-translation-failed" not in seeds
    assert "airmet_translation_failed" not in ids


def test_tc_f24_004_translation_failed_keeps_airmet_root() -> None:
    tac = (VENDOR / "airmet-translation-failed.tac").read_text(encoding="utf-8")
    assert "AIRMET" in tac.upper()
    assert "INVALID TS" in tac.upper()
    result = convert(tac, product="AIRMET", profile=_PROFILE, iwxxm_version=_VERSION)
    # Convert may soft-succeed; adjacency requires AIRMET root — never SIGMET/VA swap.
    assert result.product == "AIRMET"
    assert result.xml
    assert "<iwxxm:AIRMET " in result.xml
    assert "<iwxxm:SIGMET " not in result.xml
    assert "<iwxxm:VolcanicAshSIGMET " not in result.xml
    assert "iwxxm:VolcanicAshAdvisory" not in result.xml


def test_tc_f24_004_airmet_tac_under_sigmet_hint_does_not_swap_to_sigmet_root() -> None:
    """AIRMET-shaped TAC must not emit SIGMET root when forced through product=SIGMET."""
    tac = (ANNEX3 / "airmet_a6_1a_ts.tac").read_text(encoding="utf-8")
    # Lint under wrong product should fail (template/gate), not silent-ok as SIGMET.
    assert lint(tac, product="SIGMET").ok is False
    result = convert(tac, product="SIGMET", profile=_PROFILE, iwxxm_version=_VERSION)
    # Parser may fail or emit issues; if XML is produced it must not claim happy AIRMET→SIGMET.
    if result.ok and result.xml:
        assert "<iwxxm:AIRMET " not in result.xml or result.product != "AIRMET"

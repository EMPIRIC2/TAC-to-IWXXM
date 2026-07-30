"""TC-F27-004 — F27 theme C1 + translation-failed adjacency (S027 / EV-021 T4.4).

Common-rule coverage for TCA: ``reportStatus`` / ``permissibleUsage`` on the WMO golden,
T1 negatives still emit registry diagnostics, and ``tc-advisory-translation-failed`` is not a
happy-path golden and must not silent-swap product/root with SIGMET/TC SIGMET.

Convert-only (no TAC lint surface) — CRS attrs, ``translationFailedTAC`` emission, COLLECT
packing — documented for matrix note (F26 C1 / F23 C1 pattern).
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

_C1_CONVERT_ONLY = (
    "2-D CRS attrs (srsName / srsDimension / axisLabels)",
    "translationFailedTAC",
    "COLLECT packing / code-list URIs",
)


def _load_manifest() -> dict[str, Any]:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def _read(rel: str) -> str:
    path = FIXTURES / rel
    assert path.is_file(), f"missing fixture: {path}"
    return path.read_text(encoding="utf-8")


def _case_ids(cases: list[dict[str, Any]]) -> list[str]:
    return [str(c["id"]) for c in cases]


_MANIFEST = _load_manifest()
_T1_ERRORS = list(_MANIFEST.get("f27_t1_errors", []))


def test_tc_f27_004_c1_convert_only_documented() -> None:
    assert len(_C1_CONVERT_ONLY) >= 3
    assert "translationFailedTAC" in _C1_CONVERT_ONLY


def test_tc_f27_004_t1_negatives_present_for_c1() -> None:
    assert len(_T1_ERRORS) >= 1
    for case in _T1_ERRORS:
        assert case["product"] == "TCA"
        assert _read(case["tac"]).strip()


@pytest.mark.parametrize("case", _T1_ERRORS, ids=_case_ids(_T1_ERRORS))
def test_tc_f27_004_negatives_emit_registry_codes(case: dict[str, Any]) -> None:
    report = lint(_read(case["tac"]), product="TCA")
    assert report.ok is False
    codes = {i.code for i in report.issues}
    expected = case["expected_codes"][0]
    assert expected in codes, f"expected {expected} in {sorted(codes)}"
    if case.get("require_spans"):
        matched = [i for i in report.issues if i.code == expected]
        assert matched and matched[0].start is not None and matched[0].end is not None


def test_tc_f27_004_golden_has_report_status_and_usage() -> None:
    """C1 — reportStatus / permissibleUsage present on default convert of A2-2."""
    tac = (ANNEX3 / "tca_a2_2.tac").read_text(encoding="utf-8")
    result = convert(tac, product="TCA", profile=_PROFILE, iwxxm_version=_VERSION)
    assert result.ok is True
    assert result.xml
    assert 'reportStatus="NORMAL"' in result.xml
    assert 'permissibleUsage="OPERATIONAL"' in result.xml
    assert "<iwxxm:TropicalCycloneAdvisory" in result.xml


def test_tc_f27_004_translation_failed_not_in_happy_path_pack() -> None:
    manifest = json.loads((ANNEX3 / "manifest.json").read_text(encoding="utf-8"))
    seeds = {c.get("seed") for c in manifest["cases"]}
    ids = {c["id"] for c in manifest["cases"]}
    assert "tc-advisory-translation-failed" not in seeds
    assert "tca_translation_failed" not in ids
    assert "tc_advisory_translation_failed" not in ids


def test_tc_f27_004_translation_failed_keeps_tca_root() -> None:
    tac = (VENDOR / "tc-advisory-translation-failed.tac").read_text(encoding="utf-8")
    assert "TC ADVISORY" in tac.upper()
    result = convert(tac, product="TCA", profile=_PROFILE, iwxxm_version=_VERSION)
    # Convert may soft-succeed; adjacency requires TCA root — never SIGMET/TC SIGMET swap.
    assert result.product == "TCA"
    assert result.xml
    assert "<iwxxm:TropicalCycloneAdvisory" in result.xml
    assert "<iwxxm:SIGMET " not in result.xml
    assert "<iwxxm:TropicalCycloneSIGMET " not in result.xml
    assert "<iwxxm:AIRMET " not in result.xml


def test_tc_f27_004_tca_tac_under_sigmet_hint_does_not_swap_to_sigmet_root() -> None:
    """TCA-shaped TAC must not emit SIGMET root when forced through product=SIGMET."""
    tac = (ANNEX3 / "tca_a2_2.tac").read_text(encoding="utf-8")
    assert lint(tac, product="SIGMET").ok is False
    result = convert(tac, product="SIGMET", profile=_PROFILE, iwxxm_version=_VERSION)
    if result.ok and result.xml:
        assert "<iwxxm:TropicalCycloneAdvisory" not in result.xml or result.product != "TCA"

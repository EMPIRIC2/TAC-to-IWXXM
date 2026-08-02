"""F20 / S1 — SPECI exceptional-rule deepen (TC-F20-004 / #734).

HARD theme S1 from taf-speci-research-catalog.md.
T3.1 fixtures; T3.2 encodes registry + METAR/SPECI S1 diagnostics.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from tac_validate import lint
from tac_validate.issue_registry import by_code

FIXTURES = Path(__file__).resolve().parent / "fixtures"
MANIFEST_PATH = FIXTURES / "manifest.json"

_INFO_CODES = {
    "NIL_REPORT",
    "CAVOK_PRESENT",
    "NSC_PRESENT",
    "NCD_PRESENT",
    "NOSIG_PRESENT",
    "NSW_PRESENT",
    "VV_NOT_OBSERVABLE",
    "WX_NOT_OBSERVABLE",
    "RVR_PRESENT",
    "WIND_DIR_VARIATION",
    "COR_PRESENT",
}


def _load_manifest() -> dict[str, Any]:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def _read_tac(rel: str) -> str:
    path = FIXTURES / rel
    assert path.is_file(), f"missing fixture: {path}"
    text = path.read_text(encoding="utf-8")
    assert text.strip(), f"empty fixture: {path}"
    return text


def _case_ids(cases: list[dict[str, Any]]) -> list[str]:
    return [str(c["id"]) for c in cases]


_MANIFEST = _load_manifest()
# Product filter required: F28 also uses theme ids that must not collide (SX1 for SWXA).
_S1_ACCEPT = [c for c in _MANIFEST["accept"] if c.get("theme") == "S1" and c.get("product") == "SPECI"]
_S1_INFO = list(_MANIFEST.get("s1_modifier_info", []))
_S1_ERRORS = list(_MANIFEST.get("s1_errors", []))


def test_s1_manifest_sections_present() -> None:
    assert len(_S1_ACCEPT) >= 11
    assert {c["product"] for c in _S1_ACCEPT} == {"SPECI"}
    assert len(_S1_INFO) >= 11
    assert len(_S1_ERRORS) >= 1
    for case in _S1_ACCEPT + _S1_INFO + _S1_ERRORS:
        assert (_read_tac(case["tac"])).strip()
    codes = {c["expected_codes"][0] for c in _S1_INFO}
    assert codes == _INFO_CODES
    for case in _S1_ERRORS:
        assert case["expected_codes"][0] == "INVALID_NIL"


@pytest.mark.parametrize("case", _S1_ACCEPT, ids=_case_ids(_S1_ACCEPT))
def test_s1_accept_ok(case: dict[str, Any]) -> None:
    report = lint(_read_tac(case["tac"]), product=case["product"])
    assert report.ok is True
    assert not any(i.severity == "error" for i in report.issues)


@pytest.mark.parametrize("case", _S1_INFO, ids=_case_ids(_S1_INFO))
def test_s1_modifier_emits_info(case: dict[str, Any]) -> None:
    code = case["expected_codes"][0]
    report = lint(_read_tac(case["tac"]), product=case["product"])
    assert report.ok is True
    matched = [i for i in report.issues if i.code == code]
    assert matched, f"expected info code {code}; got {[i.code for i in report.issues]}"
    assert all(i.severity == "info" for i in matched)
    assert by_code(code).severity == "info"
    if case.get("require_spans"):
        assert any(i.start is not None and i.end is not None and i.end > i.start for i in matched)


@pytest.mark.parametrize("case", _S1_ERRORS, ids=_case_ids(_S1_ERRORS))
def test_s1_invalid_emits_error(case: dict[str, Any]) -> None:
    code = case["expected_codes"][0]
    report = lint(_read_tac(case["tac"]), product=case["product"])
    assert report.ok is False
    codes = {i.code for i in report.issues if i.severity == "error"}
    assert code in codes
    assert by_code(code).severity == "error"
    if case.get("require_spans"):
        matched = [i for i in report.issues if i.code == code]
        assert any(i.start is not None and i.end is not None and i.end > i.start for i in matched)

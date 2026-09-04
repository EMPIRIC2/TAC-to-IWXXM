"""F26 theme V1 - VAA exceptional accept + negatives (TC-F26-001/004 / #736).

HARD theme from vaa-tca-theme-fixture-map.md. T1.1 fixtures; T1.2 registry/rules.
Always write "F26 theme V1" (not F23 VA-SIGMET V1) - D-S027-EV021-s02m1-1.
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
    "VAA_VOLCANO_UNKNOWN",
    "VAA_VOLCANO_UNNAMED",
    "VAA_RMK_NIL",
    "VAA_FCST_NO_VA_EXP",
    "VAA_NO_FURTHER_ADVISORIES",
}
_ERROR_CODES = {
    "MISSING_VOLCANO",
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
_V1_ACCEPT = [c for c in _MANIFEST["accept"] if c.get("theme") == "V1" and c.get("product") == "VAA"]
_V1_INFO = list(_MANIFEST.get("f26_v1_modifier_info", []))
_V1_ERRORS = list(_MANIFEST.get("f26_v1_errors", []))


def test_f26_v1_manifest_sections_present() -> None:
    assert len(_V1_ACCEPT) >= 3
    assert {c["product"] for c in _V1_ACCEPT} == {"VAA"}
    assert {c["id"] for c in _V1_ACCEPT} >= {
        "accept_vaa_v1_volcano_unknown",
        "accept_vaa_v1_volcano_unnamed",
        "accept_vaa_v1_rmk_nil_fcst_no_va",
        "accept_vaa_v1_no_further",
    }
    assert len(_V1_INFO) >= 5
    assert len(_V1_ERRORS) >= 1
    for case in _V1_ACCEPT + _V1_INFO + _V1_ERRORS:
        assert (_read_tac(case["tac"])).strip()
    codes = {c["expected_codes"][0] for c in _V1_INFO}
    assert codes == _INFO_CODES
    for case in _V1_ERRORS:
        assert case["expected_codes"][0] in _ERROR_CODES


@pytest.mark.parametrize("case", _V1_ACCEPT, ids=_case_ids(_V1_ACCEPT))
def test_f26_v1_accept_ok(case: dict[str, Any]) -> None:
    report = lint(_read_tac(case["tac"]), product=case["product"])
    assert report.ok is True
    assert not any(i.severity == "error" for i in report.issues)


@pytest.mark.parametrize("case", _V1_INFO, ids=_case_ids(_V1_INFO))
def test_f26_v1_modifier_emits_info(case: dict[str, Any]) -> None:
    code = case["expected_codes"][0]
    report = lint(_read_tac(case["tac"]), product=case["product"])
    assert report.ok is True
    matched = [i for i in report.issues if i.code == code]
    assert matched, f"expected info code {code}; got {[i.code for i in report.issues]}"
    assert all(i.severity == "info" for i in matched)
    assert by_code(code).severity == "info"
    if case.get("require_spans"):
        assert any(i.start is not None and i.end is not None and i.end > i.start for i in matched)


@pytest.mark.parametrize("case", _V1_ERRORS, ids=_case_ids(_V1_ERRORS))
def test_f26_v1_invalid_emits_error(case: dict[str, Any]) -> None:
    code = case["expected_codes"][0]
    report = lint(_read_tac(case["tac"]), product=case["product"])
    assert report.ok is False
    codes = {i.code for i in report.issues if i.severity == "error"}
    assert code in codes
    assert by_code(code).severity == "error"
    if case.get("require_spans"):
        matched = [i for i in report.issues if i.code == code]
        assert matched
        assert matched[0].start is not None
        assert matched[0].end is not None

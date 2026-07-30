"""F20 / T1 — TAF NIL / CNL / AMD / COR accept + negatives (TC-F20-004).

HARD theme T1 from taf-speci-research-catalog.md / #735 exceptional-rule table.
T1.1 fixtures + assertions; T1.2 encodes registry rows + rules.
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

_INFO_CODES = {"NIL_REPORT", "CNL_REPORT", "AMD_PRESENT", "COR_PRESENT"}
_ERROR_CODES = {"INVALID_NIL", "INVALID_CNL_SHAPE"}


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
_T1_ACCEPT = [c for c in _MANIFEST["accept"] if c.get("theme") == "T1" and c.get("product") == "TAF"]
_T1_INFO = list(_MANIFEST.get("t1_modifier_info", []))
_T1_ERRORS = list(_MANIFEST.get("t1_errors", []))


def test_t1_manifest_sections_present() -> None:
    assert len(_T1_ACCEPT) >= 4
    assert {c["product"] for c in _T1_ACCEPT} == {"TAF"}
    assert {c["id"] for c in _T1_ACCEPT} >= {
        "accept_taf_t1_nil",
        "accept_taf_t1_cnl",
        "accept_taf_t1_amd",
        "accept_taf_t1_cor",
    }
    assert len(_T1_INFO) >= 4
    assert len(_T1_ERRORS) >= 2
    for case in _T1_ACCEPT + _T1_INFO + _T1_ERRORS:
        assert (_read_tac(case["tac"])).strip()
    codes = {c["expected_codes"][0] for c in _T1_INFO}
    assert codes == _INFO_CODES
    for case in _T1_ERRORS:
        assert case["expected_codes"][0] in _ERROR_CODES


@pytest.mark.parametrize("case", _T1_ACCEPT, ids=_case_ids(_T1_ACCEPT))
def test_t1_accept_ok(case: dict[str, Any]) -> None:
    report = lint(_read_tac(case["tac"]), product=case["product"])
    assert report.ok is True
    assert not any(i.severity == "error" for i in report.issues)


@pytest.mark.parametrize("case", _T1_INFO, ids=_case_ids(_T1_INFO))
def test_t1_modifier_emits_info(case: dict[str, Any]) -> None:
    code = case["expected_codes"][0]
    report = lint(_read_tac(case["tac"]), product=case["product"])
    assert report.ok is True
    matched = [i for i in report.issues if i.code == code]
    assert matched, f"expected info code {code}; got {[i.code for i in report.issues]}"
    assert all(i.severity == "info" for i in matched)
    assert by_code(code).severity == "info"
    if case.get("require_spans"):
        assert any(i.start is not None and i.end is not None and i.end > i.start for i in matched)


@pytest.mark.parametrize("case", _T1_ERRORS, ids=_case_ids(_T1_ERRORS))
def test_t1_invalid_emits_error(case: dict[str, Any]) -> None:
    code = case["expected_codes"][0]
    report = lint(_read_tac(case["tac"]), product=case["product"])
    assert report.ok is False
    codes = {i.code for i in report.issues if i.severity == "error"}
    assert code in codes
    assert by_code(code).severity == "error"
    if case.get("require_spans"):
        matched = [i for i in report.issues if i.code == code]
        assert any(i.start is not None and i.end is not None and i.end > i.start for i in matched)

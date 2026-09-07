"""F20 / T2 - TAF FM/BECMG/TEMPO/PROB + TL/AT (TC-F20-004).

HARD theme T2 from taf-speci-research-catalog.md / #735.
T1.3 fixtures; T1.4 encodes registry + rules.
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
    "FM_PRESENT",
    "BECMG_PRESENT",
    "TEMPO_PRESENT",
    "PROB_PRESENT",
    "TL_PRESENT",
    "AT_PRESENT",
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
_T2_ACCEPT = [c for c in _MANIFEST["accept"] if c.get("theme") == "T2"]
_T2_INFO = list(_MANIFEST.get("t2_modifier_info", []))
_T2_ERRORS = list(_MANIFEST.get("t2_errors", []))


def test_t2_manifest_sections_present() -> None:
    assert len(_T2_ACCEPT) >= 6
    assert {c["product"] for c in _T2_ACCEPT} == {"TAF"}
    assert len(_T2_INFO) >= 6
    assert len(_T2_ERRORS) >= 3
    for case in _T2_ACCEPT + _T2_INFO + _T2_ERRORS:
        assert (_read_tac(case["tac"])).strip()
    codes = {c["expected_codes"][0] for c in _T2_INFO}
    assert codes == _INFO_CODES
    for case in _T2_ERRORS:
        assert case["expected_codes"] == ["INVALID_PROB"]


@pytest.mark.parametrize("case", _T2_ACCEPT, ids=_case_ids(_T2_ACCEPT))
def test_t2_accept_ok(case: dict[str, Any]) -> None:
    report = lint(_read_tac(case["tac"]), product=case["product"])
    assert report.ok is True
    assert not any(i.severity == "error" for i in report.issues)


@pytest.mark.parametrize("case", _T2_INFO, ids=_case_ids(_T2_INFO))
def test_t2_modifier_emits_info(case: dict[str, Any]) -> None:
    code = case["expected_codes"][0]
    report = lint(_read_tac(case["tac"]), product=case["product"])
    assert report.ok is True
    matched = [i for i in report.issues if i.code == code]
    assert matched, f"expected info code {code}; got {[i.code for i in report.issues]}"
    assert all(i.severity == "info" for i in matched)
    assert by_code(code).severity == "info"
    if case.get("require_spans"):
        assert any(i.start is not None and i.end is not None and i.end > i.start for i in matched)


@pytest.mark.parametrize("case", _T2_ERRORS, ids=_case_ids(_T2_ERRORS))
def test_t2_invalid_prob_emits_error(case: dict[str, Any]) -> None:
    code = case["expected_codes"][0]
    report = lint(_read_tac(case["tac"]), product=case["product"])
    assert report.ok is False
    codes = {i.code for i in report.issues if i.severity == "error"}
    assert code in codes
    assert by_code(code).severity == "error"
    if case.get("require_spans"):
        matched = [i for i in report.issues if i.code == code]
        assert any(i.start is not None and i.end is not None and i.end > i.start for i in matched)

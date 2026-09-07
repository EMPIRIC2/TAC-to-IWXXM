"""F20 / T3 - TAF TX/TN, CAVOK, NSC, NSW, VV/// (TC-F20-004).

HARD theme T3 from taf-speci-research-catalog.md / #735.
T1.5 fixtures; T1.6 encodes registry + rules.
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
    "TX_TN_PRESENT",
    "CAVOK_PRESENT",
    "NSC_PRESENT",
    "NSW_PRESENT",
    "VV_OMIT",
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
_T3_ACCEPT = [c for c in _MANIFEST["accept"] if c.get("theme") == "T3"]
_T3_INFO = list(_MANIFEST.get("t3_modifier_info", []))
_T3_ERRORS = list(_MANIFEST.get("t3_errors", []))


def test_t3_manifest_sections_present() -> None:
    assert len(_T3_ACCEPT) >= 5
    assert {c["product"] for c in _T3_ACCEPT} == {"TAF"}
    assert len(_T3_INFO) >= 5
    assert len(_T3_ERRORS) >= 1
    for case in _T3_ACCEPT + _T3_INFO + _T3_ERRORS:
        assert (_read_tac(case["tac"])).strip()
    codes = {c["expected_codes"][0] for c in _T3_INFO}
    assert codes == _INFO_CODES
    assert _T3_ERRORS[0]["expected_codes"] == ["INVALID_TX_TN"]


@pytest.mark.parametrize("case", _T3_ACCEPT, ids=_case_ids(_T3_ACCEPT))
def test_t3_accept_ok(case: dict[str, Any]) -> None:
    report = lint(_read_tac(case["tac"]), product=case["product"])
    assert report.ok is True
    assert not any(i.severity == "error" for i in report.issues)


@pytest.mark.parametrize("case", _T3_INFO, ids=_case_ids(_T3_INFO))
def test_t3_modifier_emits_info(case: dict[str, Any]) -> None:
    code = case["expected_codes"][0]
    report = lint(_read_tac(case["tac"]), product=case["product"])
    assert report.ok is True
    matched = [i for i in report.issues if i.code == code]
    assert matched, f"expected info code {code}; got {[i.code for i in report.issues]}"
    assert all(i.severity == "info" for i in matched)
    assert by_code(code).severity == "info"
    if case.get("require_spans"):
        assert any(i.start is not None and i.end is not None and i.end > i.start for i in matched)


@pytest.mark.parametrize("case", _T3_ERRORS, ids=_case_ids(_T3_ERRORS))
def test_t3_invalid_tx_tn_emits_error(case: dict[str, Any]) -> None:
    code = case["expected_codes"][0]
    report = lint(_read_tac(case["tac"]), product=case["product"])
    assert report.ok is False
    codes = {i.code for i in report.issues if i.severity == "error"}
    assert code in codes
    assert by_code(code).severity == "error"
    if case.get("require_spans"):
        matched = [i for i in report.issues if i.code == code]
        assert any(i.start is not None and i.end is not None and i.end > i.start for i in matched)

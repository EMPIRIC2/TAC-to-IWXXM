"""F23 / V1 — VA SIGMET accept + negatives (TC-F23-004 / #739).

HARD theme V1 from sigmet-research-catalog.md. T3.1 fixtures + T3.2 registry/rules.
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
    "VA_VOLCANO_IDENTITY",
    "VA_ASH_GEOMETRY",
    "NO_VA_EXP",
    "VA_CNL_FIR_MOVED",
}
_ERROR_CODES = {
    "MISSING_VA_VOLCANO",
    "INVALID_NO_VA_EXP",
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
# Product filter required: F26 also uses theme id V1 for VAA (D-S027-EV021-s02m1-1).
_V1_ACCEPT = [c for c in _MANIFEST["accept"] if c.get("theme") == "V1" and c.get("product") == "SIGMET"]
_V1_INFO = list(_MANIFEST.get("v1_modifier_info", []))
_V1_ERRORS = list(_MANIFEST.get("v1_errors", []))


def test_v1_manifest_sections_present() -> None:
    assert len(_V1_ACCEPT) >= 3
    assert {c["product"] for c in _V1_ACCEPT} == {"SIGMET"}
    assert {c["id"] for c in _V1_ACCEPT} >= {
        "accept_sigmet_v1_va_volcano",
        "accept_sigmet_v1_no_va_exp",
        "accept_sigmet_v1_cnl_fir_moved",
    }
    assert len(_V1_INFO) >= 4
    assert len(_V1_ERRORS) >= 2
    for case in _V1_ACCEPT + _V1_INFO + _V1_ERRORS:
        assert (_read_tac(case["tac"])).strip()
    codes = {c["expected_codes"][0] for c in _V1_INFO}
    assert codes == _INFO_CODES
    for case in _V1_ERRORS:
        assert case["expected_codes"][0] in _ERROR_CODES


@pytest.mark.parametrize("case", _V1_ACCEPT, ids=_case_ids(_V1_ACCEPT))
def test_v1_accept_ok(case: dict[str, Any]) -> None:
    report = lint(_read_tac(case["tac"]), product=case["product"])
    assert report.ok is True
    assert not any(i.severity == "error" for i in report.issues)


@pytest.mark.parametrize("case", _V1_INFO, ids=_case_ids(_V1_INFO))
def test_v1_modifier_emits_info(case: dict[str, Any]) -> None:
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
def test_v1_invalid_emits_error(case: dict[str, Any]) -> None:
    code = case["expected_codes"][0]
    report = lint(_read_tac(case["tac"]), product=case["product"])
    assert report.ok is False
    codes = {i.code for i in report.issues if i.severity == "error"}
    assert code in codes
    assert by_code(code).severity == "error"
    if case.get("require_spans"):
        matched = [i for i in report.issues if i.code == code]
        assert any(i.start is not None and i.end is not None and i.end > i.start for i in matched)

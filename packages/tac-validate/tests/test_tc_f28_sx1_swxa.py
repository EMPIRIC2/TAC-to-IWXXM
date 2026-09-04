"""F28 theme SX1 - SWXA exceptional accept + negatives (TC-F28-001/004 / #740).

HARD theme for Space Weather Advisory. T11.1 fixtures; T11.2 registry/rules.
Theme id **SX1** (not SPECI S1) - D-S036-F28-sx1.
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
    "SWXA_RMK_NIL",
    "SWXA_FCST_NO_SWX_EXP",
    "SWXA_NO_FURTHER_ADVISORIES",
}
_ERROR_CODES = {
    "MISSING_SWXC",
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
_SX1_ACCEPT = [c for c in _MANIFEST["accept"] if c.get("theme") == "SX1" and c.get("product") == "SWXA"]
_SX1_INFO = list(_MANIFEST.get("f28_sx1_modifier_info", []))
_SX1_ERRORS = list(_MANIFEST.get("f28_sx1_errors", []))


def test_f28_sx1_manifest_sections_present() -> None:
    assert len(_SX1_ACCEPT) >= 3
    assert {c["product"] for c in _SX1_ACCEPT} == {"SWXA"}
    assert {c["id"] for c in _SX1_ACCEPT} >= {
        "accept_swxa_sx1_hf_com",
        "accept_swxa_sx1_gnss",
        "accept_swxa_sx1_radiation",
        "accept_swxa_sx1_rmk_nil",
        "accept_swxa_sx1_no_further",
    }
    assert len(_SX1_INFO) >= 3
    assert len(_SX1_ERRORS) >= 1
    for case in _SX1_ACCEPT + _SX1_INFO + _SX1_ERRORS:
        assert (_read_tac(case["tac"])).strip()
    codes = {c["expected_codes"][0] for c in _SX1_INFO}
    assert codes == _INFO_CODES
    for case in _SX1_ERRORS:
        assert case["expected_codes"][0] in _ERROR_CODES


@pytest.mark.parametrize("case", _SX1_ACCEPT, ids=_case_ids(_SX1_ACCEPT))
def test_f28_sx1_accept_ok(case: dict[str, Any]) -> None:
    report = lint(_read_tac(case["tac"]), product=case["product"])
    assert report.ok is True
    assert not any(i.severity == "error" for i in report.issues)


@pytest.mark.parametrize("case", _SX1_INFO, ids=_case_ids(_SX1_INFO))
def test_f28_sx1_modifier_emits_info(case: dict[str, Any]) -> None:
    code = case["expected_codes"][0]
    report = lint(_read_tac(case["tac"]), product=case["product"])
    assert report.ok is True
    matched = [i for i in report.issues if i.code == code]
    assert matched, f"expected info code {code}; got {[i.code for i in report.issues]}"
    assert all(i.severity == "info" for i in matched)
    assert by_code(code).severity == "info"
    if case.get("require_spans"):
        assert any(i.start is not None and i.end is not None and i.end > i.start for i in matched)


@pytest.mark.parametrize("case", _SX1_ERRORS, ids=_case_ids(_SX1_ERRORS))
def test_f28_sx1_invalid_emits_error(case: dict[str, Any]) -> None:
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

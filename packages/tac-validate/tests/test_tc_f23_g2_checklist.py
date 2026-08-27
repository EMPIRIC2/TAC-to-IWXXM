"""F23 / G2 - general SIGMET sequence/validity/FIR/OBS/intensity (TC-F23-004).

HARD theme G2 from sigmet-research-catalog.md / #733 checklist.
T1.3 fixtures + assertions; T1.4 encodes registry rows + rules.
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
    "SIGMET_SEQUENCE",
    "FIR_OR_CTA",
    "OBS_OR_FCST",
    "INTENSITY_CHANGE",
}
_ERROR_CODES = {
    "MISSING_SEQUENCE",
    "INVALID_VALIDITY_DURATION",
    "MISSING_FIR_OR_CTA",
    "MISSING_OBS_OR_FCST",
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
_G2_ACCEPT = [c for c in _MANIFEST["accept"] if c.get("theme") == "G2"]
_G2_INFO = list(_MANIFEST.get("g2_modifier_info", []))
_G2_ERRORS = list(_MANIFEST.get("g2_errors", []))


def test_g2_manifest_sections_present() -> None:
    assert len(_G2_ACCEPT) >= 4
    assert {c["product"] for c in _G2_ACCEPT} == {"SIGMET"}
    assert {c["id"] for c in _G2_ACCEPT} >= {
        "accept_sigmet_g2_sequence",
        "accept_sigmet_g2_fir",
        "accept_sigmet_g2_obs",
        "accept_sigmet_g2_intensity",
    }
    assert len(_G2_INFO) >= 4
    assert len(_G2_ERRORS) >= 4
    for case in _G2_ACCEPT + _G2_INFO + _G2_ERRORS:
        assert (_read_tac(case["tac"])).strip()
    codes = {c["expected_codes"][0] for c in _G2_INFO}
    assert codes == _INFO_CODES
    for case in _G2_ERRORS:
        assert case["expected_codes"][0] in _ERROR_CODES


@pytest.mark.parametrize("case", _G2_ACCEPT, ids=_case_ids(_G2_ACCEPT))
def test_g2_accept_ok(case: dict[str, Any]) -> None:
    report = lint(_read_tac(case["tac"]), product=case["product"])
    assert report.ok is True
    assert not any(i.severity == "error" for i in report.issues)


@pytest.mark.parametrize("case", _G2_INFO, ids=_case_ids(_G2_INFO))
def test_g2_modifier_emits_info(case: dict[str, Any]) -> None:
    code = case["expected_codes"][0]
    report = lint(_read_tac(case["tac"]), product=case["product"])
    assert report.ok is True
    matched = [i for i in report.issues if i.code == code]
    assert matched, f"expected info code {code}; got {[i.code for i in report.issues]}"
    assert all(i.severity == "info" for i in matched)
    assert by_code(code).severity == "info"
    if case.get("require_spans"):
        assert any(i.start is not None and i.end is not None and i.end > i.start for i in matched)


@pytest.mark.parametrize("case", _G2_ERRORS, ids=_case_ids(_G2_ERRORS))
def test_g2_invalid_emits_error(case: dict[str, Any]) -> None:
    code = case["expected_codes"][0]
    report = lint(_read_tac(case["tac"]), product=case["product"])
    assert report.ok is False
    codes = {i.code for i in report.issues if i.severity == "error"}
    assert code in codes
    assert by_code(code).severity == "error"
    if case.get("require_spans"):
        matched = [i for i in report.issues if i.code == code]
        assert any(i.start is not None and i.end is not None and i.end > i.start for i in matched)

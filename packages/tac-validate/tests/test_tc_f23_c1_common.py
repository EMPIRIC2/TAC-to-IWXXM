"""F23 / C1 - common rules for SIGMET + VA (TC-F23-004 / matrix C1).

HARD theme C1 from sigmet-research-catalog.md (#733/#739 common table).
T4.3 seeded fixtures; T4.4 encodes MULTI_REPORT_BULLETIN for SIGMET, tags
reportStatus/nil/COR codes with ``c1``, and asserts. CRS / translationFailedTAC /
COLLECT packing remain convert-only (matrix note - F20 C1 pattern).
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
    "SIGMET_CNL",
    "STNR_MOVEMENT",
    "MULTI_REPORT_BULLETIN",
    "NO_VA_EXP",
    "VA_CNL_FIR_MOVED",
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
_C1_ACCEPT = [c for c in _MANIFEST["accept"] if c.get("theme") == "C1" and c.get("product") == "SIGMET"]
_C1_INFO = list(_MANIFEST.get("f23_c1_modifier_info", []))
_C1_ERRORS = list(_MANIFEST.get("f23_c1_errors", []))

# Convert-only (no TAC lint surface) - documented for matrix deferral.
_C1_CONVERT_ONLY = (
    "2-D CRS attrs (srsName / srsDimension / axisLabels)",
    "translationFailedTAC",
    "COLLECT packing / code-list URIs",
)


def test_f23_c1_manifest_sections_present() -> None:
    assert len(_C1_ACCEPT) >= 7
    assert {c["product"] for c in _C1_ACCEPT} == {"SIGMET"}
    assert len(_C1_INFO) >= 5
    assert len(_C1_ERRORS) >= 1
    for case in _C1_ACCEPT + _C1_INFO + _C1_ERRORS:
        assert (_read_tac(case["tac"])).strip()
    codes = {c["expected_codes"][0] for c in _C1_INFO}
    assert codes == _INFO_CODES
    for case in _C1_ERRORS:
        assert case["expected_codes"][0] == "INVALID_SIGMET_COR"
    assert by_code("MULTI_REPORT_BULLETIN").severity == "info"
    assert "c1" in by_code("MULTI_REPORT_BULLETIN").tags
    assert "sigmet" in by_code("MULTI_REPORT_BULLETIN").tags
    for code in _INFO_CODES - {"MULTI_REPORT_BULLETIN"}:
        assert "c1" in by_code(code).tags
    assert "c1" in by_code("INVALID_SIGMET_COR").tags
    assert len(_C1_CONVERT_ONLY) >= 3


@pytest.mark.parametrize("case", _C1_ACCEPT, ids=_case_ids(_C1_ACCEPT))
def test_f23_c1_accept_ok(case: dict[str, Any]) -> None:
    report = lint(_read_tac(case["tac"]), product=case["product"])
    assert report.ok is True
    assert not any(i.severity == "error" for i in report.issues)


@pytest.mark.parametrize("case", _C1_INFO, ids=_case_ids(_C1_INFO))
def test_f23_c1_modifier_emits_info(case: dict[str, Any]) -> None:
    code = case["expected_codes"][0]
    report = lint(_read_tac(case["tac"]), product=case["product"])
    assert report.ok is True
    matched = [i for i in report.issues if i.code == code]
    assert matched, f"expected info code {code}; got {[i.code for i in report.issues]}"
    assert all(i.severity == "info" for i in matched)
    assert by_code(code).severity == "info"
    if case.get("require_spans"):
        assert any(i.start is not None and i.end is not None and i.end > i.start for i in matched)


@pytest.mark.parametrize("case", _C1_ERRORS, ids=_case_ids(_C1_ERRORS))
def test_f23_c1_invalid_emits_error(case: dict[str, Any]) -> None:
    code = case["expected_codes"][0]
    report = lint(_read_tac(case["tac"]), product=case["product"])
    assert report.ok is False
    codes = {i.code for i in report.issues if i.severity == "error"}
    assert code in codes
    assert by_code(code).severity == "error"
    if case.get("require_spans"):
        matched = [i for i in report.issues if i.code == code]
        assert any(i.start is not None and i.end is not None and i.end > i.start for i in matched)

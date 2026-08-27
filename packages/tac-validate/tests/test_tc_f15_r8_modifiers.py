"""Research R8 / E11-28 - AUTO/COR/NIL/NOSIG/TEMPO/RVR/VRB·gust (T3.11/T3.12).

HARD pack: each theme has accept coverage; modifiers emit info codes; malformed
NIL/RVR/wind emit errors.
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
_R8_ACCEPT = [c for c in _MANIFEST["accept"] if c.get("theme") == "R8"]
_R8_ACCEPT_NIL = [c for c in _R8_ACCEPT if c["id"] == "accept_metar_r8_nil"]
_R8_ACCEPT_OTHER = [c for c in _R8_ACCEPT if c["id"] != "accept_metar_r8_nil"]
_R8_INFO = list(_MANIFEST.get("r8_modifier_info", []))
_R8_ERRORS = list(_MANIFEST.get("r8_errors", []))

_INFO_CODES = {
    "AUTO_PRESENT",
    "COR_PRESENT",
    "NIL_REPORT",
    "NOSIG_PRESENT",
    "TEMPO_PRESENT",
    "RVR_PRESENT",
    "WIND_VRB_OR_GUST",
}


def test_r8_manifest_sections_present() -> None:
    assert len(_R8_ACCEPT) >= 8
    assert {c["product"] for c in _R8_ACCEPT} == {"METAR", "SPECI"}
    assert len(_R8_ACCEPT_NIL) >= 1
    assert len(_R8_INFO) >= 7
    assert len(_R8_ERRORS) >= 4
    for case in _R8_ACCEPT + _R8_INFO + _R8_ERRORS:
        assert (_read_tac(case["tac"])).strip()
    codes = {c["expected_codes"][0] for c in _R8_INFO}
    assert codes == _INFO_CODES
    for case in _R8_ERRORS:
        assert case["expected_codes"][0] in {"INVALID_NIL", "INVALID_RVR", "INVALID_WIND"}


@pytest.mark.parametrize("case", _R8_ACCEPT_OTHER, ids=_case_ids(_R8_ACCEPT_OTHER))
def test_r8_accept_modifiers_ok(case: dict[str, Any]) -> None:
    report = lint(_read_tac(case["tac"]), product=case["product"])
    assert report.ok is True


@pytest.mark.parametrize("case", _R8_ACCEPT_NIL, ids=_case_ids(_R8_ACCEPT_NIL))
def test_r8_accept_nil_ok(case: dict[str, Any]) -> None:
    report = lint(_read_tac(case["tac"]), product=case["product"])
    assert report.ok is True
    assert not any(i.severity == "error" for i in report.issues)


@pytest.mark.parametrize("case", _R8_INFO, ids=_case_ids(_R8_INFO))
def test_r8_modifier_emits_info(case: dict[str, Any]) -> None:
    code = case["expected_codes"][0]
    report = lint(_read_tac(case["tac"]), product=case["product"])
    assert report.ok is True
    matched = [i for i in report.issues if i.code == code]
    assert matched
    assert all(i.severity == "info" for i in matched)
    assert by_code(code).severity == "info"
    if case.get("require_spans"):
        assert any(i.start is not None and i.end is not None and i.end > i.start for i in matched)


@pytest.mark.parametrize("case", _R8_ERRORS, ids=_case_ids(_R8_ERRORS))
def test_r8_invalid_modifier_emits_error(case: dict[str, Any]) -> None:
    code = case["expected_codes"][0]
    report = lint(_read_tac(case["tac"]), product=case["product"])
    assert report.ok is False
    codes = {i.code for i in report.issues if i.severity == "error"}
    assert code in codes
    assert by_code(code).severity == "error"
    if case.get("require_spans"):
        matched = [i for i in report.issues if i.code == code]
        assert any(i.start is not None and i.end is not None and i.end > i.start for i in matched)

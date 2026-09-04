"""F24 / A1 - AIRMET header / sequence / FIR (TC-F24-001/004).

HARD theme A1 from wmo-quality-research-catalog.md / #731.
T1.1 fixtures + assertions; T1.2 encodes rules (reuse MISSING_SEQUENCE / MISSING_FIR_OR_CTA).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from tac_validate import lint

FIXTURES = Path(__file__).resolve().parent / "fixtures"
MANIFEST_PATH = FIXTURES / "manifest.json"

_ERROR_CODES = {"MISSING_SEQUENCE", "MISSING_FIR_OR_CTA"}


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
_A1_ACCEPT = [c for c in _MANIFEST["accept"] if c.get("theme") == "A1" and c["product"] == "AIRMET"]
_A1_ERRORS = [
    c for c in _MANIFEST["negative"] if c.get("theme") == "A1" and c["product"] == "AIRMET" and c.get("expected_codes")
]


def test_a1_manifest_sections_present() -> None:
    assert len(_A1_ACCEPT) >= 1
    assert {c["id"] for c in _A1_ACCEPT} >= {"accept_airmet_basic"}
    assert len(_A1_ERRORS) >= 2
    assert {c["expected_codes"][0] for c in _A1_ERRORS} == _ERROR_CODES
    for case in _A1_ACCEPT + _A1_ERRORS:
        assert (_read_tac(case["tac"])).strip()


@pytest.mark.parametrize("case", _A1_ACCEPT, ids=_case_ids(_A1_ACCEPT))
def test_a1_accept_ok(case: dict[str, Any]) -> None:
    report = lint(_read_tac(case["tac"]), product=case["product"])
    assert report.ok is True
    assert not any(i.severity == "error" for i in report.issues)


@pytest.mark.parametrize("case", _A1_ERRORS, ids=_case_ids(_A1_ERRORS))
def test_a1_error_codes(case: dict[str, Any]) -> None:
    report = lint(_read_tac(case["tac"]), product=case["product"])
    codes = {i.code for i in report.issues}
    expected = case["expected_codes"][0]
    assert expected in codes, f"expected {expected} in {sorted(codes)}"
    if case.get("require_spans"):
        matched = [i for i in report.issues if i.code == expected]
        assert matched
        assert matched[0].start is not None
        assert matched[0].end is not None

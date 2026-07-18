"""TC-F12-001 template+gate coverage for SIGMET/AIRMET/VAA/TCA (T2.1)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from tac_validate import lint

FIXTURES = Path(__file__).resolve().parent / "fixtures"
MANIFEST_PATH = FIXTURES / "manifest.json"
_T22_REASON = "T2.2: encode template+gate product rules"


def _template_cases() -> list[dict[str, Any]]:
    data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return [c for c in data["negative"] if c["depth"] == "template_gate"]


def _ids(cases: list[dict[str, Any]]) -> list[str]:
    return [str(c["id"]) for c in cases]


def test_template_gate_manifest_cites_a6_or_a2() -> None:
    for case in _template_cases():
        cite = str(case.get("cite", ""))
        assert "A6" in cite or "A2" in cite, case["id"]


@pytest.mark.xfail(strict=True, reason=_T22_REASON)
@pytest.mark.parametrize("case", _template_cases(), ids=_ids(_template_cases()))
def test_template_gate_diagnostics_are_actionable(case: dict[str, Any]) -> None:
    tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8")
    report = lint(tac, product=case["product"])
    assert report.ok is False
    errors = [i for i in report.issues if i.severity == "error"]
    assert errors
    for code in case["expected_codes"]:
        hit = next(i for i in errors if i.code == code)
        assert hit.message
        assert hit.start is not None and hit.end is not None
        assert hit.end > hit.start

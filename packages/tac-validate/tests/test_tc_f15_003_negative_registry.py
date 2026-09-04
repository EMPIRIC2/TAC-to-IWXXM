"""TC-F15-003 / T2.3 - negative fixture ``expected_codes`` ⊆ registry."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from tac_validate.issue_registry import by_code

FIXTURES = Path(__file__).resolve().parent / "fixtures"
MANIFEST_PATH = FIXTURES / "manifest.json"


def _negative_cases() -> list[dict[str, Any]]:
    return list(json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))["negative"])


@pytest.mark.parametrize("case", _negative_cases(), ids=[c["id"] for c in _negative_cases()])
def test_negative_expected_codes_subset_of_registry(case: dict[str, Any]) -> None:
    for code in case["expected_codes"]:
        by_code(code)  # KeyError if unregistered

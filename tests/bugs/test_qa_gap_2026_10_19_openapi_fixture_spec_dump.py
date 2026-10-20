"""Regression test: OpenAPI contract fixture names covering tests.

Fails while the fixture source is the OpenAPI document, or while any
interaction lacks ``covered_by`` pointing at an existing test file that
contains that operation path. Passes when every interaction names such a
test, even if the field lists match the spec. [Corpus: tests] [Corpus: api]
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests" / "contracts" / "openapi-interactions.json"
GENERATOR_SOURCE = "apps/frontend/openapi/openapi.json"


def _covering_file(covered_by: object) -> Path | None:
    if not isinstance(covered_by, str) or not covered_by.strip():
        return None
    relative = covered_by.split("::", 1)[0]
    path = ROOT / relative
    if path.is_file():
        return path
    return None


def test_openapi_contract_fixture_names_covering_tests() -> None:
    """Each fixture interaction names a test file that contains its path."""
    assert FIXTURE.is_file(), f"missing contract fixture: {FIXTURE}"
    payload: object = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert isinstance(payload, dict), "contract fixture is not an object"
    problems: list[str] = []
    if payload.get("source") == GENERATOR_SOURCE:
        problems.append("fixture source is the OpenAPI document")
    interactions = payload.get("interactions")
    if not isinstance(interactions, list) or not interactions:
        problems.append("fixture has no interactions")
    else:
        unnamed = 0
        for item in interactions:
            if not isinstance(item, dict):
                unnamed += 1
                continue
            path = _covering_file(item.get("covered_by"))
            operation = item.get("path")
            if path is None or not isinstance(operation, str):
                unnamed += 1
                continue
            if operation not in path.read_text(encoding="utf-8"):
                unnamed += 1
        if unnamed:
            problems.append(
                f"{unnamed} of {len(interactions)} interactions do not name an existing "
                "test file that contains the operation path"
            )
    assert not problems, "OpenAPI fixture is still generator output (G1): " + "; ".join(
        problems
    )

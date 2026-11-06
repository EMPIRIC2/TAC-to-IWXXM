"""OpenAPI operations have interaction rows and Pact consumer documents.

``scripts/ci/check_openapi_contract.py`` plus
``tests/contracts/openapi-interactions.json`` is the #1432 status and
required-field gate. ``tests/contracts/pacts/`` holds Pact consumer documents
(``pactSpecification``, consumer, provider, interactions). An operation is
uncovered when no Pact interaction names its method, path, and a status that
both the OpenAPI operation and the interaction rows declare.

[Corpus: tests] [Corpus: api]
"""

from __future__ import annotations

import json
from typing import Any

import pytest
from tests.scripts.conftest import REPO_ROOT, load_script

SPEC = REPO_ROOT / "apps" / "frontend" / "openapi" / "openapi.json"
INTERACTIONS = REPO_ROOT / "tests" / "contracts" / "openapi-interactions.json"
PACTS = REPO_ROOT / "tests" / "contracts" / "pacts"
HTTP_METHODS = frozenset(
    {"get", "post", "put", "patch", "delete", "head", "options", "trace"}
)


@pytest.mark.unit
def test_openapi_interactions_cover_every_operation() -> None:
    """Each OpenAPI operation has at least one interaction row."""
    checker = load_script(
        "ci/check_openapi_contract.py",
        "check_openapi_contract_for_operations",
    )
    report = checker.run_check(SPEC, INTERACTIONS)
    missing = report["missing"]["operations"]
    assert not missing, (
        f"{report['operations_missing']} operations have no interaction row"
    )


def _declared_statuses(operation: dict[str, Any]) -> set[str]:
    responses = operation.get("responses", {})
    if not isinstance(responses, dict):
        return set()
    return {str(code) for code in responses if str(code).isdigit()}


def _openapi_operations(spec: dict[str, Any]) -> list[tuple[str, str, set[str]]]:
    paths = spec.get("paths", {})
    if not isinstance(paths, dict):
        return []
    operations: list[tuple[str, str, set[str]]] = []
    for path, path_item in paths.items():
        if not isinstance(path_item, dict):
            continue
        for method, operation in path_item.items():
            if method.lower() not in HTTP_METHODS or not isinstance(operation, dict):
                continue
            operations.append(
                (method.upper(), str(path), _declared_statuses(operation))
            )
    return operations


def _interaction_statuses() -> dict[tuple[str, str], set[str]]:
    document = json.loads(INTERACTIONS.read_text(encoding="utf-8"))
    rows = document.get("interactions", [])
    allowed: dict[tuple[str, str], set[str]] = {}
    if not isinstance(rows, list):
        return allowed
    for row in rows:
        if not isinstance(row, dict):
            continue
        method = str(row.get("method", "")).upper()
        path = str(row.get("path", ""))
        allowed.setdefault((method, path), set()).add(str(row.get("status", "")))
    return allowed


def _pact_statuses() -> dict[tuple[str, str], set[str]]:
    covered: dict[tuple[str, str], set[str]] = {}
    for pact_path in sorted(PACTS.glob("*.json")):
        document = json.loads(pact_path.read_text(encoding="utf-8"))
        if not isinstance(document, dict):
            continue
        consumer = document.get("consumer", {})
        provider = document.get("provider", {})
        metadata = document.get("metadata", {})
        if not isinstance(consumer, dict) or not consumer.get("name"):
            msg = f"{pact_path.name} has no consumer name"
            raise AssertionError(msg)
        if not isinstance(provider, dict) or not provider.get("name"):
            msg = f"{pact_path.name} has no provider name"
            raise AssertionError(msg)
        if not isinstance(metadata, dict):
            msg = f"{pact_path.name} has no metadata"
            raise AssertionError(msg)
        pact_specification = metadata.get("pactSpecification", {})
        if not isinstance(pact_specification, dict) or not pact_specification.get(
            "version"
        ):
            msg = f"{pact_path.name} has no pactSpecification version"
            raise AssertionError(msg)
        interactions = document.get("interactions", [])
        if not isinstance(interactions, list):
            continue
        for interaction in interactions:
            if not isinstance(interaction, dict):
                continue
            request = interaction.get("request", {})
            response = interaction.get("response", {})
            if not isinstance(request, dict) or not isinstance(response, dict):
                continue
            method = str(request.get("method", "")).upper()
            path = str(request.get("path", ""))
            covered.setdefault((method, path), set()).add(
                str(response.get("status", ""))
            )
    return covered


@pytest.mark.unit
def test_pact_documents_cover_every_openapi_operation() -> None:
    """Each OpenAPI operation has a Pact interaction with a declared status."""
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    operations = _openapi_operations(spec)
    allowed = _interaction_statuses()
    covered = _pact_statuses()
    missing: list[str] = []
    for method, path, declared in operations:
        seen = covered.get((method, path), set())
        if not seen & declared & allowed.get((method, path), set()):
            missing.append(f"{method} {path}")
    assert not missing, f"{len(missing)} operations have no Pact interaction: {missing}"

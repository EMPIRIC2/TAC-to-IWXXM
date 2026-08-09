"""TC-EV048-002/005 — OpenAPI free of internal planning vocabulary (EV-048 / #951).

T1.1: red clean-scan until M2 strip; synthetic inject always green.
[Corpus: tests] [Corpus: api] [Corpus: product §F21]
"""

from __future__ import annotations

import copy
import re
from collections.abc import Iterable, Iterator
from typing import Any

import pytest

from src import api as api_module

# Locked patterns (D-S057-guard-s0=1, D-S057-04-guard-ext=1).
# `#NNN` uses (?<!\\w) because ``\\b#`` does not match after spaces/slashes (e.g. ``#702``).
INTERNAL_DOC_REF_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("Corpus", re.compile(r"\[Corpus:")),
    ("docs/sessions", re.compile(r"docs/sessions/")),
    ("docs/feature-list", re.compile(r"docs/feature-list")),
    ("ADR", re.compile(r"\bADR-\d+\b")),
    ("EV", re.compile(r"\bEV-\d+\b")),
    ("S0", re.compile(r"\bS0\d+\b")),
    ("TC", re.compile(r"\bTC-[A-Z0-9-]+\b")),
    ("E##", re.compile(r"\bE\d{2}-\d+\b")),
    ("#NNN", re.compile(r"(?<!\w)#\d{3,}\b")),
    # Product feature ids (D-S057-qa003=2).
    ("Fn", re.compile(r"\bF\d+\b")),
)

ALLOWLIST: frozenset[str] = frozenset()


def find_internal_doc_refs(text: str) -> list[tuple[str, str]]:
    """Return ``(pattern_name, match)`` pairs for planning vocabulary in ``text``."""
    hits: list[tuple[str, str]] = []
    for name, pattern in INTERNAL_DOC_REF_PATTERNS:
        for match in pattern.finditer(text):
            token = match.group(0)
            if token in ALLOWLIST:
                continue
            hits.append((name, token))
    return hits


def walk_string_values(obj: Any, path: str = "$") -> Iterator[tuple[str, str]]:
    """Yield ``(json_path, value)`` for every string in a JSON-like structure."""
    if isinstance(obj, dict):
        for key, value in obj.items():
            yield from walk_string_values(value, f"{path}.{key}")
    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            yield from walk_string_values(value, f"{path}[{index}]")
    elif isinstance(obj, str):
        yield path, obj


def collect_openapi_ref_hits(schema: dict[str, Any]) -> list[tuple[str, str, str]]:
    """Scan an OpenAPI document for internal doc refs."""
    found: list[tuple[str, str, str]] = []
    for path, value in walk_string_values(schema):
        for name, token in find_internal_doc_refs(value):
            found.append((path, name, token))
    return found


def format_hits(hits: Iterable[tuple[str, str, str]]) -> str:
    """Format OpenAPI hits for assertion messages."""
    lines = [f"  {path}: {name}={token!r}" for path, name, token in hits]
    return "\n".join(lines) if lines else "(none)"


def test_tc_ev048_005_synthetic_inject_detected() -> None:
    """Guard must fail when a synthetic planning cite is injected into a string."""
    poisoned = "Soft-preview mode (ADR-022): best-effort; see #702 and TC-F7-002 / E11-31 / EV-040 / S011 / F31"
    hits = find_internal_doc_refs(poisoned)
    names = {name for name, _ in hits}
    assert "ADR" in names
    assert "#NNN" in names
    assert "TC" in names
    assert "E##" in names
    assert "EV" in names
    assert "S0" in names
    assert "Fn" in names


def test_tc_ev048_005_clean_operator_copy_passes() -> None:
    """Operator-friendly replacements must not trip the guard."""
    clean = (
        "Soft-preview: best-effort IWXXM with failure spans on partial convert. "
        "Public (no login required). Deterministic plain-language paragraph of the report."
    )
    assert find_internal_doc_refs(clean) == []


def test_tc_ev048_002_openapi_export_has_no_internal_doc_refs() -> None:
    """TC-EV048-002: walk all OpenAPI string values; fail on planning vocabulary."""
    schema = api_module.app.openapi()
    hits = collect_openapi_ref_hits(schema)
    assert hits == [], f"OpenAPI still contains internal planning vocabulary ({len(hits)} hits):\n{format_hits(hits)}"


def test_tc_ev048_005_injected_openapi_description_detected() -> None:
    """Regression: mutating a description in a copied schema is detected."""
    schema = copy.deepcopy(api_module.app.openapi())
    paths = schema.get("paths") or {}
    injected = False
    for path_item in paths.values():
        if not isinstance(path_item, dict):
            continue
        for method_body in path_item.values():
            if isinstance(method_body, dict) and "description" in method_body:
                method_body["description"] = f"{method_body.get('description', '')} [Corpus: product] ADR-999"
                injected = True
                break
        if injected:
            break
    if not injected:
        schema.setdefault("info", {})["description"] = "leak ADR-999 [Corpus: tests]"

    hits = collect_openapi_ref_hits(schema)
    names = {name for _, name, _ in hits}
    assert "ADR" in names or "Corpus" in names

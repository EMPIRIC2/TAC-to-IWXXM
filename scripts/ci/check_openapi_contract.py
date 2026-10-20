#!/usr/bin/env python3
"""Check OpenAPI statuses and required fields against local contract fixtures.

Compares ``apps/frontend/openapi/openapi.json`` with
``scripts/ci/fixtures/openapi_contract_interactions.json``. This is an in-repo
status and required-field suite (no PactFlow, no broker). An operation, in-scope
status, required JSON request field, or required JSON response field that is
absent from the fixtures fails the process.

In-scope statuses are HTTP 2xx and 4xx except 500, 501, 502, and 503, matching
the 2026-10-18 contract scan. Request and response fields are the top-level
``required`` names on ``application/json`` schemas (``$ref`` resolved locally).

Acceptance command::

    uv run python scripts/ci/check_openapi_contract.py

Refresh the committed fixtures only after an intentional API contract change::

    uv run python scripts/ci/check_openapi_contract.py --write-fixtures
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import TypedDict, cast

ROOT = Path(__file__).resolve().parents[2]
SPEC_PATH = ROOT / "apps" / "frontend" / "openapi" / "openapi.json"
FIXTURE_PATH = (
    ROOT / "scripts" / "ci" / "fixtures" / "openapi_contract_interactions.json"
)

HTTP_METHODS = frozenset(
    {"get", "post", "put", "patch", "delete", "head", "options", "trace"}
)
EXCLUDED_STATUSES = frozenset({"500", "501", "502", "503"})
STATUS_IN_SCOPE = re.compile(r"^[24]\d\d$")
CONVERT_RESPONSE_FIELDS = frozenset({"failed", "successful", "total_processed"})

JsonObject = dict[str, object]


class OperationContract(TypedDict):
    """One OpenAPI operation's in-scope statuses and required JSON fields."""

    method: str
    path: str
    statuses: set[str]
    request_fields: set[str]
    response_fields: dict[str, set[str]]


class Interaction(TypedDict):
    """One local contract interaction covering a method, path, and status."""

    method: str
    path: str
    status: str
    request_fields: list[str]
    response_fields: list[str]


def _pointer(document: JsonObject, ref: str) -> object:
    """
    Resolve a local JSON pointer such as ``#/components/schemas/Name``.

    Parameters
    ----------
    document :
        Parsed OpenAPI document.
    ref :
        Pointer beginning with ``#/``.

    Returns
    -------
    object
        The referenced node.

    Raises
    ------
    KeyError
        If a pointer segment is missing.
    """
    current: object = document
    for raw_part in ref[2:].split("/"):
        part = raw_part.replace("~1", "/").replace("~0", "~")
        if not isinstance(current, dict) or part not in current:
            message = f"unresolved $ref {ref}"
            raise KeyError(message)
        current = current[part]
    return current


def _resolve(node: object, document: JsonObject, stack: frozenset[str]) -> object:
    """
    Replace local ``$ref`` nodes, stopping on cycles.

    Parameters
    ----------
    node :
        Schema or schema fragment.
    document :
        Parsed OpenAPI document.
    stack :
        ``$ref`` pointers already being resolved.

    Returns
    -------
    object
        Ref-resolved node.
    """
    if isinstance(node, list):
        return [_resolve(item, document, stack) for item in node]
    if not isinstance(node, dict):
        return node
    mapping = cast(JsonObject, node)
    ref = mapping.get("$ref")
    if isinstance(ref, str) and ref.startswith("#/"):
        if ref in stack:
            return {}
        target = _resolve(_pointer(document, ref), document, stack | {ref})
        extras = {
            key: _resolve(value, document, stack)
            for key, value in mapping.items()
            if key != "$ref"
        }
        if isinstance(target, dict) and extras:
            merged = dict(target)
            merged.update(extras)
            return merged
        return target
    return {key: _resolve(value, document, stack) for key, value in mapping.items()}


def _json_schema(content: object) -> JsonObject:
    """
    Return the JSON media-type schema from an OpenAPI ``content`` block.

    Parameters
    ----------
    content :
        OpenAPI content map, or anything else.

    Returns
    -------
    dict
        Schema object, or an empty mapping when the body is not JSON.
    """
    if not isinstance(content, dict):
        return {}
    entry: object | None = content.get("application/json")
    if entry is None:
        for key, value in content.items():
            if isinstance(key, str) and "json" in key:
                entry = value
                break
    if not isinstance(entry, dict):
        return {}
    schema = entry.get("schema", {})
    if not isinstance(schema, dict):
        return {}
    return cast(JsonObject, schema)


def _required_fields(schema: object) -> set[str]:
    """
    Collect top-level required property names, including composition keywords.

    Parameters
    ----------
    schema :
        Resolved schema node.

    Returns
    -------
    set of str
        Required field names.
    """
    if not isinstance(schema, dict):
        return set()
    fields: set[str] = set()
    for keyword in ("allOf", "anyOf", "oneOf"):
        branches = schema.get(keyword, [])
        if isinstance(branches, list):
            for branch in branches:
                fields |= _required_fields(branch)
    required = schema.get("required", [])
    if isinstance(required, list):
        fields.update(str(field) for field in required)
    return fields


def _load_json(path: Path) -> JsonObject:
    """
    Load a JSON object from ``path``.

    Parameters
    ----------
    path :
        File to read.

    Returns
    -------
    dict
        Parsed object.

    Raises
    ------
    ValueError
        If the file is not a JSON object.
    """
    loaded: object = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        message = f"{path} is not a JSON object"
        raise ValueError(message)
    return cast(JsonObject, loaded)


def extract_operations(document: JsonObject) -> dict[str, OperationContract]:
    """
    Walk OpenAPI paths and collect in-scope statuses and required JSON fields.

    Parameters
    ----------
    document :
        Parsed OpenAPI document.

    Returns
    -------
    dict
        Operations keyed by ``method:path`` with the method uppercased.
    """
    paths = document.get("paths")
    if not isinstance(paths, dict):
        return {}
    operations: dict[str, OperationContract] = {}
    for path, path_item in paths.items():
        if not isinstance(path, str) or not isinstance(path_item, dict):
            continue
        for method, operation in path_item.items():
            if method not in HTTP_METHODS or not isinstance(operation, dict):
                continue
            responses = operation.get("responses")
            if not isinstance(responses, dict):
                responses = {}
            statuses = {
                str(code)
                for code in responses
                if str(code) not in EXCLUDED_STATUSES
                and STATUS_IN_SCOPE.match(str(code))
            }
            request_body = operation.get("requestBody")
            request_fields: set[str] = set()
            if isinstance(request_body, dict):
                request_fields = _required_fields(
                    _json_schema(request_body.get("content"))
                )
            response_fields: dict[str, set[str]] = {}
            for code in statuses:
                response_obj = responses.get(code, {})
                content = (
                    response_obj.get("content")
                    if isinstance(response_obj, dict)
                    else {}
                )
                response_fields[code] = _required_fields(_json_schema(content))
            key = f"{method.upper()}:{path}"
            operations[key] = OperationContract(
                method=method.upper(),
                path=path,
                statuses=statuses,
                request_fields=request_fields,
                response_fields=response_fields,
            )
    return operations


def interactions_from_operations(
    operations: dict[str, OperationContract],
) -> list[Interaction]:
    """
    Build one interaction per in-scope status from the current OpenAPI document.

    Parameters
    ----------
    operations :
        Output of :func:`extract_operations`.

    Returns
    -------
    list
        Interactions whose fields match the document's required JSON fields.
    """
    interactions: list[Interaction] = []
    for info in operations.values():
        request_fields = sorted(info["request_fields"])
        if not info["statuses"]:
            interactions.append(
                Interaction(
                    method=info["method"],
                    path=info["path"],
                    status="200",
                    request_fields=request_fields,
                    response_fields=[],
                )
            )
            continue
        interactions.extend(
            Interaction(
                method=info["method"],
                path=info["path"],
                status=status,
                request_fields=request_fields,
                response_fields=sorted(info["response_fields"].get(status, set())),
            )
            for status in sorted(info["statuses"])
        )
    return interactions


def _as_interactions(payload: JsonObject) -> list[Interaction]:
    """
    Parse fixture interactions.

    Parameters
    ----------
    payload :
        Fixture document.

    Returns
    -------
    list
        Normalized interactions.

    Raises
    ------
    ValueError
        If the fixture shape is wrong.
    """
    raw = payload.get("interactions")
    if not isinstance(raw, list):
        message = "fixture missing interactions array"
        raise ValueError(message)
    interactions: list[Interaction] = []
    for item in raw:
        if not isinstance(item, dict):
            message = "interaction is not an object"
            raise ValueError(message)
        method = item.get("method")
        path = item.get("path")
        status = item.get("status")
        request_fields = item.get("request_fields", [])
        response_fields = item.get("response_fields", [])
        if not isinstance(method, str) or not isinstance(path, str):
            message = "interaction method and path must be strings"
            raise ValueError(message)
        if not isinstance(request_fields, list) or not isinstance(
            response_fields, list
        ):
            message = "interaction fields must be arrays"
            raise ValueError(message)
        interactions.append(
            Interaction(
                method=method.upper(),
                path=path,
                status=str(status),
                request_fields=[str(field) for field in request_fields],
                response_fields=[str(field) for field in response_fields],
            )
        )
    return interactions


def _coverage_gaps(
    operations: dict[str, OperationContract],
    interactions: list[Interaction],
) -> list[str]:
    """
    List uncovered operations, statuses, and required fields.

    Parameters
    ----------
    operations :
        Contracts extracted from OpenAPI.
    interactions :
        Fixture interactions.

    Returns
    -------
    list of str
        Human-readable gaps. Empty when the fixtures cover the document.
    """
    by_operation: dict[str, list[Interaction]] = {}
    for interaction in interactions:
        key = f"{interaction['method']}:{interaction['path']}"
        by_operation.setdefault(key, []).append(interaction)

    gaps: list[str] = []
    for key, info in sorted(operations.items()):
        matched = by_operation.get(key, [])
        if not matched:
            gaps.append(f"operation missing: {key}")
            continue
        covered_statuses = {item["status"] for item in matched}
        gaps.extend(
            f"status missing: {key} {status}"
            for status in sorted(info["statuses"] - covered_statuses)
        )
        covered_request: set[str] = set()
        for item in matched:
            covered_request.update(item["request_fields"])
        gaps.extend(
            f"required request field missing: {key} {field}"
            for field in sorted(info["request_fields"] - covered_request)
        )
        for status, fields in sorted(info["response_fields"].items()):
            covered_response: set[str] = set()
            for item in matched:
                if item["status"] == status:
                    covered_response.update(item["response_fields"])
            gaps.extend(
                f"required response field missing: {key} {status} {field}"
                for field in sorted(fields - covered_response)
            )
    convert_key = "POST:/api/v1/convert"
    convert_covered: set[str] = set()
    for item in by_operation.get(convert_key, []):
        if item["status"] == "200":
            convert_covered.update(item["response_fields"])
    gaps.extend(
        f"required response field missing: {convert_key} 200 {field}"
        for field in sorted(CONVERT_RESPONSE_FIELDS - convert_covered)
    )
    return gaps


def _write_fixtures(operations: dict[str, OperationContract]) -> None:
    """
    Write the baseline fixture file from ``operations``.

    Parameters
    ----------
    operations :
        Contracts extracted from the current OpenAPI document.
    """
    payload = {
        "kind": "openapi-status-and-required-field-contract",
        "source": "apps/frontend/openapi/openapi.json",
        "interactions": interactions_from_operations(operations),
    }
    FIXTURE_PATH.parent.mkdir(parents=True, exist_ok=True)
    FIXTURE_PATH.write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
    )


def _count_gaps(gaps: list[str]) -> dict[str, int]:
    """
    Summarize gap lines into the four acceptance counts.

    Parameters
    ----------
    gaps :
        Lines from :func:`_coverage_gaps`.

    Returns
    -------
    dict
        Counts for operations, statuses, request fields, and response fields.
    """
    counts = {
        "operations missing": 0,
        "status codes missing": 0,
        "required request fields missing": 0,
        "required response fields missing": 0,
    }
    for gap in gaps:
        if gap.startswith("operation missing"):
            counts["operations missing"] += 1
        elif gap.startswith("status missing"):
            counts["status codes missing"] += 1
        elif gap.startswith("required request field"):
            counts["required request fields missing"] += 1
        elif gap.startswith("required response field"):
            counts["required response fields missing"] += 1
    return counts


def main(argv: list[str] | None = None) -> int:
    """
    Run the contract check, or rewrite fixtures when asked.

    Parameters
    ----------
    argv :
        CLI arguments, excluding the program name.

    Returns
    -------
    int
        ``0`` when every in-scope status and required field is covered.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write-fixtures",
        action="store_true",
        help="rewrite the committed interaction fixtures from the OpenAPI document",
    )
    args = parser.parse_args(argv)
    if not SPEC_PATH.is_file():
        print(f"missing OpenAPI document: {SPEC_PATH}", file=sys.stderr)
        return 2
    raw_document = _load_json(SPEC_PATH)
    operations = extract_operations(_resolve_operations(raw_document))
    if args.write_fixtures:
        _write_fixtures(operations)
        print(f"wrote {FIXTURE_PATH.relative_to(ROOT)}")
    if not FIXTURE_PATH.is_file():
        print(
            f"missing contract fixtures: {FIXTURE_PATH.relative_to(ROOT)}",
            file=sys.stderr,
        )
        return 2
    try:
        interactions = _as_interactions(_load_json(FIXTURE_PATH))
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    gaps = _coverage_gaps(operations, interactions)
    counts = _count_gaps(gaps)
    for label, count in counts.items():
        print(f"{label}: {count}")
    if gaps:
        preview = gaps[:30]
        print("\n".join(preview), file=sys.stderr)
        if len(gaps) > len(preview):
            print(f"... {len(gaps) - len(preview)} more", file=sys.stderr)
        return 1
    return 0


def _resolve_operations(document: JsonObject) -> JsonObject:
    """
    Return a copy of ``document`` whose path schemas have local refs resolved.

    Parameters
    ----------
    document :
        Unresolved OpenAPI document. Pointers resolve against this object.

    Returns
    -------
    dict
        Document with ``paths`` schemas resolved. Components are left in place
        so pointers remain valid during resolution.
    """
    resolved_paths = _resolve(document.get("paths"), document, frozenset())
    copied = dict(document)
    if isinstance(resolved_paths, dict):
        copied["paths"] = resolved_paths
    return copied


if __name__ == "__main__":
    raise SystemExit(main())

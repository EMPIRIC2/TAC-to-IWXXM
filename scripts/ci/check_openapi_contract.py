#!/usr/bin/env python3
"""Local consumer-contract check for OpenAPI status codes and required fields.

Compares committed interactions with ``apps/frontend/openapi/openapi.json``.
The measured surface matches the 2026-10-18 scan of that document: every HTTP
operation, every 2xx and 4xx status, and every required field on a JSON
request or response body. An empty interaction file reports the same missing
counts as that scan. The check fails when the document adds a promise that no
interaction covers.

This is an in-repo status and required-field suite. It does not call PactFlow
or read Pact consumer JSON.

[Corpus: tests] [Corpus: api] [Corpus: product]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

HTTP_METHODS = frozenset(
    {"get", "post", "put", "patch", "delete", "head", "options", "trace"}
)
DEFAULT_EXCLUDE_CODES = frozenset({"500", "501", "502", "503"})
_STATUS_RE = re.compile(r"[24]\d\d")
ROOT = Path(__file__).resolve().parents[2]


def _resolve_node(
    node: object, root: dict[str, object], seen: frozenset[str]
) -> object:
    """
    Return ``node`` with internal ``$ref`` pointers replaced.

    Parameters
    ----------
    node :
        Current JSON value.
    root :
        Document used to look up pointers.
    seen :
        Pointers already entered, used to reject cycles.

    Returns
    -------
    Any
        Resolved value.

    Raises
    ------
    ValueError
        The pointer is external, circular, unresolvable, or not a string.
    """
    if isinstance(node, dict):
        ref = node.get("$ref")
        if isinstance(ref, str):
            return _resolve_ref(root, ref, seen)
        if "$ref" in node:
            raise ValueError("$ref must be a string")
        return {key: _resolve_node(value, root, seen) for key, value in node.items()}
    if isinstance(node, list):
        return [_resolve_node(item, root, seen) for item in node]
    return node


def _resolve_ref(root: dict[str, object], ref: str, seen: frozenset[str]) -> object:
    """
    Resolve one internal JSON pointer.

    Parameters
    ----------
    root :
        Document used to look up pointers.
    ref :
        Pointer such as ``#/components/schemas/Name``.
    seen :
        Pointers already entered.

    Returns
    -------
    Any
        Resolved target.

    Raises
    ------
    ValueError
        The pointer is external, circular, or unresolvable.
    """
    if not ref.startswith("#/"):
        raise ValueError(f"Only internal JSON pointers are supported ({ref})")
    if ref in seen:
        raise ValueError(f"Circular $ref: {ref}")
    current: object = root
    for raw in ref[2:].split("/"):
        part = raw.replace("~1", "/").replace("~0", "~")
        if isinstance(current, dict) and part in current:
            current = current[part]
            continue
        if isinstance(current, list) and part.isdigit() and int(part) < len(current):
            current = current[int(part)]
            continue
        raise ValueError(f"Unresolved $ref: {ref}")
    return _resolve_node(current, root, seen | {ref})


def extract_required_fields(schema: object) -> set[str]:
    """
    Collect top-level required property names.

    ``allOf``, ``anyOf``, and ``oneOf`` contribute the union of their required
    names. Nested properties are not expanded.

    Parameters
    ----------
    schema :
        Resolved JSON Schema object, or a non-object branch.

    Returns
    -------
    set of str
        Required names. Empty when ``schema`` is not an object.

    Raises
    ------
    ValueError
        A combinator or ``required`` value is not a list.
    """
    if not isinstance(schema, dict):
        return set()
    fields: set[str] = set()
    for key in ("allOf", "anyOf", "oneOf"):
        if key not in schema:
            continue
        branches = schema[key]
        if not isinstance(branches, list):
            raise ValueError(f"{key} must be a list")
        for branch in branches:
            fields |= extract_required_fields(branch)
    if "required" in schema:
        required = schema["required"]
        if not isinstance(required, list):
            raise ValueError("required must be a list")
        fields.update(str(field) for field in required)
    return fields


def json_media_schema(content: object) -> dict[str, object]:
    """
    Return the JSON media-type schema from an OpenAPI ``content`` map.

    Parameters
    ----------
    content :
        OpenAPI content object. Non-objects yield an empty schema.

    Returns
    -------
    dict
        Schema object, or ``{}`` when no JSON media type is present.
    """
    if not isinstance(content, dict):
        return {}
    entry = content.get("application/json")
    if entry is None:
        for key, value in content.items():
            if "json" in key:
                entry = value
                break
    if not isinstance(entry, dict):
        return {}
    schema = entry.get("schema", {})
    if not isinstance(schema, dict):
        return {}
    return schema


def extract_operations(
    spec: dict[str, object],
    exclude_codes: frozenset[str] | set[str],
) -> dict[str, dict[str, object]]:
    """
    Walk ``paths`` and collect the measured contract surface.

    Parameters
    ----------
    spec :
        OpenAPI document. Internal ``$ref`` pointers are resolved first.
    exclude_codes :
        Status codes omitted even when they are 2xx or 4xx.

    Returns
    -------
    dict
        Operations keyed by ``method:path``.

    Raises
    ------
    ValueError
        The document, ``paths``, or ``responses`` is not an object.
    """
    if not isinstance(spec, dict):
        raise ValueError("OpenAPI document must be an object")
    resolved = _resolve_node(spec, spec, frozenset())
    if not isinstance(resolved, dict):
        raise ValueError("OpenAPI document must be an object")
    paths = resolved.get("paths", {})
    if not isinstance(paths, dict):
        raise ValueError("paths must be an object")
    operations: dict[str, dict[str, object]] = {}
    for path, path_item in paths.items():
        if not isinstance(path_item, dict):
            continue
        for method, operation in path_item.items():
            if method not in HTTP_METHODS:
                continue
            if not isinstance(operation, dict):
                raise ValueError(f"{method.upper()} {path} is not an object")
            responses = operation.get("responses", {})
            if not isinstance(responses, dict):
                raise ValueError(f"{method.upper()} {path} responses must be an object")
            status_codes: set[str] = set()
            for code in responses:
                code_str = str(code)
                if code_str in exclude_codes:
                    continue
                if _STATUS_RE.fullmatch(code_str) is None:
                    continue
                status_codes.add(code_str)
            request_body = operation.get("requestBody", {})
            if request_body is None:
                request_fields: set[str] = set()
            elif isinstance(request_body, dict):
                request_fields = extract_required_fields(
                    json_media_schema(request_body.get("content", {}))
                )
            else:
                raise ValueError(
                    f"{method.upper()} {path} requestBody must be an object"
                )
            response_fields: dict[str, set[str]] = {}
            for code in status_codes:
                response_obj = responses.get(code, {})
                if not isinstance(response_obj, dict):
                    response_fields[code] = set()
                    continue
                response_fields[code] = extract_required_fields(
                    json_media_schema(response_obj.get("content", {}))
                )
            operations[f"{method}:{path}"] = {
                "method": method,
                "path": path,
                "status_codes": status_codes,
                "req_required_fields": request_fields,
                "resp_required_fields": response_fields,
            }
    return operations


def oas_path_to_pattern(oas_path: str) -> re.Pattern[str]:
    """
    Compile an OpenAPI path template to a full-match regular expression.

    Parameters
    ----------
    oas_path :
        Template such as ``/items/{id}``.

    Returns
    -------
    re.Pattern
        Pattern anchored at both ends. Parameters match one path segment.
    """
    parts = re.split(r"(\{[^}]+\})", oas_path)
    regex = ""
    for part in parts:
        if part.startswith("{") and part.endswith("}"):
            regex += "[^/]+"
        else:
            regex += re.escape(part)
    return re.compile(f"^{regex}$")


def find_matching_operation(
    method: str,
    concrete_path: str,
    operations: dict[str, dict[str, object]],
) -> str | None:
    """
    Find the operation key for a method and path.

    Exact templates win. Otherwise the template with the fewest parameters
    that matches the concrete path wins.

    Parameters
    ----------
    method :
        HTTP method, any case.
    concrete_path :
        Interaction path. May be a template or a concrete URL path.
    operations :
        Map from ``extract_operations``.

    Returns
    -------
    str or None
        Matching key, or None when nothing matches.
    """
    method_key = method.lower()
    exact_key = f"{method_key}:{concrete_path}"
    if exact_key in operations:
        return exact_key
    candidates: list[tuple[int, str]] = []
    prefix = f"{method_key}:"
    for key, info in operations.items():
        if not key.startswith(prefix):
            continue
        oas_path = str(info["path"])
        if oas_path_to_pattern(oas_path).match(concrete_path) is None:
            continue
        candidates.append((oas_path.count("{"), key))
    if not candidates:
        return None
    candidates.sort(key=lambda item: item[0])
    return candidates[0][1]


def _as_field_set(value: object, label: str) -> set[str]:
    """
    Require a list of strings.

    Parameters
    ----------
    value :
        Raw JSON value. ``None`` means the key was omitted.
    label :
        Field name used in the error.

    Returns
    -------
    set of str
        Field names. Empty when ``value`` is None.

    Raises
    ------
    ValueError
        ``value`` is not a list of strings.
    """
    if value is None:
        return set()
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"{label} must be a list of strings")
    return set(value)


def _parse_interaction(item: object, source: Path) -> dict[str, object]:
    """
    Normalize one interaction object.

    Parameters
    ----------
    item :
        One JSON element.
    source :
        File path used in errors.

    Returns
    -------
    dict
        Method, path, status, and field sets.

    Raises
    ------
    ValueError
        The element is missing a method, path, or integer status.
    """
    if not isinstance(item, dict):
        raise ValueError(f"{source} interactions must be objects")
    method = item.get("method")
    path = item.get("path")
    if not isinstance(method, str) or not method.strip():
        raise ValueError(f"{source} interaction is missing method")
    if not isinstance(path, str) or not path.startswith("/"):
        raise ValueError(f"{source} interaction is missing path")
    try:
        status = int(item["status"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"{source} interaction status must be an integer") from exc
    return {
        "method": method.upper(),
        "path": path,
        "status": status,
        "request_fields": _as_field_set(item.get("request_fields"), "request_fields"),
        "response_fields": _as_field_set(
            item.get("response_fields"), "response_fields"
        ),
    }


def _load_interaction_document(path: Path) -> list[dict[str, object]]:
    """
    Load interactions from one JSON file.

    Parameters
    ----------
    path :
        JSON file. The root may be an object with ``interactions`` or a list.

    Returns
    -------
    list of dict
        Normalized interactions.

    Raises
    ------
    ValueError
        The JSON root is not a document this check understands.
    """
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        items = data
    elif isinstance(data, dict) and isinstance(data.get("interactions"), list):
        items = data["interactions"]
    else:
        raise ValueError(f"{path} must be an interactions object or a list")
    return [_parse_interaction(item, path) for item in items]


def load_interactions(path: Path) -> list[dict[str, object]]:
    """
    Load interactions from a JSON file or a directory of JSON files.

    Parameters
    ----------
    path :
        File or directory.

    Returns
    -------
    list of dict
        Normalized interactions.

    Raises
    ------
    FileNotFoundError
        ``path`` does not exist.
    ValueError
        A directory contains no JSON files, or a file is not valid.
    """
    if path.is_file():
        return _load_interaction_document(path)
    if not path.is_dir():
        raise FileNotFoundError(path)
    files = sorted(path.glob("*.json"))
    if not files:
        raise ValueError(f"No interaction JSON files in {path}")
    loaded: list[dict[str, object]] = []
    for file in files:
        loaded.extend(_load_interaction_document(file))
    return loaded


def compute_coverage(
    operations: dict[str, dict[str, object]],
    interactions: list[dict[str, object]],
) -> dict[str, object]:
    """
    Compare operations with interactions.

    Parameters
    ----------
    operations :
        Map from ``extract_operations``.
    interactions :
        Normalized interactions.

    Returns
    -------
    dict
        Missing counts and the missing operation, status, and field rows.
    """
    matched: dict[str, list[dict[str, object]]] = defaultdict(list)
    for interaction in interactions:
        key = find_matching_operation(
            str(interaction["method"]),
            str(interaction["path"]),
            operations,
        )
        if key:
            matched[key].append(interaction)

    missing_operations: list[dict[str, str]] = []
    missing_statuses: list[dict[str, str]] = []
    missing_requests: list[dict[str, str]] = []
    missing_responses: list[dict[str, str]] = []

    for op_key in sorted(operations):
        info = operations[op_key]
        method = str(info["method"]).upper()
        path = str(info["path"])
        group = matched.get(op_key, [])
        if not group:
            missing_operations.append({"method": method, "path": path})
        tested_codes = {str(interaction["status"]) for interaction in group}
        missing_statuses.extend(
            {"method": method, "path": path, "status": code}
            for code in sorted(set(info["status_codes"]) - tested_codes)
        )
        required_request = set(info["req_required_fields"])
        if required_request:
            tested_request: set[str] = set()
            for interaction in group:
                tested_request |= set(interaction["request_fields"])
            missing_requests.extend(
                {"method": method, "path": path, "field": field}
                for field in sorted(required_request - tested_request)
            )
        response_map = info["resp_required_fields"]
        for code in sorted(response_map):
            required_response = set(response_map[code])
            if not required_response:
                continue
            tested_response: set[str] = set()
            for interaction in group:
                if str(interaction["status"]) == code:
                    tested_response |= set(interaction["response_fields"])
            missing_responses.extend(
                {
                    "method": method,
                    "path": path,
                    "status": code,
                    "field": field,
                }
                for field in sorted(required_response - tested_response)
            )

    return {
        "interactions": len(interactions),
        "operations_missing": len(missing_operations),
        "status_codes_missing": len(missing_statuses),
        "required_request_fields_missing": len(missing_requests),
        "required_response_fields_missing": len(missing_responses),
        "has_gaps": bool(
            missing_operations
            or missing_statuses
            or missing_requests
            or missing_responses
        ),
        "missing": {
            "operations": missing_operations,
            "status_codes": missing_statuses,
            "request_fields": missing_requests,
            "response_fields": missing_responses,
        },
    }


def synthesize_interactions(
    operations: dict[str, dict[str, object]],
) -> list[dict[str, object]]:
    """
    Build interactions that cover ``operations`` exactly.

    The check does not call this. It records the fill for a document so a
    later required field stays uncovered until an interaction names it.

    Parameters
    ----------
    operations :
        Map from ``extract_operations``.

    Returns
    -------
    list of dict
        One interaction per in-scope status. Operations with no in-scope
        status get a single interaction with status ``0``.
    """
    rows: list[dict[str, object]] = []
    for op_key in sorted(operations):
        info = operations[op_key]
        request_fields = sorted(set(info["req_required_fields"]))
        statuses = sorted(set(info["status_codes"]))
        if not statuses:
            rows.append(
                {
                    "method": str(info["method"]).upper(),
                    "path": str(info["path"]),
                    "status": 0,
                    "request_fields": request_fields,
                    "response_fields": [],
                }
            )
            continue
        response_map = info["resp_required_fields"]
        rows.extend(
            {
                "method": str(info["method"]).upper(),
                "path": str(info["path"]),
                "status": int(status),
                "request_fields": request_fields,
                "response_fields": sorted(set(response_map[status])),
            }
            for status in statuses
        )
    return rows


def run_check(
    spec_path: Path,
    interactions_path: Path,
    exclude_codes: frozenset[str] | set[str] | None = None,
) -> dict[str, object]:
    """
    Load both files and return the coverage report.

    Parameters
    ----------
    spec_path :
        OpenAPI JSON file.
    interactions_path :
        Interaction JSON file or directory.
    exclude_codes :
        Status codes to skip. Defaults to 500, 501, 502, and 503.

    Returns
    -------
    dict
        Report from ``compute_coverage``.

    Raises
    ------
    ValueError
        The spec is not a JSON object or a pointer cannot be resolved.
    """
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    if not isinstance(spec, dict):
        raise ValueError("OpenAPI document must be an object")
    excluded = (
        set(DEFAULT_EXCLUDE_CODES) if exclude_codes is None else set(exclude_codes)
    )
    operations = extract_operations(spec, excluded)
    interactions = load_interactions(interactions_path)
    return compute_coverage(operations, interactions)


def format_report(report: dict[str, object]) -> str:
    """
    Format the four missing counts and any gap rows.

    Parameters
    ----------
    report :
        Report from ``compute_coverage``.

    Returns
    -------
    str
        Multiline text ending with a newline.
    """
    lines = [
        f"interactions: {report['interactions']}",
        f"operations missing: {report['operations_missing']}",
        f"status codes missing: {report['status_codes_missing']}",
        f"required request fields missing: {report['required_request_fields_missing']}",
        (
            "required response fields missing: "
            f"{report['required_response_fields_missing']}"
        ),
    ]
    missing = report["missing"]
    lines.extend(
        f"missing operation: {row['method']} {row['path']}"
        for row in missing["operations"]
    )
    lines.extend(
        f"missing status: {row['method']} {row['path']} {row['status']}"
        for row in missing["status_codes"]
    )
    lines.extend(
        f"missing request field: {row['method']} {row['path']} {row['field']}"
        for row in missing["request_fields"]
    )
    lines.extend(
        "missing response field: "
        f"{row['method']} {row['path']} {row['status']} {row['field']}"
        for row in missing["response_fields"]
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    """
    Run the check from the command line.

    Parameters
    ----------
    argv :
        Arguments excluding the program name. ``None`` reads ``sys.argv``.

    Returns
    -------
    int
        ``0`` when nothing is missing, ``1`` when coverage has gaps, ``2``
        when a file cannot be read.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--spec",
        type=Path,
        default=ROOT / "apps" / "frontend" / "openapi" / "openapi.json",
        help="OpenAPI document (default: apps/frontend/openapi/openapi.json)",
    )
    parser.add_argument(
        "--interactions",
        type=Path,
        default=ROOT / "tests" / "contracts" / "openapi-interactions.json",
        help="Interaction file (default: tests/contracts/openapi-interactions.json)",
    )
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--exclude-codes", nargs="*", default=None)
    args = parser.parse_args(argv)
    exclude = (
        None
        if args.exclude_codes is None
        else frozenset(str(code) for code in args.exclude_codes)
    )
    try:
        report = run_check(args.spec, args.interactions, exclude)
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if args.as_json:
        print(json.dumps(report, sort_keys=True))
    else:
        print(format_report(report), end="")
    return 1 if report["has_gaps"] else 0


if __name__ == "__main__":
    raise SystemExit(main())

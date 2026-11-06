"""Consumer-contract check for OpenAPI status codes and required JSON fields."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from tests.scripts.conftest import REPO_ROOT, load_script

SPEC = REPO_ROOT / "apps" / "frontend" / "openapi" / "openapi.json"
INTERACTIONS = REPO_ROOT / "tests" / "contracts" / "openapi-interactions.json"

# 2026-10-18 scan of apps/frontend/openapi/openapi.json with an empty pact:
# 88 operations, 165 status codes, 41 required request fields, 330 response fields.
SCAN_OPERATIONS = 88
SCAN_STATUSES = 165
SCAN_REQUEST_FIELDS = 41
SCAN_RESPONSE_FIELDS = 330


@pytest.fixture
def checker() -> Any:
    return load_script(
        "ci/check_openapi_contract.py", "check_openapi_contract_under_test"
    )


def _dump(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def _mini_spec() -> dict[str, Any]:
    return {
        "paths": {
            "/need": {
                "parameters": [{"name": "q"}],
                "post": {
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["name"],
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "ok",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "required": ["id"],
                                    }
                                }
                            },
                        },
                        "422": {"description": "no"},
                        "500": {"description": "excluded"},
                        "default": {"description": "ignored"},
                    },
                },
            },
            "/items/{id}": {
                "get": {
                    "responses": {
                        "200": {
                            "description": "ok",
                            "content": {
                                "application/vnd.api+json": {
                                    "schema": {
                                        "allOf": [{"required": ["id"]}],
                                        "anyOf": [{"required": ["id"]}],
                                        "oneOf": [{"required": ["kind"]}],
                                        "required": ["name"],
                                    }
                                }
                            },
                        },
                        "204": {"description": "empty"},
                    }
                }
            },
            "/files/{name}": {"get": {"responses": {"200": {"description": "file"}}}},
            "/{kind}/{name}": {
                "get": {"responses": {"200": {"description": "generic"}}}
            },
            "/a.b/{id}": {"get": {"responses": {"200": {"description": "dotted"}}}},
        }
    }


@pytest.mark.unit
def test_committed_contract_covers_the_openapi_document(checker: Any) -> None:
    report = checker.run_check(SPEC, INTERACTIONS)
    assert report["operations_missing"] == 0
    assert report["status_codes_missing"] == 0
    assert report["required_request_fields_missing"] == 0
    assert report["required_response_fields_missing"] == 0
    assert report["has_gaps"] is False
    document = json.loads(INTERACTIONS.read_text(encoding="utf-8"))
    convert = [
        row
        for row in document["interactions"]
        if row["method"] == "POST"
        and row["path"] == "/api/v1/convert"
        and row["status"] == 200
    ]
    assert len(convert) == 1
    assert {"failed", "successful", "total_processed"} <= set(
        convert[0]["response_fields"]
    )


@pytest.mark.unit
def test_main_on_committed_files_exits_zero(
    checker: Any, capsys: pytest.CaptureFixture[str]
) -> None:
    code = checker.main(["--spec", str(SPEC), "--interactions", str(INTERACTIONS)])
    assert code == 0
    captured = capsys.readouterr()
    assert "operations missing: 0" in captured.out
    assert "status codes missing: 0" in captured.out
    assert "required request fields missing: 0" in captured.out
    assert "required response fields missing: 0" in captured.out
    assert captured.err == ""


@pytest.mark.unit
def test_empty_interactions_match_the_scan_counts(checker: Any, tmp_path: Path) -> None:
    empty = tmp_path / "empty.json"
    _dump(empty, {"interactions": []})
    report = checker.run_check(SPEC, empty)
    assert report["interactions"] == 0
    assert report["operations_missing"] == SCAN_OPERATIONS
    assert report["status_codes_missing"] == SCAN_STATUSES
    assert report["required_request_fields_missing"] == SCAN_REQUEST_FIELDS
    assert report["required_response_fields_missing"] == SCAN_RESPONSE_FIELDS
    missing = {
        (row["method"], row["path"], row["status"], row["field"])
        for row in report["missing"]["response_fields"]
    }
    for field in ("failed", "successful", "total_processed"):
        assert ("POST", "/api/v1/convert", "200", field) in missing
    without_exclude = checker.run_check(SPEC, empty, exclude_codes=set())
    assert without_exclude["status_codes_missing"] == SCAN_STATUSES


@pytest.mark.unit
def test_new_required_response_field_without_interaction_fails(
    checker: Any, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    spec["components"]["schemas"]["ConversionResponse"]["required"].append(
        "contractProbe"
    )
    spec_path = tmp_path / "openapi.json"
    _dump(spec_path, spec)
    code = checker.main(
        [
            "--spec",
            str(spec_path),
            "--interactions",
            str(INTERACTIONS),
            "--json",
        ]
    )
    assert code == 1
    report = json.loads(capsys.readouterr().out)
    assert report["operations_missing"] == 0
    assert report["status_codes_missing"] == 0
    assert report["required_request_fields_missing"] == 0
    assert report["required_response_fields_missing"] >= 1
    assert any(
        row["method"] == "POST"
        and row["path"] == "/api/v1/convert"
        and row["status"] == "200"
        and row["field"] == "contractProbe"
        for row in report["missing"]["response_fields"]
    )


@pytest.mark.unit
def test_exclude_codes_drop_matching_statuses(
    checker: Any, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    empty = tmp_path / "empty.json"
    _dump(empty, {"interactions": []})
    code = checker.main(
        [
            "--spec",
            str(SPEC),
            "--interactions",
            str(empty),
            "--json",
            "--exclude-codes",
            "422",
        ]
    )
    assert code == 1
    report = json.loads(capsys.readouterr().out)
    assert report["status_codes_missing"] < SCAN_STATUSES
    assert all(row["status"] != "422" for row in report["missing"]["status_codes"])


@pytest.mark.unit
def test_gap_report_lists_each_missing_promise(
    checker: Any, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    spec_path = tmp_path / "spec.json"
    interactions = tmp_path / "interactions.json"
    _dump(spec_path, _mini_spec())
    _dump(interactions, {"kind": "ignored", "interactions": []})
    code = checker.main(["--spec", str(spec_path), "--interactions", str(interactions)])
    assert code == 1
    text = capsys.readouterr().out
    assert "missing operation: POST /need" in text
    assert "missing status: POST /need 200" in text
    assert "missing request field: POST /need name" in text
    assert "missing response field: POST /need 200 id" in text
    assert "500" not in text
    assert "default" not in text


@pytest.mark.unit
def test_partial_interactions_leave_the_uncovered_promise(
    checker: Any, tmp_path: Path
) -> None:
    spec_path = tmp_path / "spec.json"
    interactions = tmp_path / "interactions.json"
    _dump(spec_path, _mini_spec())
    _dump(
        interactions,
        {
            "interactions": [
                {
                    "method": "POST",
                    "path": "/need",
                    "status": 200,
                    "request_fields": [],
                    "response_fields": [],
                },
                {
                    "method": "GET",
                    "path": "/does-not-exist",
                    "status": 200,
                    "request_fields": ["name"],
                    "response_fields": ["id"],
                },
            ]
        },
    )
    report = checker.run_check(spec_path, interactions)
    assert report["operations_missing"] >= 1
    assert {"method": "POST", "path": "/need"} not in report["missing"]["operations"]
    assert any(row["status"] == "422" for row in report["missing"]["status_codes"])
    assert any(row["field"] == "name" for row in report["missing"]["request_fields"])
    assert any(
        row["field"] == "id" and row["status"] == "200"
        for row in report["missing"]["response_fields"]
    )


@pytest.mark.unit
def test_concrete_paths_and_split_files_can_cover_a_spec(
    checker: Any, tmp_path: Path
) -> None:
    spec_path = tmp_path / "spec.json"
    _dump(spec_path, _mini_spec())
    folder = tmp_path / "pacts"
    folder.mkdir()
    _dump(
        folder / "a.json",
        [
            {
                "method": "post",
                "path": "/need",
                "status": "200",
                "request_fields": ["name"],
                "response_fields": ["id"],
            },
            {
                "method": "POST",
                "path": "/need",
                "status": 422,
            },
        ],
    )
    _dump(
        folder / "b.json",
        {
            "interactions": [
                {
                    "method": "GET",
                    "path": "/items/abc",
                    "status": 200,
                    "request_fields": [],
                    "response_fields": ["id", "kind", "name"],
                },
                {
                    "method": "GET",
                    "path": "/items/abc",
                    "status": 204,
                },
                {
                    "method": "GET",
                    "path": "/files/readme",
                    "status": 200,
                },
                {
                    "method": "GET",
                    "path": "/other/thing",
                    "status": 200,
                },
                {
                    "method": "GET",
                    "path": "/a.b/1",
                    "status": 200,
                },
            ]
        },
    )
    report = checker.run_check(spec_path, folder)
    assert report["has_gaps"] is False
    exact = checker.find_matching_operation(
        "GET",
        "/files/readme",
        checker.extract_operations(json.loads(spec_path.read_text()), set()),
    )
    assert exact == "get:/files/{name}"


@pytest.mark.unit
def test_non_json_request_bodies_are_outside_the_scan_surface(checker: Any) -> None:
    spec = {
        "paths": {
            "/form": {
                "post": {
                    "requestBody": {
                        "content": {
                            "multipart/form-data": {
                                "schema": {"type": "object", "required": ["files"]}
                            },
                            "text/plain": {"schema": []},
                            "application/json": "not-an-object",
                        }
                    },
                    "responses": {"200": {"description": "ok", "content": []}},
                }
            }
        }
    }
    operations = checker.extract_operations(spec, checker.DEFAULT_EXCLUDE_CODES)
    assert operations["post:/form"]["req_required_fields"] == set()
    assert operations["post:/form"]["resp_required_fields"]["200"] == set()
    assert checker.json_media_schema(None) == {}
    assert checker.json_media_schema({"application/json": {"schema": []}}) == {}
    assert checker.json_media_schema(
        {"application/json": {"schema": {"type": "object"}}}
    ) == {"type": "object"}


@pytest.mark.unit
def test_schema_combinators_and_bad_shapes(checker: Any) -> None:
    fields = checker.extract_required_fields(
        {
            "allOf": [{"required": ["a"]}, "skip"],
            "anyOf": [{"required": ["b"]}],
            "oneOf": [{"required": ["c"]}],
            "required": ["d"],
        }
    )
    assert fields == {"a", "b", "c", "d"}
    assert checker.extract_required_fields("nope") == set()
    with pytest.raises(ValueError, match="allOf must be a list"):
        checker.extract_required_fields({"allOf": {}})
    with pytest.raises(ValueError, match="required must be a list"):
        checker.extract_required_fields({"required": "a"})


@pytest.mark.unit
def test_ref_resolution_edges(checker: Any) -> None:
    spec = {
        "components": {
            "schemas": {
                "A": {"$ref": "#/components/schemas/B"},
                "B": {"type": "object", "required": ["id"]},
                "List": [{"type": "object", "required": ["n"]}],
            }
        },
        "paths": {
            "/ref": {
                "get": {
                    "responses": {
                        "200": {
                            "description": "ok",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/A",
                                        "description": "sibling",
                                    }
                                }
                            },
                        }
                    }
                }
            }
        },
    }
    operations = checker.extract_operations(spec, set())
    assert operations["get:/ref"]["resp_required_fields"]["200"] == {"id"}
    listed = checker._resolve_ref(spec, "#/components/schemas/List/0", frozenset())
    assert listed["required"] == ["n"]
    with pytest.raises(ValueError, match="Circular"):
        checker.extract_operations(
            {
                "paths": {},
                "components": {
                    "schemas": {"Loop": {"$ref": "#/components/schemas/Loop"}}
                },
            },
            set(),
        )
    with pytest.raises(ValueError, match="must be a string"):
        checker._resolve_node({"$ref": 1}, spec, frozenset())
    with pytest.raises(ValueError, match="internal JSON pointers"):
        checker._resolve_ref(spec, "https://example.invalid/schema", frozenset())
    with pytest.raises(ValueError, match="Unresolved"):
        checker._resolve_ref(spec, "#/missing", frozenset())
    with pytest.raises(ValueError, match="Unresolved"):
        checker._resolve_ref(spec, "#/components/schemas/List/9", frozenset())
    with pytest.raises(ValueError, match="Unresolved"):
        checker._resolve_ref(spec, "#/components/schemas/List/nope", frozenset())
    with pytest.raises(ValueError, match="Unresolved"):
        checker._resolve_ref(spec, "#/components/schemas/B/type/extra", frozenset())
    tilde = {"a/b": {"required": ["z"]}, "paths": {}}
    assert checker._resolve_ref(tilde, "#/a~1b", frozenset())["required"] == ["z"]
    with pytest.raises(ValueError, match="must be an object"):
        checker.extract_operations({"$ref": "#/name", "name": "scalar"}, set())


@pytest.mark.unit
def test_malformed_operations_and_path_templates(checker: Any) -> None:
    with pytest.raises(ValueError, match="OpenAPI document must be an object"):
        checker.extract_operations([], set())
    with pytest.raises(ValueError, match="paths must be an object"):
        checker.extract_operations({"paths": []}, set())
    with pytest.raises(ValueError, match="not an object"):
        checker.extract_operations({"paths": {"/x": {"get": None}}}, set())
    with pytest.raises(ValueError, match="responses must be an object"):
        checker.extract_operations(
            {"paths": {"/x": {"get": {"responses": []}}}},
            set(),
        )
    with pytest.raises(ValueError, match="requestBody must be an object"):
        checker.extract_operations(
            {
                "paths": {
                    "/x": {
                        "post": {
                            "requestBody": "raw",
                            "responses": {"200": {"description": "ok"}},
                        }
                    }
                }
            },
            set(),
        )
    skipped = checker.extract_operations(
        {
            "paths": {
                "/skip": None,
                "/null-body": {
                    "post": {
                        "requestBody": None,
                        "responses": {
                            "200": None,
                            "301": {"description": "redirect"},
                            "422": {"description": "kept"},
                        },
                    }
                },
            }
        },
        {"422"},
    )
    assert "/skip" not in skipped
    info = skipped["post:/null-body"]
    assert info["status_codes"] == {"200"}
    assert info["req_required_fields"] == set()
    assert info["resp_required_fields"]["200"] == set()
    pattern = checker.oas_path_to_pattern("{foo")
    assert pattern.match("{foo")
    assert checker.find_matching_operation("GET", "/missing", {}) is None


@pytest.mark.unit
def test_synthesize_covers_operations_without_statuses(
    checker: Any, tmp_path: Path
) -> None:
    operations = {
        "get:/ping": {
            "method": "get",
            "path": "/ping",
            "status_codes": set(),
            "req_required_fields": set(),
            "resp_required_fields": {},
        }
    }
    rows = checker.synthesize_interactions(operations)
    assert rows == [
        {
            "method": "GET",
            "path": "/ping",
            "status": 0,
            "request_fields": [],
            "response_fields": [],
        }
    ]
    path = tmp_path / "rows.json"
    _dump(path, rows)
    report = checker.compute_coverage(operations, checker.load_interactions(path))
    assert report["has_gaps"] is False
    covered = checker.synthesize_interactions(
        checker.extract_operations(_mini_spec(), checker.DEFAULT_EXCLUDE_CODES)
    )
    covered_path = tmp_path / "covered.json"
    spec_path = tmp_path / "mini.json"
    _dump(covered_path, covered)
    _dump(spec_path, _mini_spec())
    full = checker.run_check(spec_path, covered_path)
    assert full["has_gaps"] is False
    assert any(row["path"] == "/need" and row["status"] == 200 for row in covered)


@pytest.mark.unit
def test_interaction_documents_must_be_well_formed(
    checker: Any, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    spec_path = tmp_path / "spec.json"
    _dump(spec_path, {"paths": {}})
    broken = tmp_path / "broken.json"
    cases = [
        "{",
        "{}",
        '{"interactions": {}}',
        '{"interactions": [1]}',
        '{"interactions": [{"path": "/x", "status": 200}]}',
        '{"interactions": [{"method": " ", "path": "/x", "status": 200}]}',
        '{"interactions": [{"method": 1, "path": "/x", "status": 200}]}',
        '{"interactions": [{"method": "GET", "path": "x", "status": 200}]}',
        '{"interactions": [{"method": "GET", "path": "/x"}]}',
        '{"interactions": [{"method": "GET", "path": "/x", "status": "nope"}]}',
        (
            '{"interactions": [{"method": "GET", "path": "/x", "status": 200, '
            '"request_fields": "name"}]}'
        ),
        (
            '{"interactions": [{"method": "GET", "path": "/x", "status": 200, '
            '"response_fields": [1]}]}'
        ),
    ]
    for payload in cases:
        broken.write_text(payload, encoding="utf-8")
        assert (
            checker.main(["--spec", str(spec_path), "--interactions", str(broken)]) == 2
        )
    capsys.readouterr()
    missing = tmp_path / "missing.json"
    assert checker.main(["--spec", str(spec_path), "--interactions", str(missing)]) == 2
    empty_dir = tmp_path / "empty-dir"
    empty_dir.mkdir()
    assert (
        checker.main(["--spec", str(spec_path), "--interactions", str(empty_dir)]) == 2
    )
    spec_path.write_text("[1, 2]", encoding="utf-8")
    ok = tmp_path / "ok.json"
    _dump(ok, {"interactions": []})
    assert checker.main(["--spec", str(spec_path), "--interactions", str(ok)]) == 2
    spec_path.write_bytes(b"\xff")
    assert checker.main(["--spec", str(spec_path), "--interactions", str(ok)]) == 2
    assert "ERROR:" in capsys.readouterr().err
